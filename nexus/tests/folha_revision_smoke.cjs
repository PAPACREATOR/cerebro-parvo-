// Node standard-library regression: stale HTTP response cannot reopen Folha proposal.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const code = fs.readFileSync(require("node:path").join(__dirname, "..", "ui", "app.js"), "utf8");

const flush = async () => { for (let i = 0; i < 8; i++) await Promise.resolve(); };

async function run(mode) {
  const elements=new Map(), events=new Map();
  let resolvePrepare, opens=0, confirms=0;
  const el=id=>{
    if(!elements.has(id))elements.set(id,{value:"",files:[],hidden:false,disabled:false,open:false,
      textContent:"",checked:false,replaceChildren(){},append(){},
      reset(){this.value="";},addEventListener(type,cb){events.set(id+":"+type,cb);},
      showModal(){this.open=true;opens++;},close(){this.open=false;}});
    return elements.get(id);
  };
  const ctx={document:{getElementById:el},location:{hash:""},history:{replaceState(){}},
    sessionStorage:{getItem(){return "s";},setItem(){}},URLSearchParams,
    Uint8Array,clearTimeout(){},setTimeout(){return 1;},
    fetch:async(path)=>{
      if(path==="/api/runs")return {ok:true,json:async()=>[]};
      if(path==="/api/prepare-run")return new Promise(resolve=>{
        resolvePrepare=()=>resolve({ok:true,json:async()=>({ticket:"one",summary:"Verificar",
          filename:"",attachment_bytes:0,attachment_sha256:"0".repeat(64)})});});
      if(path==="/api/confirm-run"){confirms++;return{ok:true,json:async()=>({status:"CANCELLED"})};}
      throw Error("unexpected path "+path);
    }};
  vm.runInNewContext(code,ctx,{filename:"nexus/ui/app.js"});
  const input=el("text");input.value="Verifica este ficheiro";
  const submitting=el("form").onsubmit({preventDefault(){}});
  for(let i=0;i<20&&!resolvePrepare;i++)await flush();
  assert.ok(resolvePrepare,"request was sent");
  if(mode==="edit-return"){
    const before=input.value;
    input.value="Alterado";events.get("text:input")();
    input.value=before;events.get("text:input")();
  }else if(mode==="file"){
    el("file").files=[{name:"outro.txt"}];el("file").onchange();
  }
  resolvePrepare();await submitting;await flush();
  assert.equal(opens,mode==="unchanged"?1:0,"stale response reopened confirmation");
  assert.equal(confirms,0,"unexpected execution request");
  if(mode!=="unchanged"){
    assert.equal(el("execution-confirmation").open,false);
    assert.equal(el("submit").disabled,false);
  }else{
    assert.equal(el("execution-confirmation").open,true);
    assert.equal(el("execution-approve").disabled,true);
  }
}
(async()=>{await run("edit-return");await run("file");await run("unchanged");console.log("PASS Folha stale-response, restored input, file revision and unchanged positive");})().catch(e=>{console.error(e);process.exitCode=1;});
