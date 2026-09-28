# Cérebro Independente

Sistema local-first de conhecimento e execução governada: a pessoa escreve em linguagem normal; um Core determinístico aplica regras, memória e autoridade; Activepieces executa flows e capacidades; uma tiny IA só entra num espaço Open Notebook isolado quando é necessária.

A implementação é **usar > adaptar > criar**. Nenhuma tecnologia é defendida por tradição: mantém-se apenas o que reduz complexidade sem quebrar os contratos.

## Projeto consolidado

1. [Projeto final auditado — 28/09/2026](docs/PROJETO-FINAL-AUDITADO-2026-09-28.md)
2. [Constituição e precedência](CEREBRO_CONSTITUTION.md)
3. [Arquitetura vigente](CEREBRO_ARCHITECTURE.md)
4. [Arquitetura operacional](docs/ARQUITETURA-OPERACIONAL-ADAPTATIVA.md)
5. [Estado real e evidência](STATUS.md)
6. [Matriz de compatibilidade](COMPATIBILITY-MATRIX.md)
7. [Matriz M1–M14 e IMP-001–026](docs/MATRIZ-CONFORMIDADE.md)

## Arquitetura em uma frase

**Core governa; Activepieces executa; Open Notebook pensa sob contexto limitado; Creative preserva propostas; a pessoa promove; Canonical guarda o aprovado.**

Mantêm-se:

- 3 memórias;
- 2 classes de autoridade: Creative e Canonical;
- 3 comparadores;
- M1–M14 como responsabilidades, não como obrigação de criar 14 serviços;
- proveniência, genealogia, contradições, EventLog/recovery e Human Gate;
- Markdown/formatos abertos para conteúdo humano;
- SQLite para eventos, IDs, relações, estados e índices.

Não são dependências obrigatórias: Obsidian, Joplin, Logseq, frontend próprio, vários agentes/notebooks permanentes ou RAG próprio no Core.

## Estado comprovado

O main mais recente antes desta consolidação, 3e5b61e3, passou no GitHub Actions a job **“Integridade documental e 34 testes fornecidos”**. Isto confirma regressão da suite candidata e integridade documental.

Não prova ainda:

- integração real Core ↔ Activepieces;
- Open Notebook + tiny IA;
- isolamento/sandbox E2E;
- protocolo G10/IMP-019;
- promoção Creative → Canonical;
- crash/replay real;
- Windows;
- M1–M14 ponta-a-ponta.

O produto ainda não é uma release.

## Código candidato

O candidato preservado está em [implementacao/candidata-2026-09-27](implementacao/candidata-2026-09-27). Os IMP-001–026 são contratos de comportamento/teste da família de importação; não devem ser transformados mecanicamente em 26 módulos.

## Licença

O repositório contém [PolyForm Noncommercial 1.0.0](LICENSE). Uso comercial exige licença/permissão separada do titular dos direitos. Ver [estado de licenciamento](docs/LICENCIAMENTO-PENDENTE.md). Licenças de componentes de terceiros continuam independentes.

[Plano de implementação](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md) · [Uso do GitHub](TEAM_WORKFLOW.md)
