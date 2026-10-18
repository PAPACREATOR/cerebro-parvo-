"use strict";
// Exercise the actual Folha browser script with a deterministic HTTP peer.
// Natural, essential-only questions stay in the same Folha across partial replies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const code = fs.readFileSync(path.join(__dirname, "..", "ui", "app.js"), "utf8");
const nodes = new Map(), calls = [];
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {
    value: "", files: [], hidden: false, disabled: false,
    open: false, checked: false, textContent: "", style: {},
    addEventListener(event, fn) { this["on" + event] = fn; },
    replaceChildren() {}, append() {}, reset() {this.value = "";},
    focus() {}, close() {this.open = false;}, showModal() {this.open = true;}
  });
  return nodes.get(id);
}
function interpreted(text) {
  const missing = text.split("\n").at(-1).trim() === "Guimarães" ? [] : ["tema"];
  return {
    status: "RESOLVED", intent: "trabalhar", original: text,
    execution: "NOT_AUTHORIZED",
    assistant: {
      process: "podcast", missing,
      question: missing.length ? "Sobre que tema queres trabalhar?" : null,
    }
  };
}
const ctx = {
  document: {getElementById: node, querySelector() {return null;}},
  location: {hash: ""}, history: {replaceState() {}},
  sessionStorage: {getItem() {return "test-session";}, setItem() {}},
  URLSearchParams, Uint8Array, btoa: str => Buffer.from(str, "binary").toString("base64"),
  clearTimeout() {}, setTimeout() {return 1;},
  fetch: async (uri, options) => {
    const body = options?.body ? JSON.parse(options.body) : null;
    calls.push({uri, body});
    if (uri === "/api/runs") return {ok: true, json: async () => []};
    if (uri === "/api/interpret") return {ok: true, json: async () => interpreted(body.text)};
    if (uri === "/api/prepare-run") return {ok: true, json: async () => ({
      ticket: "local-only", process: "podcast", filename: "pedido",
      summary: "Preparar plano de podcast", attachment_bytes: 0,
    })};
    throw Error("Unexpected endpoint: " + uri);
  }
};
vm.runInNewContext(code, ctx, {filename: "nexus/ui/app.js"});
async function submit(message) {
  node("text").value = message;
  node("text").oninput?.();
  await node("form").onsubmit({preventDefault() {}});
}
(async () => {
  const initial = "Cria um podcast";
  await submit(initial);
  assert.match(node("message").textContent, /tema/);
  assert.equal(node("text").value,initial+"\n");
  assert.equal(calls.filter(c=>c.uri==="/api/prepare-run").length,0);

  // Incomplete reply cannot invent a topic or discard preceding text.
  const partial=initial+"\nAinda não sei";
  await submit(partial);
  assert.equal(node("text").value,partial+"\n");
  assert.match(node("message").textContent,/tema/);
  assert.equal(calls.filter(c=>c.uri==="/api/prepare-run").length,0);
  assert.equal(calls.filter(c=>c.uri==="/api/interpret").at(-1).body.text,partial);

  // Essential detail permits one ticket, without executing before consent.
  const complete=partial+"\nGuimarães";
  await submit(complete);
  const prepares=calls.filter(c=>c.uri==="/api/prepare-run");
  assert.equal(prepares.length,1);
  assert.equal(prepares[0].body.text,complete);
  assert.equal(node("execution-confirmation").open,true);
  assert.equal(node("execution-approve").disabled,true);
  assert.equal(calls.filter(c=>c.uri==="/api/confirm-run").length,0);
  console.log("PASS same Folha: partial topic answer retained, no invented values, human gate intact");

})().catch(error => {console.error(error); process.exitCode = 1;});
