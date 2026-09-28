# Plano de execução vigente — vertical slices

Objetivo: provar o produto com o mínimo de código novo. Os IMP continuam contratos/testes; não são obrigação de implementar uma cadeia de 26 módulos antes de obter valor.

## Fase 1 — persistência recuperável mínima

Estado: **substrato implementado e testado; integração ainda pendente**.

Já existe em `implementacao/ativa-2026-09-28/cerebro/persistence.py`:

1. operation_id;
2. payload congelado em SQLite;
3. PREPARED;
4. temporário + fsync;
5. replace atómico;
6. hash verificado;
7. COMMITTED;
8. reconcile/resume;
9. proteção contra divergência e path traversal.

CI: 11 testes específicos PASS.

Falta para fechar G10/IMP-019:

- ligar ao `materialize()` do pipeline;
- integrar proveniência/EventLog completo;
- restart de processo real;
- confirmar comportamento Windows;
- teste E2E com Creative real.

## Fase 2 — primeira vertical slice sem IA

Criar um flow real:

`Activepieces Chat/trigger -> Core -> capacidade simples -> resultado UNTRUSTED -> validação -> Creative -> apresentação`.

Depois implementar decisão humana e promoção para Canonical, preservando Creative/genealogia.

Critério: fechar/reabrir mantém estado e nenhuma ferramenta escreve diretamente nos cofres.

## Fase 3 — espaço cognitivo

Integrar um único Open Notebook e uma tiny local:

- sessão/contexto por tarefa;
- regras e fontes selecionadas pelo Core;
- budget pelo limite real do modelo;
- duas tarefas de domínios diferentes;
- provar ausência de memória autoritativa transportada;
- resultado volta UNTRUSTED e passa pelos comparadores.

## Fase 4 — capacidades externas

Adicionar uma capacidade de cada vez, preferindo:

`Piece existente -> MCP/API/CLI -> adaptador fino -> código novo`.

Começar por uma integração simples e verificável. LibreOffice, Zotero, LanguageTool, Whisper e outras são opcionais por necessidade.

## Fase 5 — recuperação e produto

- FTS/rebuild;
- restart/replay;
- backup + restore testado;
- Windows;
- E2E;
- instalador/configuração simples;
- experiência sem Markdown/IDs/SQL visíveis.

## Regras de execução

- USE > ADAPT > CREATE.
- Activepieces executa; Core governa.
- Open Notebook/tiny nunca aprova, publica ou escreve diretamente.
- Um flow deve ter descrição equivalente em linguagem natural.
- Criar Subflow apenas para reutilização, teste ou isolamento.
- Não criar frontend próprio enquanto a UI existente servir.
- Não implementar eliminação de originais no MVP.
- Não transformar M1–M14 ou IMP-001–026 em módulos só para preencher uma matriz.

[Projeto final](docs/PROJETO-FINAL-AUDITADO-2026-09-28.md) · [Pendências](docs/PENDENCIAS.md)
