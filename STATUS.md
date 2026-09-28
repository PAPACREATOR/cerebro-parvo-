# Estado operacional — 28-09-2026

## Desenho atual

Arquitetura consolidada em [Projeto final auditado](docs/PROJETO-FINAL-AUDITADO-2026-09-28.md):

- Core determinístico pequeno;
- Activepieces como UI/oficina de execução;
- Pieces/Subflows/MCP/API/CLI antes de código próprio;
- um único espaço Open Notebook para cognição temporária;
- uma tiny IA que muda de contexto conforme a tarefa;
- Creative e Canonical em Markdown/formatos abertos com a mesma mecânica de escrita e autoridade distinta;
- SQLite para eventos, IDs, relações, estados, permissões, proveniência e índices;
- 3 memórias, 3 comparadores e M1–M14 preservados como responsabilidades;
- pessoa como autoridade final.

Obsidian/Joplin/Logseq não são dependências do runtime. Obsidian permanece referência de mercado e viewer opcional de Markdown, se útil.

## Prova executada

No commit 3e5b61e31774ba64c8a96cd5b83d515b3f0f3f56:

- GitHub Actions: **SUCCESS**;
- job: **Integridade documental e 34 testes fornecidos**;
- suite candidata: 34 testes reproduzidos sem falha pela workflow;
- código candidato não foi alterado pelos refinamentos de arquitetura.

Isto é regressão do candidato existente. Não é certificação do produto completo.

## Decisões técnicas novas

### G10/IMP-019

Foi selecionado um protocolo mínimo de commit recuperável:

PREPARED em SQLite -> materialização Markdown por replace atómico -> verificação de hash -> COMMITTED -> derivados.

Crash é reconciliado por operation_id, estado e hash. Divergência fecha em RECOVERY_REQUIRED.

**Estado: desenho escolhido; implementação/testes NOT RUN. G10 só fecha depois de crash/replay/idempotência reais.**

### Eliminação

Eliminação automática de originais fica fora do MVP. IMP-024–026 permanecem preservados para trabalho futuro e nunca são necessários para provar o primeiro produto útil.

## Ainda NOT RUN

- Activepieces real;
- MCP real entre Core e flows;
- Open Notebook/tiny;
- isolamento real do espaço cognitivo;
- persistência Creative completa;
- Human Gate + promoção Canonical;
- FTS/rebuild;
- crash/restart/replay;
- Windows;
- E2E do produto;
- instalação por utilizador não técnico.

## Próximo portão

Construir uma vertical slice, não continuar a expandir documentação:

pessoa -> Activepieces -> Core -> Creative -> aprovação -> Canonical,

e depois inserir Open Notebook/tiny como ramo cognitivo isolado.

[Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md) · [Compatibilidade](COMPATIBILITY-MATRIX.md)
