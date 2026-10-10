# Fase 1 — Inventário e reconciliação documental (2026-10-10)

Estado: EM CURSO. Não declarar fechado sem inventário completo dos artefactos publicados e revisão das divergências. Escopo exclusivo: documentação; sem execução Windows ou alterações Kernel.

## Documentos verificados diretamente na branch principal
| Ficheiro | Constatação |
| --- | --- |
| AGENTS.md | Descreve Activepieces como executor na `main` antiga; a reconciliação do ficheiro é da PR #41, sem edição direta nesta PR #46. |
| CEREBRO_CONSTITUTION.md | A `main` antiga descreve Activepieces como plataforma por defeito; manter inalterado nesta PR #46 para evitar conflito com PR #41. |
| CEREBRO_ARCHITECTURE.md | Desenha Activepieces no centro na `main` antiga; verificar a redação revista na PR #41. |
| IMPLEMENTATION_PLAN.md | Na `main` antiga prescreve Activepieces e Memory Provider; a PR #41 propõe a atualização, sem sobreposição nesta PR #46. |
| DECISIONS.md | Regista a decisão posterior Nexus Minimal de 30/09 e considera Activepieces superado como requisito. |
| STATUS.md | Regista Activepieces fora do Core e que o E2E completo continua pendente. |
| docs/RECONCILIACAO.md | Reconciliação datada de 27/09, anterior à decisão de 30/09; não pode ser apresentada isoladamente como estado atual. |
| docs/INVENTARIO-HISTORICO.md | Declara preservar 35 blobs de 24/09; não prova cópia do PC atual. |
| auditoria/CONSOLIDACAO-2026-10-10.md | Plano, limites, crédito a Hrvoje Abraham e critérios Sandy. |

## Resultado confirmado deste ciclo

- [Índice de vigência documental](INDICE-DE-VIGENCIA-DOCUMENTAL-2026-10-10.md) criado com a classificação de 16 documentos efetivamente lidos. É **parcial** e não certifica o espelho do PC.
- Inventário técnico da branch `main`: 208 entradas, incluindo 177 ficheiros (identificadores Git por ficheiro); mais 49 branches com os respetivos commit SHA. São fotografias do GitHub, não prova de cópia do Windows.
- Decisão humana: Sandy fora do trabalho ativo; integração suspensa, crédito histórico mantido.
- PR #46 continua Draft e isolada; depois da reversão preventiva das quatro alterações aos documentos de raiz, contém **apenas ficheiros em `auditoria/`**. Código e documentos operacionais foram preservados.

## Evidências adicionais de 2026-10-10

- [Auditoria de ligações/duplicações](AUDITORIA-LINKS-DUPLICADOS-2026-10-10.md): 100 ficheiros Markdown lidos, 1 referência histórica não materializada, 2 pares de blobs Git idênticos em versões distintas — nada eliminado.
- PR #41 é a frente de navegação e atualizações de README/STATUS/DECISIONS; a PR #46 mantém-se isolada e não edita essas superfícies.

## Reconciliação entre branches e navegação

- [Comparação de branches](COMPARACAO-BRANCHES-2026-10-10.md): `main` tem 177 ficheiros; PR #41 possui 374 e PR #45 possui 372 (snapshots separados). A branch antiga `pc-full-mirror-20261004` tem 175 ficheiros e **não comprova** a cópia atual do Windows.
- Documentação nova da PR #41: 8 ficheiros de navegação analisados, 14 referências relativas verificadas, zero destinos em falta (método estático); ver [auditoria de links](AUDITORIA-LINKS-DUPLICADOS-2026-10-10.md).
- Não consolidar as alterações da PR #41 na PR #46, nem declarar os 374 ficheiros parte da `main`.

