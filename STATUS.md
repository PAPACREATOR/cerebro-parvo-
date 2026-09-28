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

Obsidian/Joplin/Logseq não são dependências do runtime. Obsidian permanece referência de mercado e viewer opcional de Markdown.

## Prova executada

No commit `f48382f396e3b4af18e62a15c3ecb6104dfd52c9`:

- GitHub Actions: **SUCCESS**;
- suite histórica importada: **34 PASS**;
- writer recuperável ativo: **11 PASS**;
- total executado pela CI em duas suites: **45 testes sem falha**;
- integridade documental: PASS.

Isto continua a ser evidência parcial, não certificação do produto completo.

## Implementação ativa

Existe agora `implementacao/ativa-2026-09-28/`.

O componente `cerebro/persistence.py` implementa o substrato de G10:

`PREPARED em SQLite -> temporário + fsync -> os.replace -> hash -> COMMITTED -> reconcile/resume`.

Testado:

- Creative;
- Canonical com o mesmo writer;
- idempotência;
- crash após PREPARED;
- crash após replace;
- replay/resume a partir do payload congelado;
- divergência de bytes;
- COMMITTED sem ficheiro;
- operação reutilizada com payload diferente;
- path traversal.

**Estado G10/IMP-019: PARCIAL IMPLEMENTADO / TESTADO.** Falta ligar este writer ao pipeline `materialize()`, provar restart de processo real e integração com EventLog/flows.

## Publicação e colaboração

Preparados:

- PolyForm Noncommercial 1.0.0;
- CONTRIBUTING;
- Contributor License Agreement para preservar possibilidade de relicenciamento comercial;
- política de licenciamento comercial;
- SECURITY;
- CODE_OF_CONDUCT;
- THIRD_PARTY_NOTICES;
- template de PR com aceitação explícita do CLA;
- scan textual por padrões comuns de segredos sem resultados encontrados.

A visibilidade do repositório continua **PRIVATE** porque o conector GitHub disponível não expõe a operação administrativa de alteração de visibilidade.

## Ainda NOT RUN

- Activepieces real;
- MCP real entre Core e flows;
- Open Notebook/tiny;
- isolamento real do espaço cognitivo;
- Human Gate + promoção Canonical;
- FTS/rebuild;
- restart de processo real;
- backup/restore;
- Windows;
- E2E do produto;
- instalação por utilizador não técnico.

## Próximo portão

1. ligar o writer ao `materialize()`;
2. primeira vertical slice Activepieces -> Core -> Creative;
3. Human Gate -> Canonical;
4. Open Notebook/tiny isolado.

[Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md) · [Compatibilidade](COMPATIBILITY-MATRIX.md)
