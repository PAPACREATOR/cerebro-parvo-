# Nexus — reconciliação do estado no GitHub (11-10-2026)

> Relatório datado da triagem GitHub. A fonte operacional que se deve manter atualizada continua a ser [PONTO-DE-SITUACAO.md](PONTO-DE-SITUACAO.md). Este documento não é outra memória, outro plano de execução nem um handoff.

## Produto oficial

- Repositório: `PAPACREATOR/cerebro-parvo-`; **um só runtime autoritativo no `main`**.
- HEAD de referência na auditoria: [`fc3c48a5cb9a594ae4de0fc790fd586147d91de4`](https://github.com/PAPACREATOR/cerebro-parvo-/commit/fc3c48a5cb9a594ae4de0fc790fd586147d91de4).
- PR [#50](https://github.com/PAPACREATOR/cerebro-parvo-/pull/50): Folha Única, Writer/Sandy e dois gates humanos distintos; #51: convergência do candidato para `main`; #53: seleção determinística das dez capacidades existentes; [#55](https://github.com/PAPACREATOR/cerebro-parvo-/pull/55): gateway Node opcional subordinado ao Python, FTS5 de consulta através do Host e Creative/Canonical separados.
- A PR #55 teve **8 de 8 workflows SUCCESS no mesmo HEAD candidato** `7c217b3c2fdb24e9e75997d93191ce175a03aead`, antes do merge. Não equivalem a certificação de todo o software no PC físico.
- Runtime: Folha → API Python → confirmação pré-execução → Host → runner direto ou Writer/Sandy na fronteira Windows → Store/Creative → revisão e **aprovação humana explícita** → Canonical. MCP é transporte opcional de ferramentas externas e tem regressões reais de protocolo; não é outra autoridade.
- Índice FTS5 derivado: o modo normal pesquisa só Canonical; Creative é consultável apenas quando pedido explicitamente. Nenhuma consulta concede aprovação nem promoção.

## Organização das PRs e trabalho preservado

- Candidatos cujos commits são antepassados do `main`: #23, #32, #43 e #45 **fechados como substituídos**, depois de comparação Git (`behind_by=0`). Commits, branches e evidência intactos.
- Propostas paralelas incompatíveis com o caminho mínimo: #52 (segundo roteador `tool_router.py` quando #53 usa `capability_router.py`) e #34 (documentação sobre #31/#32, com remoções de caminhos ativos) **fechadas sem merge**. Recuperar apenas melhorias comprovadas por testes, nunca transplantar cegamente.
- PRs históricas #30 e #31: testes de persistência do antigo `implementacao/` preservados e PRs encerradas **sem merge**; transpor só garantias demonstradamente em falta no runtime `nexus/`, pela issue #4.
- Documentação ativa: [PR #54](https://github.com/PAPACREATOR/cerebro-parvo-/pull/54) ainda em Draft; precisa de reconciliação da sua base com #55 antes de qualquer integração. As PRs #41/#49 e a #46 contêm trabalho documental/evidência a comparar sem apagar genealogia; não presumir conteúdo aprovado por estar numa branch.
- Dependabot #24/#27 propõe versões/SHA de actions diferentes das atualmente fixadas e #25 propõe `pytest==9.1.1` em `requirements-auditoria.txt`, que ainda está em `8.3.5`. **Não estão resolvidas só porque o Nexus usa pytest 9.1.1 noutro ficheiro.** Avaliar pin, segurança e testes antes de integrar.
- Laboratórios de testes e integração (#44, #47), inventário/clones (#48), instalação/provisioning (#29) e aceitação física (#28) não são prova de release e permanecem isolados até revisão.

## Issues — não confundir encerramento com resolução funcional

- [#33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) fechada como **substituída** pela convergência. Não significa produto integralmente concluído.
- Continuam abertas #3 (IMP-001 receção), #4 (G10/IMP-019 e recuperação), #35 (ajuda pública), #36 (Writer real/LPAC, prova final), #37 (linguagem PT-PT adversarial), #38 (classificação documental completa), #39 (revisão independente), #42 (OpenNotebook real e microprocessos).
- Nenhum comentário externo com «Closes #...» conta como contribuição aceite sem PR, commit ou patch reprodutível. Não fechar #36 apenas por PASS Writer num SHA antigo: repetir Writer real no candidato correto com os gates aplicáveis.

## Limitações verificadas

- CI GitHub `PASS` ≠ instalação no PC físico, GPU, criação de podcast/vídeo/áudio, Writer editorial completo ou resistência a perda súbita de energia.
- A execução interna das dez capacidades é atualmente Python direto governado pelo Host; não instalar um segundo orquestrador/MCP interno só para aumentar a contagem de ferramentas.
- Sem alterações a Kernel, Host, Store, contratos, parser, sandbox ou manifesto nesta organização documental.
- Creative nunca é promovido automaticamente. Canonical **exige decisão humana específica e válida**.

## Critério de próximos fechos

Para cada issue: comportamento exigido → teste direto e inverso com recusas → log/SHA/ambiente → validação independente quando aplicável → documentação e fecho. Preservar as evidências FAIL e históricos mesmo depois do encerramento.
