# Reconciliação de bancadas — Nexus, 17-10-2026

## Fonte de verdade

A main integrada pela PR #93 é 59e80836baaea4a000ea375483315fce5bb60a7a. O candidato 13197a7bd37affa1e9a711de54399dfa26886f55 tinha 48/48 checks SUCCESS. Isto não valida a instalação do proprietário nem upstream multimédia físico.

O inventário inicial do repositório principal encontrou zero PRs abertas, zero issues abertas e 93 referências de branches (antes desta bancada de manutenção). Há 74 PRs encerradas na primeira página da API, das quais 32 merged e 42 encerradas sem merge. Um fecho de issue por transferência de requisitos não prova implementação completa.

## Classificação seletiva, sem apagar trabalho exclusivo

- Contidas inteiramente na main (ahead_by=0 no exame): test/execute-learn-two-real-tools-20261016, lab/windows-full-install-20261006, lab/behavioral-sessions-matrix-20261014, lab/folha-shell-bidirectional-e2e-20261014, lab/varied-real-folha-family-cases-20261014, integration-convergence-20261004, lab/open-notebook-isolation-20261009 e test/open-notebook-upstream-http-schema-20261013. São candidatas à remoção das refs depois de verificar dependências/uso em CI; os commits e PRs permanecem no histórico GitHub.
- Contribuição isolada útil: lab/opennotebook-m6-normal-gate-20261012 acrescenta apenas o ficheiro de testes nexus/tests/test_open_notebook_normal_folha_gate.py, sem runtime novo. Integrado seletivamente nesta bancada; exige CI Windows e Linux antes de qualquer merge. Peer OpenNotebook sintético, portanto não prova backend real.
- Divergentes com risco de substituir componentes: integration/generic-tool-routing-20261010 (inclui host.py), lab/molde-diagnostic-20261013 (inclui app.py e integrity.json), work/core-regression-20261007 (inclui store.py e persistência). Não fundir branches completas. Comparar testes e contratos pequenos; proteger Host, Kernel, Store, isolamento e Human Gate.
- Históricos documentais a consultar, mas não misturar automaticamente: docs/organizacao-2026-10-12, docs/status-reconciliation-20261013, docs/generic-flow-phase1-20261010.

Não foi executada eliminação de branches ou de repositórios; não confundir esta auditoria com limpeza concluída. Se não estiver disponível uma operação de remoção de referências GitHub com salvaguardas, deixar as refs intactas.

## Testes reais e integração no Windows

O script nexus/windows/sync-nexus-code.ps1 já faz sincronização do checkout oficial existente por fast-forward, recusando origin incorreto e mudanças locais. Esta bancada reforça-o com testes funcionais num par de repositórios Git descartáveis: ficheiro local não registado, mudança de SHA remoto não autorizada e origin diferente. Não instala software, não escreve no PC do utilizador e não substitui o script.

O script TESTAR-NEXUS-REAL-BIDIRECIONAL.bat já está na main; recolhe relatórios de testes nativos, sem afirmar que OpenNotebook/modelo ou WAV/MP4 reais foram produzidos. O provisionamento protegido continua bloqueado; atualização real do PC necessita da etapa própria.

## Estudo paralelo de ferramentas semelhantes

Critério de adoção: existe lacuna reproduzível? O Nexus já faz? A alternativa é mais simples e segura no PC-alvo? Consegue passar teste adversarial e rollback? Há compatibilidade de licenças? Se falhar qualquer critério, documentar sem integrar.

- OpenAdapt / openadapt-flow: confirmar efeito externo por read-back após gravar e bloquear o segundo passo se o primeiro só declarou sucesso; útil como matriz de testes, sem incorporar UI/agent/LLM. Fonte: https://github.com/OpenAdaptAI/openadapt-flow
- Microsoft UFO2: preferir UI Automation/Win32/COM a cliques frágeis onde adaptador nativo não existe. Estudar isoladamente sob sandbox e mínimo privilégio; não importar HostAgent/AppAgents nem autoridade LLM. Fonte: https://github.com/microsoft/UFO
- Dagu: comparar estado de tarefas, retry controlado e intervenção humana; rejeitar duplicação do Shell/Store como orquestrador externo. Fonte: https://github.com/dagucloud/dagu
- OpenWOP: extrair casos de idempotency key, interruption/replay e version pinning como testes de contrato, sem novo servidor ou protocolo obrigatório. Fonte: https://github.com/openwop/openwop
- Temporal: observar a distinção entre reexecução da lógica e efeitos externos. Um efeito confirmado ou de resultado desconhecido nunca se repete apenas porque a resposta se perdeu. Fonte: https://docs.temporal.io/tasks

Decisão vigente: estudo e adaptação por blocos; sem clonagem/importação de runtimes, sem dependência de IA permanente, sem reabrir arquitetura e sem atribuir autoridade ao molde. O próximo alvo são testes de efeito observável, idempotência de pedidos compostos e recovery sem replay.
