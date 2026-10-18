"use strict";
// Real Chrome + real loopback Python HTTP, with a disposable Store.
// Research presentation uses mocked research/run responses; parsing and drafts use the real Host.
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
    const initialDraft=page.waitForResponse(response=>
      response.request().method()==="GET" &&
      new URL(response.url()).pathname==="/api/folha-draft/a");
    await page.goto(launch.href);
    assert.equal((await (await initialDraft).json()).text,"");
    assert.equal(await page.locator("#text").inputValue(),"");
    assert.equal(await page.locator("#workspace").count(),0);
    assert.equal(await page.locator("#product").count(),0);
    assert.equal(await page.locator(".stages").count(),0);
    assert.equal(await page.locator("button:visible").count(),0);
    await page.screenshot({path:path.join(artifacts,"folha-vazia.png"),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
    await page.setViewportSize({width:1280,height:920});

    // Real Host: no forced tone or duration questionnaire.
    await page.locator("#text").fill("Cria um podcast sobre Guimarães");
    await page.locator("#submit").click();
    await page.locator("#execution-confirmation").waitFor({state:"visible"});
    assert.equal(await page.locator("#execution-confirm").isChecked(),false);
    assert.equal(await page.locator("#execution-approve").isDisabled(),true);
    assert.match(await page.locator("#execution-review").textContent(),/Guimarães/);
    await page.locator("#execution-cancel").click();
    assert.ok(routes.includes("/api/confirm-run"));
    assert.equal(routes.includes("/api/approve"),false);

    // A missing topic is asked naturally in the SAME editable Folha.
    await page.locator("#text").fill("Cria um podcast");
    await page.locator("#submit").click();
    try {
      await page.waitForFunction(()=>document.getElementById("message").textContent.includes("tema"),null,{timeout:6000});
    } catch(error) {
      const diag=await page.evaluate(async()=>{
        const s=sessionStorage.getItem("nexus-session");
        const res=await fetch("/api/interpret",{method:"POST",
          headers:{"X-Nexus-Session":s,"Content-Type":"application/json"},
          body:JSON.stringify({text:"Cria um podcast"})});
        return {status:res.status,preview:await res.json(),
          value:document.getElementById("text").value,
          message:document.getElementById("message").textContent,
          notice:document.getElementById("notice").textContent,
          result:document.getElementById("result").hidden,
          submitDisabled:document.getElementById("submit").disabled};
      });
      console.error("ESSENTIAL_QUESTION_DIAGNOSIS",JSON.stringify(diag));
      throw error;
    }
    assert.equal(await page.locator("#text").inputValue(),"Cria um podcast\n");
    const savedQuestion=page.waitForResponse(response=>
      response.request().method()==="POST" &&
      new URL(response.url()).pathname==="/api/folha-draft" &&
      response.request().postDataJSON()?.text==="Cria um podcast\nGuimarães");
    await page.locator("#text").fill("Cria um podcast\nGuimarães");
    assert.equal((await savedQuestion).status(),200);
    await page.reload();
    await page.waitForFunction(()=>document.getElementById("text").value==="Cria um podcast\nGuimarães");
    await page.locator("#submit").click();
    await page.locator("#execution-confirmation").waitFor({state:"visible"});
    assert.match(await page.locator("#execution-review").textContent(),/Cria um podcast[\s\S]*Guimarães/);
    await page.locator("#execution-cancel").click();

    // New request only clears this editor, never switches to a second Folha.
    await page.locator("#navigation summary").click();
    await page.locator("#new").click();
    await page.waitForFunction(()=>document.getElementById("text").value==="" &&
      !document.getElementById("navigation").open);
    assert.equal(await page.evaluate(()=>sessionStorage.getItem("nexus-active-folha")||"a"),"a");
    assert.ok(!routes.some(route=>route==="/api/folha-draft/b"));

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
    await page.locator("#text").fill("Pesquisa fontes sobre Guimarães");
    await page.locator("#submit").click();
    await page.waitForFunction(()=>document.getElementById("content").textContent.includes("pt.wikipedia.org"));
    assert.equal(await page.locator("#result").isVisible(),true);
    assert.equal(await page.locator("#execution-confirmation").isVisible(),false);
    await page.screenshot({path:path.join(artifacts,"folha-fontes.png"),fullPage:true});

    // Persist and recover exact binary input through the one Folha.
    const draftBinary=Buffer.from([0,1,2,10,13,255,128,65,0]);
    const draftPath=path.join(data,"draft-ação.bin");
    await fs.writeFile(draftPath,draftBinary);
    const binarySaved=page.waitForResponse(response=>
      response.request().method()==="POST" &&
      new URL(response.url()).pathname==="/api/folha-draft" &&
      response.request().postDataJSON()?.filename==="draft-ação.bin" &&
      response.request().postDataJSON()?.text==="Trabalho contínuo com anexo");
    await page.locator("#file").setInputFiles(draftPath);
    await page.locator("#text").fill("Trabalho contínuo com anexo");
    const binaryAck=await binarySaved;
    assert.equal(binaryAck.status(),200);
    assert.equal((await binaryAck.json()).attachment,draftBinary.toString("base64"));
    const restored=page.waitForResponse(response=>response.request().method()==="GET" &&
      new URL(response.url()).pathname==="/api/folha-draft/a");
    await page.reload();
    assert.equal((await restored).status(),200);
    await page.waitForFunction(()=>document.getElementById("text").value==="Trabalho contínuo com anexo" &&
      document.getElementById("file").files[0]?.name==="draft-ação.bin");
    const restoredBytes=await page.locator("#file").evaluate(
      async el=>Array.from(new Uint8Array(await el.files[0].arrayBuffer())));
    assert.deepEqual(restoredBytes,Array.from(draftBinary));
    assert.ok(!routes.some(route=>route==="/api/folha-draft/b"));
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({result:"PASS",windowsWebSupported:true,oneFolha:true,
      essentialQuestionSameFolha:true,humanGateIntact:true,pageErrors:errors.length}));
  } finally {
    if(browser)await browser.close();
    if(backend.pid&&backend.exitCode===null){
      backend.kill();await new Promise(ok=>backend.once("exit",ok));
    }
    await fs.rm(data,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
