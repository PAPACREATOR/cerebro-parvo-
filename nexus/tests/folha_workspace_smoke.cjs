"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const code=fs.readFileSync(path.join(__dirname,"..","ui","app.js"),"utf8");
const tick=async()=>{for(let i=0;i<18;i++)await Promise.resolve();};
function sheet({handler,responseHandler,storageBlocked=false,hash=""}={}) {
  const nodes=new Map(),storage=new Map([["nexus-session","host-session"]]),calls=[],downloads=[];
  const hidden=new Set(["workspace","history-panel","composer-bottom","notice","result","actions","pdf","empty","resume"]);
  const node=id=>{
    if(!nodes.has(id)) {
      const listeners={};
      nodes.set(id,{id,value:"",files:[],hidden:hidden.has(id),disabled:false,open:false,checked:false,textContent:"",
        attributes:{},classList:{toggle(){}},replaceChildren(){},append(){},focus(){},scrollIntoView(){},
        addEventListener(type,fn){(listeners[type]??=[]).push(fn);},
        dispatch(type,event={}){for(const fn of listeners[type]??[])fn(event);},
        setAttribute(key,value){this.attributes[key]=value;},
        showModal(){this.open=true;},close(){this.open=false;},
        click(){if(this.onclick)return this.onclick();},
        reset(){node("text").value="";node("file").files=[];node("file").value="";},
        requestSubmit(){return node("form").onsubmit({preventDefault(){}});}
      });
    }
    return nodes.get(id);
  };
  const ctx=vm.createContext({
    document:{getElementById:node,querySelector(selector){return node(selector===".sheet"?"surface":selector===".attachment"?"attachment":selector.slice(1));},
      createElement(){const value=node("download-"+downloads.length);value.click=()=>downloads.push(value);return value;}},
    location:{hash},history:{replaceState(){}},
    sessionStorage:{getItem(key){if(storageBlocked)throw new Error("Blocked");return storage.get(key)??null;},
      setItem(key,value){if(storageBlocked)throw new Error("Blocked");storage.set(key,value);}},
    fetch:async(route,options)=>{
      const body=options?.body?JSON.parse(options.body):undefined;calls.push({route,body,headers:options?.headers});
      const value=handler?await handler(route,body):[];
      if(responseHandler)return responseHandler(route,value);
      return {ok:true,json:async()=>value};
    },
    URLSearchParams,Uint8Array,Blob,btoa,clearTimeout(){},setTimeout(){return 0;},
    URL:{createObjectURL(blob){storage.set("download-blob",blob);return "blob:preparation";},revokeObjectURL(){}},
    console
  });
  vm.runInContext(code,ctx);
  return {node,storage,calls,downloads,ctx,
    input(id,value){node(id).value=value;node(id).dispatch("input");},
    async submit(text){this.input("text",text);await node("form").onsubmit({preventDefault(){}});await tick();}
  };
}
test("white sheet has no wizard, product picker, six steps or brief forms",()=>{
  const html=fs.readFileSync(path.join(__dirname,"..","ui","index.html"),"utf8");
  assert.match(html,/id="text"/);
  assert.match(html,/id="result"/);
  for(const forbidden of ['id="workspace"','id="product"','id="stage-0"',
    'id="brief-tone"','id="stage-reviewed"','id="stage-next"'])
    assert.equal(html.includes(forbidden),false,forbidden);
});
test("text-only web request goes from Nexus classification to Host research",async()=>{
  const ui=sheet({handler:async(route)=>{
    if(route==="/api/interpret") return {status:"RESOLVED",intent:"web",original:"Pesquisa fontes sobre Guimarães",
      assistant:{process:"web",question:null,missing:[]}};
    if(route==="/api/research")return {run_id:"a".repeat(32)};
    if(route.startsWith("/api/runs/"))return {status:"RUNNING",title:"Pesquisa"};
    return [];
  }});
  await ui.submit("Pesquisa fontes sobre Guimarães");
  assert.deepEqual(ui.calls.map(c=>c.route),["/api/interpret","/api/research","/api/runs/"+"a".repeat(32)]);
  assert.equal(ui.calls[1].body.text,"Pesquisa fontes sobre Guimarães");
  assert.equal(ui.node("result").hidden,false);
  assert.equal(ui.node("execution-confirmation").open,false);
  assert.equal(ui.calls.some(c=>c.route==="/api/confirm-run"),false);
});
test("Nexus asks tone and duration in natural language before the Host",async()=>{
  const ui=sheet({handler:async(route,body)=>{
    if(route==="/api/interpret"){
      const answered=/^Cria um podcast sobre Guimarães\n/.test(body.text);
      return {status:"RESOLVED",intent:"trabalhar",original:body.text,
        assistant:{process:"podcast",question:answered?null:"Que tom pretendes e quanto deve durar?",
          missing:answered?[]:["tom","duração"]}};
    }
    if(route==="/api/prepare-run")return {ticket:"one",process:"podcast",filename:"pedido"};
    return [];
  }});
  await ui.submit("Cria um podcast sobre Guimarães");
  assert.match(ui.node("message").textContent,/tom.*durar/);
  assert.equal(ui.calls.some(c=>c.route==="/api/prepare-run"),false);
  await ui.submit("Informal, 5 minutos");
  assert.equal(ui.calls.filter(c=>c.route==="/api/interpret").length,2);
  const approved=ui.calls.find(c=>c.route==="/api/prepare-run");
  assert.match(approved.body.text,/^Cria um podcast sobre Guimarães/);
  assert.match(approved.body.text,/Informal, 5 minutos/);
  assert.equal(approved.body.filename,"");
  assert.equal(approved.body.attachment,"");
  assert.equal(ui.node("execution-confirmation").open,true);
  assert.equal(ui.node("execution-approve").disabled,true);
  assert.equal(ui.calls.some(c=>c.route==="/api/confirm-run"),false);
});
test("registered file capability still requires the original human ticket",async()=>{
  const req="& verificar integridade de ficheiro";
  const ui=sheet({handler:async(route)=>{
    if(route==="/api/interpret")return {status:"RESOLVED",intent:"trabalhar",original:req};
    if(route==="/api/prepare-run")return {ticket:"native",process:"verify",filename:"fonte.txt"};
    if(route==="/api/confirm-run")return {status:"CANCELLED"};
    return [];
  }});
  ui.node("file").files=[{name:"fonte.txt",size:1,arrayBuffer:async()=>Uint8Array.from([97]).buffer}];
  await ui.submit(req);
  assert.equal(ui.node("execution-confirmation").open,true);
  assert.equal(ui.node("execution-approve").disabled,true);
  await ui.node("execution-cancel").onclick();
  assert.equal(ui.calls.filter(c=>c.route==="/api/confirm-run").length,1);
  assert.equal(ui.calls.find(c=>c.route==="/api/confirm-run").body.confirmed,false);
});
test("unknown tasks do not invent tool execution",async()=>{
  const ui=sheet({handler:async(route,body)=>{
    assert.equal(route,"/api/interpret");
    return {status:"UNRESOLVED",original:body.text,assistant:{process:null,question:null,missing:[]}};
  }});
  await ui.submit("Faz uma operação desconhecida");
  assert.deepEqual(ui.calls.map(c=>c.route),["/api/interpret"]);
  assert.equal(ui.node("execution-confirmation").open,false);
  assert.equal(ui.node("result").hidden,false);
});