- [Auditoria completa dos links Markdown da PR #41](PR41-AUDITORIA-LIGACOES-2026-10-10.md): 149/149 documentos, 168 referências relativas, 11 destinos em falta; sem tocar na branch dessa PR.

## Fecho do subciclo — coerência documental entre PRs

- PR #41, SHA `46c6b6722028017b5c174986128be4a151588ae7`: **149/149 Markdown lidos**; 168 ligações locais relativas verificadas, 11 sem destino; ver [auditoria PR #41](PR41-AUDITORIA-LIGACOES-2026-10-10.md).
- PR #45, SHA `66027af7f2ea084bc62d85b840d1fc3113e60a97`: 142 documentos Markdown, dos quais 137 têm blob idêntico à PR #41, quatro partilhados diferem, um exclusivo; nos cinco exclusivos/alterados, 11 ligações relativas verificadas, zero sem destino; ver [comparação](COMPARACAO-BRANCHES-2026-10-10.md).
- [Manifesto Git dos documentos Markdown das três refs](MANIFESTO-DOCUMENTOS-BRANCHES-2026-10-10.json) guardado por caminho, tamanho e blob SHA. **SHA Git não equivale automaticamente ao SHA-256 dos ficheiros em `C:\Nexus`.**
- A PR #46 altera exclusivamente `auditoria/`; os quatro documentos de raiz antes modificados nesta branch foram restaurados à `main` sem alterar a PR #41.
- **Pendente:** auditoria de fontes locais, comparação de hashes após entrega do Codex, links externos/âncoras, dados pessoais/segredos e escolha do HEAD definitivo. Não aprovar a consolidação antes dessas verificações.

## Política documental
- Documentos constitucionais, decisões, contratos, testes e evidências são conservados; não reescrever o passado como se tivesse sido outra decisão.
- Separar explicitamente «vigente», «histórico», «experimental» e «pendente de validação».
- Uma nota em Markdown não prova remoção de runtime ou integração funcional.
- Atribuir a Hrvoje Abraham o que efetivamente desenvolveu no Sandy, sem o designar colaborador Nexus sem aceitação explícita.
- Evitar tocar em ficheiros de código ou PRs concorrentes do Codex/Work.

## Fecho da Fase 1 — verificação obrigatória
- [x] Enumerar a árvore publicada de `main` e as branches com SHA no snapshot de 2026-10-10: 208 entradas (177 ficheiros), 49 branches. Isto não cobre ficheiros locais nem garante que branches isoladas tenham sido integradas. Ver [manifesto da árvore](INVENTARIO-GITHUB-MAIN-2026-10-10.json) e [manifesto das branches](BRANCHES-GITHUB-2026-10-10.json).
- [x] Verificar estaticamente os links Markdown locais nos **100 documentos** da branch `main`: 99 referências internas encontradas; uma referência histórica não materializada em `historico/repositorio-2026-09-24/README.md` para `MEMORIA-DE-TRABALHO.md`. Links externos/âncoras e outras sintaxes ainda por validar. Ver [auditoria](AUDITORIA-LINKS-DUPLICADOS-2026-10-10.md).
- [ ] Levantar documentos operacionais duplicados/contraditórios e produzir índice inequívoco de vigência. Existe [índice parcial](INDICE-DE-VIGENCIA-DOCUMENTAL-2026-10-10.md). A PR #41 apresenta decisões mais recentes sobre Conductor/MCP do que a `main`, sem merge confirmado; não sobrepor edições.
- [ ] Confirmar com o Codex que a cópia local está publicada e depois comparar manifestos/hashes de documentos.
- [ ] Verificar que não foram incluídos segredos, informação pessoal ou grandes binários inadequados num repositório público.
- [ ] Rever os resultados antes de qualquer merge.

## Fora de âmbito nesta fase
- Cópia local para GitHub: trabalho atribuído ao Codex, dependente de validação de hashes e completude.
- Activepieces: nenhuma remoção de runtime até análise de dependências e testes.
- Testes Windows E2E: ainda não executados por esta frente documental.
- **Sandy: integração suspensa por decisão humana de 2026-10-10.** O crédito histórico ao autor permanece; não reabrir sem nova decisão explícita.

Esta fase limita-se à reconciliação documental e à organização rastreável no GitHub.
