"use strict";
// Native Windows acceptance: one visible Folha -> real Host/LPAC -> Sandy Writer.
// Only the user's two tool confirmations are driven by Playwright test actions.
// No mocked API response, no fake provider, no Canonical promotion.
const {chromium}=require("playwright");
const fs=require("node:fs/promises"),fss=require("node:fs");
const path=require("node:path"),os=require("node:os"),net=require("node:net");
const assert=require("node:assert/strict"),crypto=require("node:crypto");
const {spawn,spawnSync}=require("node:child_process");

(async()=>{
  assert.equal(process.platform,"win32","Real Writer browser gate must use Windows");
  assert.equal(process.env.NEXUS_REAL_WRITER,"1");
  for(const name of ["LIBREOFFICE_EXE","SANDY_EXE"])
    assert.ok(process.env[name]&&fss.existsSync(process.env[name]),name+" is required");

  const repo=path.resolve(__dirname,"../..");
  const root=await fs.mkdtemp(path.join(os.tmpdir(),"nexus-real-writer-browser-"));
  const data=path.join(root,"data");
  const evidence=path.resolve("writer-evidence");
  await fs.mkdir(data,{recursive:true});
  await fs.mkdir(evidence,{recursive:true});
  const input=path.join(root,"fonte.odt");
  const py=process.env.NEXUS_TEST_PYTHON||"python";
  const maker=spawnSync(py,["-c",
    "import sys; from pathlib import Path; from nexus.tests.test_native_writer_route_real import document; Path(sys.argv[1]).write_bytes(document())",
    input],{cwd:repo,encoding:"utf8",timeout:30000});
  assert.equal(maker.status,0,"ODT generation failed: "+(maker.stderr||maker.error||""));
  const raw=await fs.readFile(input);
  const expectedInput=crypto.createHash("sha256").update(raw).digest("hex");
  await fs.writeFile(path.join(data,"libreoffice.json"),JSON.stringify({
    executable:process.env.LIBREOFFICE_EXE,
    sandy:process.env.SANDY_EXE,
  }),"utf8");

  const reservation=net.createServer();
  await new Promise(resolve=>reservation.listen(0,"127.0.0.1",resolve));
  const port=reservation.address().port;
  await new Promise(resolve=>reservation.close(resolve));
  const origin="http://127.0.0.1:"+port;
  const backend=spawn(py,["-m","nexus.app","--data",data,"--port",String(port),"--no-browser"],
    {cwd:repo,stdio:["ignore","pipe","pipe"]});
  const diagnostics=[];
  backend.stderr.on("data",x=>diagnostics.push(String(x)));
  backend.on("error",x=>diagnostics.push(x.message));
  let browser;
  try {
    let ready=false;
    for(let n=0;n<100;n++){
      if(backend.exitCode!==null)throw Error("Host start failure: "+diagnostics.join(""));
      try {if((await fetch(origin)).ok){ready=true;break;}}catch(_){}
      await new Promise(resolve=>setTimeout(resolve,100));
    }
    assert.ok(ready,"Host not ready: "+diagnostics.join(""));
    const launch=new URL(await fs.readFile(path.join(data,"launch-url.txt"),"utf8"));
    assert.equal(launch.origin,origin);
    const session=launch.hash.slice(1).split("session=")[1];
    assert.ok(session&&session.length>20);

    async function api(target){
      const res=await fetch(origin+target,{headers:{"X-Nexus-Session":session}});
      assert.ok(res.ok,target+" HTTP "+res.status);
      return res.json();
    }
    browser=await chromium.launch({channel:"chrome",headless:true});
    const page=await browser.newPage({acceptDownloads:true,locale:"pt-PT"});
    page.setDefaultTimeout(200000);
    const errors=[],requests=[];
    page.on("pageerror",e=>errors.push(e.message));
    page.on("request",req=>{
      if(new URL(req.url()).pathname.startsWith("/api/"))requests.push(new URL(req.url()).pathname);
    });
    await page.goto(launch.href);
    assert.equal(await page.locator("#text").inputValue(),"");
    assert.equal(await page.locator("#workspace").count(),0);
    await page.locator("#file").setInputFiles(input);
    await page.locator("#text").fill("Verifica este documento e converte-o em PDF");
    await page.locator("#submit").click();
    await page.locator("#execution-confirmation").waitFor({state:"visible"});
    assert.match(await page.locator("#execution-summary").textContent(),/Verificar documento/);
    assert.equal(await page.locator("#execution-approve").isDisabled(),true);
    assert.equal(requests.includes("/api/confirm-run"),false);
    await page.locator("#execution-confirm").check();
    await page.locator("#execution-approve").click();

    // The real Windows confined verify must complete BEFORE Writer is proposed.
    await page.waitForFunction(()=>{
      const d=document.getElementById("execution-confirmation");
      return d.open&&document.getElementById("execution-summary").textContent.includes("Converter documento verificado");
    },null,{timeout:200000});
    assert.equal(await page.locator("#execution-approve").isDisabled(),true);
    assert.equal(requests.filter(x=>x==="/api/confirm-run").length,1);
    await page.locator("#execution-confirm").check();
    await page.locator("#execution-approve").click();

    // Real Writer/Sandy outputs a PDF, Host validates it, and a read-only
    // receipt joins both verified Store packets before the Folha reports done.
    await page.waitForFunction(
      ()=>document.getElementById("notice").textContent.includes("cadeia verificada"),
      null,{timeout:200000});
    assert.equal(await page.locator("#pdf").isVisible(),true);
    assert.equal(requests.filter(x=>x==="/api/confirm-run").length,2);
    assert.equal(requests.includes("/api/flow-receipt"),true);
    assert.equal(requests.includes("/api/approve"),false);
    assert.equal(requests.includes("/api/run"),false);

    const history=await api("/api/runs");
    assert.equal(history.length,2);
    const verify=history.find(x=>x.process_id==="verify");
    const writer=history.find(x=>x.process_id==="convert_pdf");
    assert.ok(verify&&writer);
    assert.notEqual(verify.run_id,writer.run_id);
    assert.equal(verify.input_sha256,expectedInput);
    assert.equal(writer.input_sha256,expectedInput);
    assert.equal(verify.status,"HUMAN_REQUIRED");
    assert.equal(writer.status,"HUMAN_REQUIRED");
    assert.match(writer.artifact_sha256,/^[0-9a-f]{64}$/);
    const output=await fetch(origin+"/api/pdf/"+writer.run_id,{
      headers:{"X-Nexus-Session":session},
    });
    assert.equal(output.status,200);
    const pdf=Buffer.from(await output.arrayBuffer());
    assert.equal(pdf.subarray(0,5).toString(),"%PDF-");
    assert.ok(pdf.subarray(-1024).includes(Buffer.from("%%EOF")));
    assert.equal(crypto.createHash("sha256").update(pdf).digest("hex"),writer.artifact_sha256);
    const saved=path.join(evidence,"folha-two-real-tools.pdf");
    await fs.writeFile(saved,pdf);
    await page.screenshot({path:path.join(evidence,"folha-two-real-tools.png"),fullPage:true});
    assert.deepEqual(errors,[]);
    assert.equal(fss.existsSync(path.join(data,"canonical",verify.run_id)),false);
    assert.equal(fss.existsSync(path.join(data,"canonical",writer.run_id)),false);
    console.log(JSON.stringify({result:"PASS",oneFolha:true,twoRealHostRuns:true,
      realSandyWriter:true,pdfSha256:writer.artifact_sha256,requestSha256:expectedInput,
      canonicalPromotion:false,receiptRequested:true,pageErrors:errors.length}));
  } finally {
    if(browser)await browser.close();
    if(backend.pid&&backend.exitCode===null){
      backend.kill();
      await Promise.race([
        new Promise(resolve=>backend.once("exit",resolve)),
        new Promise(resolve=>setTimeout(resolve,5000)),
      ]);
    }
    await fs.rm(root,{recursive:true,force:true,maxRetries:6,retryDelay:200});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
