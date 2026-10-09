"use strict";
const el = id => document.getElementById(id);
const fragment = new URLSearchParams(location.hash.slice(1));
if (fragment.has("session")) {
  sessionStorage.setItem("nexus-session", fragment.get("session"));
  history.replaceState(null, "", "/");
}
const session = sessionStorage.getItem("nexus-session") || "";
let current = null, ticket = null, poll = null, currentContent = "", executionTicket = null;
const labels = {RUNNING:"A executar",HUMAN_REQUIRED:"Em Creative · por rever",PASS:"Aprovado",FAIL:"Não concluído",UNKNOWN:"Por esclarecer",BLOCKED:"Precisa de atenção"};
async function api(path, data) {
  const response = await fetch(path, {method:data === undefined ? "GET":"POST",
    headers:{"X-Nexus-Session":session,"Content-Type":"application/json"},
    body:data === undefined ? undefined:JSON.stringify(data)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || "Não foi possível concluir.");
  return value;
}
function notice(message) { el("notice").textContent = message; }
async function list() {
  const items = await api("/api/runs");
  el("history").replaceChildren();
  items.forEach(item => {
    const button = document.createElement("button");
    button.className="history-item"; button.textContent=item.title;
    const small = document.createElement("small"); small.textContent=labels[item.status] || item.status;
    button.append(small); button.onclick=()=>show(item.run_id).catch(e=>notice(e.message));
    el("history").append(button);
  });
}
async function show(id) {
  current=id;
  const item=await api("/api/runs/"+id);
  el("empty").hidden=true; el("result").hidden=false;
  el("status").textContent=labels[item.status] || item.status;
  el("result-title").textContent=item.result ? item.result.title : item.title;
  el("message").textContent=item.message;
  el("pdf").hidden=!item.artifact_sha256;
  currentContent=item.content || "";
  el("content").textContent=currentContent;
  el("actions").hidden=!item.content;
  el("prepare").hidden=item.status!=="HUMAN_REQUIRED";
  el("submit").disabled=item.status==="RUNNING";
  clearTimeout(poll);
  if(item.status==="RUNNING") poll=setTimeout(()=>show(id).catch(e=>notice(e.message)),900);
  else await list();
}
async function requestPayload() {
  const file=el("file").files[0];
  if(file && file.size>2097152) throw new Error("Escolhe um ficheiro até 2 MB.");
  let attachment="";
  if(file) {
    const bytes=new Uint8Array(await file.arrayBuffer());
    let binary="";
    for(let i=0;i<bytes.length;i+=8192) binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
    attachment=btoa(binary);
  }
  return {text:el("text").value,filename:file ? file.name:"",attachment};
}
el("form").onsubmit=async event=>{
  event.preventDefault(); notice(""); el("submit").disabled=true;
  try {
    const payload=await requestPayload();
    const prepared=await api("/api/prepare-run",payload);
    executionTicket=prepared.ticket;
    el("execution-summary").textContent=prepared.summary;
    el("execution-review").textContent="Ficheiro: "+prepared.filename+"\nBytes: "+prepared.attachment_bytes+"\nSHA-256: "+prepared.attachment_sha256;
    el("execution-confirm").checked=false;
    el("execution-approve").disabled=true;
    el("execution-confirmation").showModal();
  } catch(error) {notice(error.message);el("submit").disabled=false;}
};
el("execution-confirm").onchange=()=>{el("execution-approve").disabled=!el("execution-confirm").checked;};
el("execution-cancel").onclick=async()=>{
  const stale=executionTicket; executionTicket=null;
  try {
    if(stale) await api("/api/confirm-run",{ticket:stale,confirmed:false,...await requestPayload()});
  } catch(_error) {}
  el("execution-confirmation").close(); el("submit").disabled=false;
};
el("execution-approve").onclick=async()=>{
  el("execution-approve").disabled=true;
  const active=executionTicket; executionTicket=null;
  try {
    const response=await api("/api/confirm-run",{ticket:active,confirmed:true,...await requestPayload()});
    el("execution-confirmation").close();
    await list(); await show(response.run_id);
  } catch(error) {
    el("execution-confirmation").close(); notice(error.message); el("submit").disabled=false;
  }
};
el("file").onchange=()=>{el("file-label").textContent=el("file").files[0]?.name || "Até 2 MB · um ficheiro de cada vez";};
el("new").onclick=()=>{
  clearTimeout(poll); current=null; executionTicket=null; el("form").reset(); el("file-label").textContent="Até 2 MB · um ficheiro de cada vez";
  el("empty").hidden=false;el("result").hidden=true;el("submit").disabled=false;notice("");el("text").focus();
};
el("prepare").onclick=async()=>{
  try {const value=await api("/api/prepare",{run_id:current}); ticket=value.ticket;
    el("review").textContent=value.content;el("confirm").checked=false;el("approve").disabled=true;el("approval").showModal();
  } catch(error){notice(error.message);}
};
el("confirm").onchange=()=>{el("approve").disabled=!el("confirm").checked;};
el("cancel").onclick=()=>{ticket=null;el("approval").close();};
el("approve").onclick=async()=>{
  el("approve").disabled=true;
  try {await api("/api/approve",{run_id:current,ticket,confirmed:el("confirm").checked});el("approval").close();await show(current);notice("Resultado guardado como aprovado.");}
  catch(error){el("approval").close();notice(error.message);}
};
el("download").onclick=()=>{
  const url=URL.createObjectURL(new Blob([currentContent],{type:"text/markdown;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download="resultado-nexus.md";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
list().catch(error=>notice(error.message));

el("pdf").onclick=async()=>{
  try {
    const response=await fetch("/api/pdf/"+current,{headers:{"X-Nexus-Session":session}});
    if(!response.ok) throw new Error("Não foi possível obter o PDF verificado.");
    const url=URL.createObjectURL(await response.blob());
    const a=document.createElement("a");a.href=url;a.download="resultado-nexus.pdf";a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  } catch(error){notice(error.message);}
};
