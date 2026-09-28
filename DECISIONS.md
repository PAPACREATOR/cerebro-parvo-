# Decisões vigentes e genealogia

## 28-09-2026 — simplificação para dois blocos nucleares (VIGENTE)

Após reanálise de Activepieces, PiecesOS e projetos de memória MCP locais, a composição física deixa de ser considerada fechada e passa a uma decisão por teste.

### Núcleo candidato

1. **Activepieces Community** — motor executivo/governação operacional.
2. **Memory Provider local SQLite/MCP** — conhecimento/pesquisa/proveniência.

O humano permanece acima dos dois como autoridade final.

SQLite deixa de ser um terceiro serviço: é preferencialmente a base interna do Memory Provider.

### Candidatos de memória

**A — RMANOV/sqlite-memory-mcp (MIT)**
- SQLite/WAL;
- FTS5/BM25;
- semântica opcional via sqlite-vec;
- knowledge graph;
- provenance/event tracking;
- candidate claims;
- promoção approval-aware/canonical facts;
- sessões e recuperação;
- funcionalidades avançadas opcionais que não são necessárias ao núcleo.

É o candidato funcionalmente mais próximo da nossa governação, mas qualquer promoção automática/policy-gated deve ser subordinada ao Human Gate do Cérebro.

**B — Beledarian/mcp-local-memory (MIT)**
- SQLite;
- FTS5;
- sqlite-vec + embeddings locais;
- pesquisa temporal;
- entidades/relações/observações;
- lifecycle auditável;
- suppress/restore em vez de eliminação obrigatória.

É mais simples e menos opinativo sobre governação.

**Decisão:** não escolher por semelhança ou número de funções. Executar o mesmo contrato de testes nos dois. O que cumprir as leis com menos adaptação/dependências vence.

### Activepieces

- core Community: MIT;
- Enterprise/commercial folders não fazem parte do núcleo;
- função: processos, recipes, estados de execução, Human Gate, MCP/HTTP e coordenação;
- Activepieces não é proprietário do conhecimento.

### PiecesOS

- removido como dependência obrigatória;
- permanece benchmark/opção experimental;
- proprietário;
- versões antigas 11.x e 12.3.x demonstram arquitetura local/MCP, mas não existe prova suficiente para o tornar dependência redistribuível/perpétua;
- não escrever arquitetura que dependa do entitlement Pieces.

### Open Notebook e K-DLC

Saem do runtime obrigatório. A investigação feita permanece genealogia e fonte de requisitos. Só regressam se um FAIL concreto justificar.

### Providers periféricos

Zotero, LibreOffice, ComfyUI, LanguageTool, IA local, web, email e publicação são capacidades chamadas por receitas, não blocos nucleares.

### Regras reforçadas

- LIGAR > CONFIGURAR > ADAPTAR > CRIAR.
- Nenhum componente entra sem um FAIL que o justifique.
- Se não pode ser desligado sem destruir o resto, está mal integrado.
- Memória não é autoridade.
- IA não é autoridade.
- Activepieces executa; humano decide.
- PROMOTE_TO_CANONICAL requer Human Gate explícito.
- Similaridade semântica nunca autoriza eliminação.

## Decisão anterior — composição Activepieces + Open Notebook + K-DLC (HISTÓRICA)

A fase anterior demonstrou que ferramentas maduras podiam substituir grande parte do código próprio, mas acumulava providers e responsabilidades. Foi simplificada pela decisão vigente acima. Open Notebook/K-DLC continuam preservados como alternativas históricas, não como orientação operacional.

## Evidência histórica de implementação

O código Python e writer recuperável já testados permanecem preservados como fallback/evidência. Não são apagados e não voltam a ser obrigatórios sem FAIL real.
