# Documentação interna do Nexus

Esta pasta contém a documentação para desenvolvimento, planeamento e manutenção. A porta de entrada pública do projeto é o [README principal](../README.md).

## Estrutura

- [`architecture/`](architecture/) — arquitetura, constituição e decisões
- [`planning/`](planning/) — planos de implementação, instalação, compatibilidade e estado
- [`internal/`](internal/) — fluxo de trabalho, agentes e regras internas
- [`architecture/DECISIONS.md`](architecture/DECISIONS.md) — decisões arquiteturais e genealogia

## Regra

A raiz do repositório é a montra pública. Esta pasta é para quem desenvolve, mantém ou contribui.

## Onde consultar o estado que realmente conta

- **Produto e instalação:** [runtime Nexus](../nexus/README.md) e [ponto de situação por fase](../nexus/docs/PONTO-DE-SITUACAO.md). São referências de trabalho; uma afirmação de PASS exige o commit, ambiente e logs correspondentes.
- **Estado atual da integração:** consultar a [PR #87](https://github.com/PAPACREATOR/cerebro-parvo-/pull/87) e a [coordenação #62](https://github.com/PAPACREATOR/cerebro-parvo-/issues/62). Em 15/10/2026, a PR #87 permanece Draft e não integrada; este parágrafo é um retrato datado, não um monitor de CI.
- **Constituição e papéis:** [Constituição](architecture/CEREBRO_CONSTITUTION.md), [arquitetura](architecture/CEREBRO_ARCHITECTURE.md) e [decisões](architecture/DECISIONS.md). A pessoa mantém a autoridade; IA, Wikipédia, OpenNotebook e moldes não autorizam operações ou promoção a Canonical.
- **Plano versus resultado:** [planeamento](planning/) e contratos descrevem critérios; não provam instalação, E2E nem aceitação física.
- **Evidência histórica:** [genealogia](GENEALOGIA.md), [inventário histórico](INVENTARIO-HISTORICO.md), [arquivo de evolução](../historico/) e [relatórios do Nexus](../nexus/docs/). Não substituir o estado real por documentos com títulos como «final» ou «PASS» datados de outra fase.

## Duplicação documental comprovada em 15/10/2026

A [issue #38](https://github.com/PAPACREATOR/cerebro-parvo-/issues/38) regista **seis pares de ficheiros byte-a-byte idênticos** (Git blob igual) entre `arquivo/` e as fontes abaixo. Estas fontes são preferidas como caminhos de leitura; **não foi removido nenhum original**:

| Fonte de leitura | Cópia exata em arquivo |
| --- | --- |
| [Arquitetura](architecture/CEREBRO_ARCHITECTURE.md) | `arquivo/CEREBRO_ARCHITECTURE.md` |
| [Compatibilidade](planning/COMPATIBILITY-MATRIX.md) | `arquivo/COMPATIBILITY-MATRIX.md` |
| [Implementação](planning/IMPLEMENTATION_PLAN.md) | `arquivo/IMPLEMENTATION_PLAN.md` |
| [Instalação](planning/INSTALLATION_PLAN.md) | `arquivo/INSTALLATION_PLAN.md` |
| [Fluxo da equipa](internal/TEAM_WORKFLOW.md) | `arquivo/TEAM_WORKFLOW.md` |
| [Testes fornecidos](../auditoria/testes-fornecidos-2026-09-27.txt) | `arquivo/auditoria/testes-fornecidos-2026-09-27.txt` |

A igualdade do conteúdo não prova que os caminhos arquivados não tenham consumidores externos ou referências ainda ativas. Qualquer remoção exige verificação de backlinks e aprovação explícita. A classificação por famílias e o inventário da antiga [PR #49](https://github.com/PAPACREATOR/cerebro-parvo-/pull/49), bem como a auditoria da [PR #46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46), continuam recuperáveis no Git: são trabalho de época, não devem ser integrados indiscriminadamente na `main` atual.

**Regra de reconciliação:** primeiro ler a fonte vigente, depois conferir o código e os checks do mesmo SHA. O histórico é preservado, não reexecutado nem promovido automaticamente.
