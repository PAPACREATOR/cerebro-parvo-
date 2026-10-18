"use strict";
// Exercise the actual Folha browser script with a deterministic HTTP peer.
// A reply supplying only duration must NOT be silently copied into tone.
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
  const missing = [];
  if (!/\b(?:documental|informal)\b/iu.test(text)) missing.push("tom");
  if (!/\b\d+\s*minutos?\b/iu.test(text)) missing.push("duração");
  return {
    status: "RESOLVED", intent: "trabalhar", original: text,
    execution: "NOT_AUTHORIZED",
    assistant: {
      process: "podcast", missing,
      question: missing.length ? "Falta informação para continuar." : null,
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
  const original = "Cria um podcast sobre Guimarães";
  await submit(original);
  assert.match(node("message").textContent, /Falta informação/);
  assert.equal(calls.filter(c => c.uri === "/api/prepare-run").length, 0);

  // A single answer with duration does not supply any tone.
  await submit(original+"\n5 minutos");
  assert.equal(calls.filter(c => c.uri === "/api/prepare-run").length, 0,
    "Invented tone was accepted as if the human had specified it");
  const second = calls.filter(c => c.uri === "/api/interpret").at(-1);
  assert.equal(second.body.text, original + "\n5 minutos");
  assert.match(node("message").textContent, /Falta informação/);

  // A later independent answer supplies the missing tone explicitly.
  await submit(original+"\n5 minutos\ndocumental");
  const prepares = calls.filter(c => c.uri === "/api/prepare-run");
  assert.equal(prepares.length, 1);
  assert.equal(prepares[0].body.text, original + "\n5 minutos\ndocumental");
  assert.doesNotMatch(prepares[0].body.text, /Tom: 5 minutos|Duração: documental/i);
  assert.equal(node("execution-confirmation").open, true);
  assert.equal(node("execution-approve").disabled, true);
  assert.equal(calls.filter(c => c.uri === "/api/confirm-run").length, 0);
  console.log("PASS staged dialogue: no fabricated tone, explicit duration and tone, human gate intact");
})().catch(error => {console.error(error); process.exitCode = 1;});
