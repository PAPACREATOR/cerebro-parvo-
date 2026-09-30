# Decisões vigentes e genealogia

## 30-09-2026 — Nexus Minimal: launcher metódico + bancada descartável (VIGENTE)

A arquitetura foi reduzida novamente para preservar funções e cortar engenharia própria.

### Formulação vigente

**Nexus é um launcher metódico, com memória, leis e templates executáveis, que compõe ferramentas existentes para atingir um fim.**

Fluxo principal:

```text
Humano → Folha em linguagem natural → Condutor
                                  ├→ template/processo conhecido → ferramenta/capability
                                  └→ problema novo → Open Notebook/tiny → resultado
                                                        ↓
Creative → VERIFY → PASS/FAIL/UNKNOWN → Human Gate quando exigido → Canonical
                                                        ↓
                                    experiência validada → template candidato
```

### Responsabilidades fechadas

- **Folha Nexus:** interface inicial em linguagem natural; anexos, resultados e Human Gates. Infraestrutura fica invisível na utilização normal.
- **Conductor:** runtime/condutor candidato para flows, routing, scripts, MCP, paralelismo e gates. Deve passar testes locais antes de ser dependência definitiva.
- **Open Notebook:** apenas bancada cognitiva. Não é memória Nexus, Creative, Canonical, arquivo, Wiki, autoridade ou interface principal.
- **Nexus/Windows:** memória soberana, regras, proveniência, histórico, processos/templates e continuidade.
- **Tiny local:** cognição probabilística apenas quando necessária, dentro do pacote de trabalho autorizado.
- **Capabilities:** LibreOffice, Zotero, LanguageTool, web, imagem, áudio, Whisper/TTS etc. entram por processo, nunca por antecipação.

### Memória soberana

A memória durável pertence ao Nexus e deve permanecer em formatos portáveis/reconstruíveis: Markdown, JSON, YAML, fontes originais, hashes e logs; SQLite/FTS5 pode servir de índice/estado quando necessário. Destruir Open Notebook não pode destruir conhecimento Nexus.

### Agente em microprocesso

Um agente não precisa de identidade persistente. Pode ser reconstruído por tarefa como:

`tiny + prompt + contexto permitido + leis + ferramentas permitidas + schema + objetivo`.

Executa, devolve resultado estruturado e termina. O que persiste é memória/processo/proveniência, não o agente.

### Templates/processos

Experiência validada pode ser compilada num processo explícito e testável (`process.yaml`, schemas, prompts, regras e testes). A primeira resolução pode usar mais cognição; ocorrências semelhantes devem reutilizar o processo e, quando possível, reduzir chamadas à IA. Aprendizagem nunca aumenta autoridade.

### Benchmark externo único

Para impedir dispersão, o único projeto externo escolhido para comparação arquitetónica nesta fase é **Negentropy-Laby/OpenDoge**. Motivos: local-first/single-operator, workflow templates, runtime contracts, approvals, evidence/replay e extensão por slots/capabilities. É benchmark, não dependência nem arquitetura a copiar. Só se adapta algo se reduzir código/risco sem violar leis Nexus e com licença compatível.

### Testes que decidem

1. Folha → condutor → bancada → JSON → Creative → Folha;
2. Canonical não aceita escrita direta;
3. Human Gate permite promoção explícita;
4. Open Notebook pode ser destruído/reconstruído sem perda Nexus;
5. tiny não ganha acesso fora do pacote permitido;
6. proveniência percorre resultado ↔ processo ↔ contexto/evidência ↔ fonte/pedido;
7. microprocessos independentes podem comparar e produzir PASS/FAIL/UNKNOWN;
8. tarefa semelhante reutiliza experiência/processo com menos descoberta;
9. substituir tiny/bancada não destrói leis nem memória.

### Regra de engenharia

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.** O Core programa sobretudo cola, contratos, memória, leis, auditoria e testes. Não reprogramar motores maduros.

---

## 28-09-2026 — simplificação Activepieces + Memory Provider (HISTÓRICA / SUPERADA)

A fase anterior propôs Activepieces Community + um Memory Provider SQLite/MCP como dois blocos nucleares. Foi útil para provar que workflows, memória e providers podiam ser desacoplados, mas ainda atribuía demasiada responsabilidade a um provider de memória e mantinha um motor específico como centro conceptual.

Os candidatos RMANOV/sqlite-memory-mcp e Beledarian/mcp-local-memory permanecem referências históricas. Não são dependências vigentes e só regressam perante FAIL concreto.

PiecesOS permanece benchmark histórico/proprietário, não dependência.

## Decisão anterior — Activepieces + Open Notebook + K-DLC (HISTÓRICA)

Demonstrou que ferramentas maduras podiam substituir grande parte do código próprio, mas acumulava providers e responsabilidades. Open Notebook regressa agora com responsabilidade muito mais estreita: **bancada de trabalho apenas**.

## Evidência histórica de implementação

Código Python e writer recuperável já testados permanecem preservados como fallback/evidência. Não são apagados e não voltam a ser obrigatórios sem FAIL real.
