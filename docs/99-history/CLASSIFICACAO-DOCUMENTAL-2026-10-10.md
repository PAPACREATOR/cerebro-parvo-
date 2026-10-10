# Catálogo e classificação de documentos — 10/10/2026

**Objetivo:** manter uma árvore legível sem destruir proveniência, quebrar links ou confundir documentos de época com o runtime do candidato atual. Classificação de **leitura documental**, não mudança física dos ficheiros. Base da leitura: PR #49, branch documental, e PR #45, commit `66027af7f2ea084bc62d85b840d1fc3113e60a97`.

## Vocabulário

- **REGRA:** invariantes e autoridade humana; não é descrição de testes.
- **ATIVO/ÍNDICE:** ponto de entrada ou orientação vigente; tem de apontar para evidência datada.
- **PONTE:** documento legado cujo caminho é mantido para compatibilidade; a sua leitura exige o contexto posterior.
- **CONTRATO:** comportamento pretendido e critérios de aceitação; não significa capacidade aprovada.
- **RELATÓRIO:** resultado de um teste numa data/ambiente/SHA; não é verdade intemporal.
- **HISTÓRICO:** versão substituída/estudo/laboratório que se conserva integralmente.
- **EVIDÊNCIA:** logs, matrizes, hashes e ligação a PR/CI, sempre com limitação.

## Mapa prático

| Família e caminhos | Classe | Regra para quem lê |
| --- | --- | --- |
| [`CEREBRO_CONSTITUTION.md`](../../CEREBRO_CONSTITUTION.md), [`nexus/laws/CONSTITUTION.md`](../../nexus/laws/CONSTITUTION.md) | REGRA (com versões próprias) | Usar como limites; qualquer divergência exige decisão humana e reconciliação, não síntese silenciosa |
| [`README.md`](../../README.md), [`AGENTS.md`](../../AGENTS.md), [`docs/README.md`](../README.md) | ATIVO/ÍNDICE | Orientação e entrada; sempre conferir HEAD |
| [`STATUS.md`](../../STATUS.md), [`DECISIONS.md`](../../DECISIONS.md), [`CEREBRO_ARCHITECTURE.md`](../../CEREBRO_ARCHITECTURE.md), [`IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md) | ATIVO/PONTE | Estado e arquitetura misturam épocas; leitura corrente depende da [matriz por SHA](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) |
| [`docs/10-current/`](../10-current/README.md), [`docs/20-architecture/`](../20-architecture/MINIMUM-CORE.md), [`docs/40-decisions/`](../40-decisions/README.md), [`docs/60-evidence/`](../60-evidence/README.md) | ATIVO/ÍNDICE e ADR | Novos guias de leitura; não são novos módulos do produto |
| [`nexus/docs/PONTO-DE-SITUACAO.md`](../../nexus/docs/PONTO-DE-SITUACAO.md) | PONTE + RELATÓRIO ACUMULADO | Ler por data/SHA; a abertura de 08/10 não descreve, sozinha, a PR #45 posterior |
| [`nexus/docs/F001.md`](../../nexus/docs/F001.md) até [`F013-PROVENIENCIA-INVERSA.md`](../../nexus/docs/F013-PROVENIENCIA-INVERSA.md) | CONTRATO + RELATÓRIOS por fase | Cada F00x tem alcance próprio; não somar PASS diferentes |
| [`nexus/docs/CAPABILITY-WRITER-EDITORIAL.md`](../../nexus/docs/CAPABILITY-WRITER-EDITORIAL.md), [`CONTRATO-LAB-WIKI-KERNEL-FLOWS.md`](../../nexus/docs/CONTRATO-LAB-WIKI-KERNEL-FLOWS.md), [`CONTRATO-ISOLAMENTO-2026-10-05.md`](../../nexus/docs/CONTRATO-ISOLAMENTO-2026-10-05.md) | CONTRATO | Indicam gates, não aceitação física |
| [`nexus/docs/RELATORIO-*`](../../nexus/docs/README.md), [`TESTES-ADVERSARIAIS.md`](../../nexus/docs/TESTES-ADVERSARIAIS.md), [`WINDOWS-STACK-COMPATIBILITY-2026-10-07.md`](../../nexus/docs/WINDOWS-STACK-COMPATIBILITY-2026-10-07.md) | RELATÓRIO/EVIDÊNCIA | Resultado datado por ambiente; alguns relatórios são de laboratório ou simulação |
| [`auditoria/`](../../auditoria/) e [PR #46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46) | EVIDÊNCIA | Inventários e reconciliações; não validam o PC físico nem segredos completos |
| [`docs/PROJETO-FINAL-AUDITADO-2026-09-28.md`](../PROJETO-FINAL-AUDITADO-2026-09-28.md), [`docs/baseline/`](../baseline/), [`docs/CONTRATOS-IMP.md`](../CONTRATOS-IMP.md) | HISTÓRICO/CONTRATOS | Fonte de decisões de setembro; «final» no título não significa release de outubro |
| [`historico/repositorio-2026-09-24/`](../../historico/repositorio-2026-09-24/), [`historico/evolucao-2026-10-04/`](../../historico/evolucao-2026-10-04/) | HISTÓRICO | Imutável nesta revisão; consultar genealogia e motivos das substituições |
| [`implementacao/`](../../implementacao/) | HISTÓRICO/CÓDIGO LEGADO (só leitura aqui) | Não é o runtime `nexus/`; não converter PASS da PR #31 em aceitação do produto atual |
| [PR #48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48) | EVIDÊNCIA DE CÓPIA LINUX | Sem prova de inventário/limpeza do PC |

## Lógica por assunto

- **Quem chega de fora:** [começar](../00-start-here/README.md) → [estado](../10-current/README.md) → [arquitetura](../20-architecture/MINIMUM-CORE.md) → [contribuição](../30-help/README.md).
- **Quem quer saber «o que funciona»:** [código ↔ documentação](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) → [matriz de PRs](../60-evidence/MATRIZ-PRS-2026-10-10.md) → logs no SHA.
- **Quem quer compreender «porque mudámos»:** [ADRs](../40-decisions/README.md) → [decisões superadas](DECISOES-SUPERADAS-E-PORQUE.md) → [cronologia](LINHA-DO-TEMPO-2026-09-22-A-2026-10-10.md) → documento de época.
- **Quem procura contratos técnicos:** [índice `nexus/docs/`](../../nexus/docs/README.md) → contrato e relatório da capacidade.
- **Quem verifica a veracidade de PASS:** [protocolo de prova](../60-evidence/PROTOCOLO-VERIFICACAO-DOCUMENTAL.md) → workflow/execução no SHA → alcance e exclusões.

## Decisão de arrumação

**Não mover nem eliminar documentação original nesta fase.** Cada mudança física exigiria inventário antigo→novo, lista de backlinks, preservação de hashes/evidência, verificação de URLs relativos, e revisão de utilizadores externos. Índices por secção e pontes são mais reversíveis e não alteram testes nem o runtime. Esta escolha foi explicitada na [PR #49](https://github.com/PAPACREATOR/cerebro-parvo-/pull/49).

## Duplicação

Não chamar «duplicado» a dois relatórios com números iguais mas SHA/plataforma diferentes. Duplicação eliminável só após igualdade de conteúdo/semântica e confirmação de ausência de contexto ou links exclusivos. Esta classificação **não autoriza eliminação automática**.
