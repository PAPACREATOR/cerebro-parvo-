# Fase 1 — Inventário e reconciliação documental (2026-10-10)

Estado: EM CURSO. Não declarar fechado sem inventário completo dos artefactos publicados e revisão das divergências. Escopo exclusivo: documentação; sem execução Windows ou alterações Kernel.

## Documentos verificados diretamente na branch principal
| Ficheiro | Constatação |
| --- | --- |
| AGENTS.md | Descrevia Activepieces como executor; foi anotado na PR #46 como referência histórica. |
| CEREBRO_CONSTITUTION.md | Ainda descreve Activepieces como plataforma por defeito no texto preservado; há nota de vigência na PR #46. |
| CEREBRO_ARCHITECTURE.md | Desenha Activepieces no centro; anotado como desenho histórico. |
| IMPLEMENTATION_PLAN.md | Chamava Activepieces e Memory Provider de dois blocos nucleares; marcado histórico na PR #46. |
| DECISIONS.md | Regista a decisão posterior Nexus Minimal de 30/09 e considera Activepieces superado como requisito. |
| STATUS.md | Regista Activepieces fora do Core e que o E2E completo continua pendente. |
| docs/RECONCILIACAO.md | Reconciliação datada de 27/09, anterior à decisão de 30/09; não pode ser apresentada isoladamente como estado atual. |
| docs/INVENTARIO-HISTORICO.md | Declara preservar 35 blobs de 24/09; não prova cópia do PC atual. |
| auditoria/CONSOLIDACAO-2026-10-10.md | Plano, limites, crédito a Hrvoje Abraham e critérios Sandy. |

## Política documental
- Documentos constitucionais, decisões, contratos, testes e evidências são conservados; não reescrever o passado como se tivesse sido outra decisão.
- Separar explicitamente «vigente», «histórico», «experimental» e «pendente de validação».
- Uma nota em Markdown não prova remoção de runtime ou integração funcional.
- Atribuir a Hrvoje Abraham o que efetivamente desenvolveu no Sandy, sem o designar colaborador Nexus sem aceitação explícita.
- Evitar tocar em ficheiros de código ou PRs concorrentes do Codex/Work.

## Fecho da Fase 1 — verificação obrigatória
- [ ] Enumerar árvore completa e branches relevantes com SHA.
- [ ] Verificar links documentais para documentos ausentes e referências locais não publicadas.
- [ ] Levantar documentos operacionais duplicados/contraditórios e produzir índice inequívoco de vigência.
- [ ] Confirmar com o Codex que a cópia local está publicada e depois comparar manifestos/hashes de documentos.
- [ ] Verificar que não foram incluídos segredos, informação pessoal ou grandes binários inadequados num repositório público.
- [ ] Rever os resultados antes de qualquer merge.

## Fora de âmbito nesta fase
- Cópia local para GitHub: trabalho atribuído ao Codex, dependente de validação de hashes e completude.
- Activepieces: nenhuma remoção de runtime até análise de dependências e testes.
- Testes Windows E2E: ainda não executados por esta frente documental.
- **Sandy: integração suspensa por decisão humana de 2026-10-10.** O crédito histórico ao autor permanece; não reabrir sem nova decisão explícita.

Esta fase limita-se à reconciliação documental e à organização rastreável no GitHub.