test("one white Folha request proposes and runs verify then PDF with two explicit Host tickets",async()=>{
  const original="Verifica este documento e converte-o em PDF";
  const sha="f".repeat(64);
  const calls=[];
  const ui=sheet({handler:async(route,body)=>{
    calls.push({route,body});
    if(route==="/api/interpret")return {
      status:"UNRESOLVED",original:body.text,execution:"NOT_AUTHORIZED",
      composite:{authority:"NONE",execution:"NOT_AUTHORIZED",requires_human_confirmation:true,
        steps:[{process:"verify",command:"verificar integridade de ficheiro"},
               {process:"convert_pdf",command:"converter para pdf"}]},
    };
    if(route==="/api/prepare-run"){
      const first=body.text.includes("integridade");
      return {ticket:first?"verify-ticket":"writer-ticket",process:first?"verify":"convert_pdf",
              filename:body.filename,attachment_sha256:sha};
    }
    if(route==="/api/confirm-run")return {run_id:body.text.includes("integridade")?"a".repeat(32):"b".repeat(32)};
    if(route==="/api/runs/"+"a".repeat(32))return {
      status:"HUMAN_REQUIRED",process_id:"verify",input_sha256:sha,result:{status:"PASS"},
    };
    if(route==="/api/runs/"+"b".repeat(32))return {
      status:"HUMAN_REQUIRED",process_id:"convert_pdf",input_sha256:sha,
      artifact_sha256:"b".repeat(64),result:{title:"PDF verificado",status:"UNKNOWN"},
      content:"# PDF",
    };
    if(route==="/api/flow-receipt")return {
      authority:"NONE",execution:"NOT_AUTHORIZED",receipt_sha256:"c".repeat(64),
      steps:[{process:"verify",run_id:"a".repeat(32)},
             {process:"convert_pdf",run_id:"b".repeat(32)}],
      product:{run_id:"b".repeat(32),sha256:"b".repeat(64)},
    };
    return [];
  }});
  ui.node("file").files=[{name:"source.odt",size:3,arrayBuffer:async()=>Uint8Array.from([1,2,3]).buffer}];
  await ui.submit(original);
  assert.equal(ui.node("execution-confirmation").open,true);
  assert.match(ui.node("execution-review").textContent,/Pedido original: Verifica este documento/);
  assert.deepEqual(calls.filter(v=>v.route==="/api/prepare-run").map(v=>v.body.text),
    ["& verificar integridade de ficheiro"]);
  assert.equal(calls.filter(v=>v.route==="/api/confirm-run").length,0);
  ui.node("execution-confirm").checked=true;
  await ui.node("execution-approve").onclick();
  assert.equal(ui.node("execution-confirmation").open,true);
  assert.deepEqual(calls.filter(v=>v.route==="/api/prepare-run").map(v=>v.body.text),
    ["& verificar integridade de ficheiro","& converter para pdf"]);
  assert.equal(calls.filter(v=>v.route==="/api/confirm-run").length,1);
  ui.node("execution-confirm").checked=true;
  await ui.node("execution-approve").onclick();
  assert.deepEqual(calls.filter(v=>v.route==="/api/confirm-run").map(v=>v.body.text),
    ["& verificar integridade de ficheiro","& converter para pdf"]);
  assert.equal(ui.node("execution-confirmation").open,false);
  assert.equal(ui.node("pdf").hidden,false);
  assert.equal(ui.node("result-title").textContent,"PDF verificado");
  const receiptRequest=calls.find(v=>v.route==="/api/flow-receipt");
  assert.ok(receiptRequest,"verified two-step receipt must be requested");
  assert.equal(receiptRequest.body.text,original);
  assert.equal(receiptRequest.body.input_sha256,sha);
  assert.equal(receiptRequest.body.verify_run_id,"a".repeat(32));
  assert.equal(receiptRequest.body.convert_run_id,"b".repeat(32));
  assert.match(ui.node("notice").textContent,/cadeia verificada/);
});
test("refused first tool and edited request never prepare or execute a second tool",async()=>{
  const original="Verifica este documento e converte-o em PDF";
  const cases=["failed","edited"];
  for(const scenario of cases){
    const ui=sheet({handler:async(route,body)=>{
      if(route==="/api/interpret")return {status:"UNRESOLVED",original:body.text,
        composite:{authority:"NONE",execution:"NOT_AUTHORIZED",
          steps:[{process:"verify",command:"verificar integridade de ficheiro"},
                 {process:"convert_pdf",command:"converter para pdf"}]}};
      if(route==="/api/prepare-run")return {
        ticket:"verify-ticket",process:"verify",attachment_sha256:"a".repeat(64),filename:"source.odt"};
      if(route==="/api/confirm-run")return {run_id:"a".repeat(32)};
      if(route.startsWith("/api/runs/"))return {
        status:"HUMAN_REQUIRED",process_id:"verify",input_sha256:"a".repeat(64),
        result:{status:"FAIL"}};
      return [];
    }});
    ui.node("file").files=[{name:"source.odt",size:3,arrayBuffer:async()=>Uint8Array.from([1,2,3]).buffer}];
    await ui.submit(original);
    if(scenario==="edited")ui.input("text",original+" agora");
    else {
      ui.node("execution-confirm").checked=true;
      await ui.node("execution-approve").onclick();
    }
    assert.equal(ui.calls.filter(x=>x.route==="/api/prepare-run").length,1);
    assert.equal(ui.calls.filter(x=>x.route==="/api/confirm-run").length,scenario==="failed"?1:0);
  }
});
