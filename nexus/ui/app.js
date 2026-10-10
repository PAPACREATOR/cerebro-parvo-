"use strict";
const el = id => document.getElementById(id);
const fragment = new URLSearchParams(location.hash.slice(1));
if (fragment.has("session")) {
  sessionStorage.setItem("nexus-session", fragment.get("session"));
  history.replaceState(null, "", "/");
}
const session = sessionStorage.getItem("nexus-session") || "";
let current = null, ticket = null, poll = null, currentContent = "", executionTicket = null;
let editRevision = 0;
function invalidateExecutionProposal() {
  editRevision++;
  executionTicket = null;
  const modal = el("execution-confirmation");
  if (modal.open) modal.close();
  el("execution-approve").disabled = true;
  el("submit").disabled = false;
}
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
function showInterpretation(preview) {
  // An interpretation is never an execution or a Creative candidate.
  current=null;
  el("empty").hidden=true;el("result").hidden=false;
  el("status").textContent=preview.status==="RESOLVED"?"Reconhecido · não executado":
    (preview.status==="BLOCKED"?"Bloqueado":"Precisa de esclarecimento");
  const intents={arquivo:"Arquivo",fontes:"Fontes",perguntar:"Pergunta",
    trabalhar:"Trabalhar",calcular:"Calcular",tema:"Tema",web:"Web"};
  el("result-title").textContent=preview.status==="RESOLVED"?
    ("Intenção: "+(intents[preview.intent]||"por esclarecer")):"Interpretação pendente";
  el("message").textContent=preview.status==="RESOLVED"?
    "A Folha compreendeu a intenção. Só estão habilitadas, com confirmação humana e anexo, a verificação de integridade e duas exportações Writer expressamente pedidas.":
    "Reformula o pedido. Nenhuma ferramenta foi chamada.";
  el("content").textContent=preview.original;
  currentContent="";
  el("actions").hidden=true;el("pdf").hidden=true;
}
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
    const revision=editRevision;
    const payload=await requestPayload();
    if (revision!==editRevision) throw new Error("O texto ou anexo mudou durante a preparação. Revê o pedido.");
    const preview=await api("/api/interpret",{text:payload.text});
    if(revision!==editRevision) throw new Error("O texto ou anexo mudou durante a interpretação.");
    if(preview.status!=="RESOLVED"||preview.intent!=="trabalhar"||
       !payload.filename||!payload.attachment) {
      showInterpretation(preview);
      return;
    }
    let prepared;
    try {
      prepared=await api("/api/prepare-run",payload);
    } catch(error) {
      // Never pretend a recognized intent is an executable capability.
      showInterpretation(preview);
      notice(error.message);
      return;
    }
    if (revision!==editRevision) {
      notice("O texto ou anexo mudou durante a preparação. Revê o pedido.");
      return;
    }
    executionTicket=prepared.ticket;
    el("execution-summary").textContent=prepared.summary;
    el("execution-review").textContent="Operação: "+prepared.process+"\nFicheiro: "+prepared.filename+"\nBytes: "+prepared.attachment_bytes+"\nSHA-256: "+prepared.attachment_sha256;
    el("execution-confirm").checked=false;
    el("execution-approve").disabled=true;
    el("execution-confirmation").showModal();
  } catch(error) {notice(error.message);}
  finally {if(!el("execution-confirmation").open)el("submit").disabled=false;}
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
  const active=executionTicket, revision=editRevision; executionTicket=null;
  try {
    if(!active)throw new Error("A confirmação já não é válida.");
    const payload=await requestPayload();
    if(revision!==editRevision)throw new Error("O pedido mudou durante a confirmação.");
    const response=await api("/api/confirm-run",{ticket:active,confirmed:true,...payload});
    el("execution-confirmation").close();
    await list(); await show(response.run_id);
  } catch(error) {
    el("execution-confirmation").close(); notice(error.message); el("submit").disabled=false;
  }
};
el("text").addEventListener("input", invalidateExecutionProposal);
el("file").onchange=()=>{invalidateExecutionProposal();el("file-label").textContent=el("file").files[0]?.name || "Até 2 MB · um ficheiro de cada vez";};
// Drag-and-drop is an input convenience, not an authorization or execution.
const surface=document.querySelector?.(".sheet");
if(surface){
  surface.addEventListener("dragover",event=>event.preventDefault());
  surface.addEventListener("drop",event=>{
    event.preventDefault();
    const files=event.dataTransfer?.files;
    if(!files?.length)return;
    if(files.length!==1){notice("Junta um ficheiro de cada vez.");return;}
    if(files[0].size>2097152){notice("Escolhe um ficheiro até 2 MB.");return;}
    try {el("file").files=files;el("file").onchange();}
    catch(_error){notice("Usa «Juntar ficheiro» para selecionar o documento.");}
  });
}
const attach=document.querySelector?.(".attachment");
if(attach) attach.addEventListener("keydown",event=>{
  if(event.key==="Enter"||event.key===" "){event.preventDefault();el("file").click();}
});
el("new").onclick=()=>{
  clearTimeout(poll); current=null; invalidateExecutionProposal(); el("form").reset(); el("file-label").textContent="Até 2 MB · um ficheiro de cada vez";
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
