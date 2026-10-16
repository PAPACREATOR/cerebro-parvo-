"use strict";
// Real Chrome + real loopback Python HTTP, with a disposable Store.
// Only the external provider response is mocked in this browser-level gate.
const {chromium}=require("playwright");
const fs=require("node:fs/promises"),path=require("node:path"),assert=require("node:assert/strict");
const os=require("node:os"),net=require("node:net"),{spawn}=require("node:child_process");

(async()=>{
  const reservation=net.createServer();
  await new Promise(ok=>reservation.listen(0,"127.0.0.1",ok));
  const port=reservation.address().port;
  await new Promise(ok=>reservation.close(ok));
  const data=await fs.mkdtemp(path.join(os.tmpdir(),"nexus-folha-e2e-"));
  const backend=spawn(process.env.NEXUS_TEST_PYTHON||"python",
    ["-m","nexus.app","--data",path.join(data,"memory"),"--port",String(port),"--no-browser"],
    {cwd:path.resolve(__dirname,"../.."),stdio:["ignore","pipe","pipe"]});
  const diagnostics=[];backend.stderr.on("data",chunk=>diagnostics.push(String(chunk)));
  backend.on("error",err=>diagnostics.push(err.message));
  let browser;
  try {
    const origin="http://127.0.0.1:"+port;
    let ready=false;
    for(let i=0;i<100;i++) {
      if(backend.exitCode!==null)throw new Error("Host startup failed: "+diagnostics.join(""));
      try {if((await fetch(origin)).ok){ready=true;break;}}catch(_error){}
      await new Promise(ok=>setTimeout(ok,100));
    }
    assert.ok(ready,"Python app did not start: "+diagnostics.join(""));
    browser=await chromium.launch({channel:"chrome",headless:true});
    const page=await browser.newPage({viewport:{width:1280,height:920},locale:"pt-PT"});
    const errors=[],routes=[];page.on("pageerror",error=>errors.push(error.message));
    page.on("request",request=>{
      const route=new URL(request.url()).pathname;
      if(route.startsWith("/api/"))routes.push(route);
    });
    const artifacts=path.resolve("folha-browser-evidence");
    await fs.mkdir(artifacts,{recursive:true});
    const launch=new URL(await fs.readFile(path.join(data,"memory","launch-url.txt"),"utf8"));
    assert.equal(launch.origin,origin);
    await page.goto(launch.href);
    assert.equal(await page.locator("#text").inputValue(),"");
    assert.equal(await page.locator("#workspace").count(),0);
    assert.equal(await page.locator("#product").count(),0);
    assert.equal(await page.locator(".stages").count(),0);
    assert.equal(await page.locator("button:visible").count(),0);
    await page.screenshot({path:path.join(artifacts,"folha-vazia.png"),fullPage:true});

    // Real Nexus parser asks for slots, not a wizard or a second assistant.
    await page.locator("#text").fill("Cria um podcast sobre Guimarães");
    await page.locator("#submit").click();
    await page.waitForFunction(()=>document.getElementById("message").textContent.includes("tom"));
    assert.equal(await page.locator("#workspace").count(),0);
    assert.equal(await page.locator("#execution-confirmation").isVisible(),false);
    await page.locator("#text").fill("informal, 5 minutos");
    await page.locator("#submit").click();
    await page.locator("#execution-confirmation").waitFor({state:"visible"});
    assert.equal(await page.locator("#execution-confirm").isChecked(),false);
    assert.equal(await page.locator("#execution-approve").isDisabled(),true);
    assert.match(await page.locator("#execution-review").textContent(),/5 minutos/);
    await page.locator("#execution-cancel").click();
    await page.waitForFunction(()=>!document.getElementById("execution-confirmation").open);
    assert.equal(routes.includes("/api/confirm-run"),true);
    assert.equal(routes.includes("/api/approve"),false);
    await page.screenshot({path:path.join(artifacts,"folha-pergunta.png"),fullPage:true});

    // Read-only source discovery renders a result in the Folha, no workflow UI.
    const fake="b".repeat(32);
    await page.route("**/api/research",route=>route.fulfill({
      status:202,contentType:"application/json",body:JSON.stringify({run_id:fake}),
    }));
    await page.route("**/api/runs/"+fake,route=>route.fulfill({
      status:200,contentType:"application/json",body:JSON.stringify({
        status:"HUMAN_REQUIRED",process_id:"web",title:"Pesquisa",
        result:{title:"Fontes encontradas"},
        content:"# Fontes\n\nhttps://pt.wikipedia.org/?curid=123\nReferência obtida.",
        message:"Candidato de pesquisa",
      }),
    }));
    await page.locator("#navigation summary").click();
    await page.locator("#new").click();
    await page.locator("#text").fill("Pesquisa fontes sobre Guimarães");
    await page.locator("#submit").click();
    await page.waitForFunction(()=>document.getElementById("content").textContent.includes("pt.wikipedia.org"));
    assert.equal(await page.locator("#workspace").count(),0);
    assert.equal(await page.locator("#result").isVisible(),true);
    assert.equal(await page.locator("#execution-confirmation").isVisible(),false);
    await page.screenshot({path:path.join(artifacts,"folha-fontes.png"),fullPage:true});

    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
    await page.locator("#navigation summary").click();
    await page.locator("#new").click();
    assert.equal(await page.locator("#text").inputValue(),"");
    assert.equal(await page.locator("button:visible").count(),0);
    await page.screenshot({path:path.join(artifacts,"folha-mobile.png"),fullPage:true});
    // Durable two-Folha scratch: save a binary attachment and switch sheets.
    // Chrome uses the REAL loopback Host. No Store run, ticket or Canonical
    // promotion is created by a draft or by reloading the browser.
    const draftBinary=Buffer.from([0,1,2,10,13,255,128,65,0]);
    const draftPath=path.join(data,"draft-ação.bin");
    await fs.writeFile(draftPath,draftBinary);
    await page.locator("#file").setInputFiles(draftPath);
    await page.locator("#text").fill("Primeira Folha persistente");
    await page.locator("#navigation summary").click();
    await page.locator("#new").click();
    assert.equal(await page.locator("#text").inputValue(),"");
    await page.locator("#text").fill("Segunda Folha, texto independente");
    await page.waitForFunction(async()=>{
      const session=sessionStorage.getItem("nexus-session");
      const res=await fetch("/api/folha-draft/b",{headers:{"X-Nexus-Session":session}});
      return res.ok&&(await res.json()).text==="Segunda Folha, texto independente";
    },null,{timeout:15000});
    await page.reload();
    await page.waitForFunction(
      ()=>document.getElementById("text").value==="Segunda Folha, texto independente");
    await page.locator("#navigation summary").click();
    await page.locator("#new").click();
    await page.waitForFunction(
      ()=>document.getElementById("text").value==="Primeira Folha persistente");
    assert.equal(await page.locator("#file").evaluate(el=>el.files[0]?.name),"draft-ação.bin");
    const restoredBytes=await page.locator("#file").evaluate(
      async el=>Array.from(new Uint8Array(await el.files[0].arrayBuffer())));
    assert.deepEqual(restoredBytes,Array.from(draftBinary));
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({result:"PASS",windowsWebSupported:true,whiteSheet:true,
      visibleWorkflowSteps:0,naturalFollowUp:true,webResult:true,humanCanonicalGateIntact:true,
      pageErrors:errors.length}));
  } finally {
    if(browser)await browser.close();
    if(backend.pid&&backend.exitCode===null){
      backend.kill();await new Promise(ok=>backend.once("exit",ok));
    }
    await fs.rm(data,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
