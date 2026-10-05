# Nexus — ponto de situação atual

Este é o único documento de estado operacional corrente em `nexus/docs`.
Estados antigos, filas, handoffs e quadros temporários foram removidos da árvore ativa; continuam recuperáveis pelo histórico Git e pelos PRs/comentários.

## Fonte de verdade operacional

- PR ativa: **#23 — CURRENT BASELINE**.
- Branch de continuação: `lab-open-notebook-avatar-20261004`.
- Kernel/Host/Store são a autoridade do sistema.
- MCP é transporte determinístico.
- OpenNotebook, LanguageTool, LibreOffice, ACE-Step, Forge e restantes integrações são ferramentas externas.
- Creative precede Canonical.
- Promoção para Canonical exige decisão humana explícita.
- Tiny/IA não recebe autoridade de sistema.
- Duplicação exata é a única base para eliminação automática; semântica/similaridade apenas sinaliza revisão.

## Correção e 10.000 ataques — implementação em validação, 05-10-2026

Pedido humano: resolver e testar 10.000 casos. Contrato do microprocesso, dono Host (sem alterar M1–M14): lançar somente um comando selecionado pelo Host, com inputs delimitados, identidade Windows de tarefa, direitos de leitura dos executáveis e escrita no trabalho, sem direitos sobre Kernel/cofres/dados externos nem capacidades de rede. Criar suspenso; verificar token AppContainer, SID e associação ao Job antes de retomar. O Job termina descendentes e impõe limites. Erros nativos não autorizam fallback. ACLs da identidade de tarefa são revogadas na limpeza sem restaurar/destruir ACLs humanas completas.

USE/ADAPT: mecanismos oficiais AppContainer/SECURITY_CAPABILITIES, DACL e Job Object, chamados por ctypes; sem serviço/conta/administração global novos. A fronteira nativa começa isolada e a ligação ao Host/MCP é feita apenas no candidato draft; não promover uma baseline sem os gates completos. Avatar/instaladores externos são um âmbito separado que também precisa de portão nativo. O teste executa 10.000 operações reais de ficheiros, leitura dos dois cofres sintéticos, descendente, controlo de escrita permitida e tentativa de ligação a um socket loopback realmente disponível. ERROR/timeout/não execução não contam como DENIED. Fontes: [Microsoft AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer), [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).

Estado desta etapa: **IMPLEMENTADO / LIGADO AO HOST/MCP NO CANDIDATO / TESTES WINDOWS EM VALIDAÇÃO / SEM RELEASE**. O gate Host publicado continua obrigatório e vermelho; não retirar nem mascarar o FAIL anterior. A aceitação exige comprovar fronteira nativa, gate do Host real, retorno/reinício e regressão no mesmo código. PC de Pedro não foi alterado.

Primeiro ensaio nativo, commit efc5b0e, [run 37364869364](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37364869364): 1 FAIL / 1 PASS. O SID derivado sem perfil não permitiu CreateProcessW (erro 2); os 10.000 ataques não executaram. Corrigida a preparação para perfil efémero por tarefa, com acesso da ferramenta ao armazenamento desse perfil explicitamente negado e limpeza no fim. A pasta de trabalho continua a ser o único destino de filesystem atribuído. Isto não cria uma conta Windows nem dá direitos globais à ferramenta. Repetição obrigatória, ainda sem PASS.

Correção de autoridade: Host.authorize agora exige str ASCII antes de hmac.compare_digest; sessões Unicode falsas passam a Blocked. O método real extraído por AST passou controlo válido + 10.000 sessões inválidas localmente; é prova de componente, não importação completa do Host. Novo test_authority_10000.py testa o Host/Store completo em quatro famílias de 2.500 inputs (sessões, tickets humanos forjados, autoridade em resultados e processos não registados), com snapshots de dados invariantes. Manifesto atualizado para a alteração revista. CI pendente. Os 40.000 inputs antigos preparados noutra cópia continuam NOT RUN; não são estes testes.

O gate Windows passa a testar Windows Server 2022 e 2025 separadamente, sem fail-fast, conservando artefactos por plataforma e os critérios do gate Host. O job 2025 do commit f5596d4 ainda estava em fila sem runner na última consulta; fila não é PASS nem FAIL do código.

Commit 7aed704, [run 37367782434](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37367782434): **10.000 inputs de autoridade PASS em cada Windows** (4 funções pytest; 2.500 casos por função), 1,03 s em Server 2022 e 0,85 s em Server 2025. A fronteira nativa continuou 1 FAIL / 1 PASS por OS: CreateProcessW erro 203 (variável de ambiente não encontrada), antes dos ataques. Nova preparação acrescenta USERPROFILE/APPDATA/LOCALAPPDATA/HOME com valores da área de tarefa, sem herdar o perfil humano. A hipótese de ambiente só passa a causa resolvida após repetição. Gate Host ainda 22 acessos proibidos permitidos; integração continua pendente.

Commit c91ba66, [run 37368326605](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37368326605): o ambiente corrigiu o lançamento; as 10.000 operações realmente executaram. Resultado do teste ainda FAIL: 6.000 recusas Win32 e 4.000 PermissionError sem winerror, classificadas como ERROR; escrita permitida funcionou, rede deu timeout. Nova verificação aceita apenas ACCESS_DENIED Win32 ou errno EACCES/EPERM sem winerror, conserva canários e exige diagnóstico nativo de capacidade de rede em falta, com socket disponível antes/depois. Timeout isolado continua ERROR. Acrescentado alvo sintético com ALL APPLICATION PACKAGES e LPAC opt-out para que esse direito partilhado não alargue a tarefa. A criação exige sucesso do atributo oficial LPAC; token AppContainer/SID/Job são verificados antes de retomar e o efeito LPAC é testado contra o alvo ALL APPLICATION PACKAGES. Resultado pendente neste novo SHA.

Commit adb64f2, [run 37370018066](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37370018066), Server 2022: FAIL antes de retomar. GetTokenInformation classe 46 deu ERROR_INVALID_PARAMETER (87). O header contém a classe, mas isso não prova suporte Win32; removida essa consulta como pré-condição. Mantidos atributo de criação LPAC obrigatório, verificação AppContainer/SID/Job e teste comportamental do direito AAP. Nenhum ataque desse job conta como executado. Repetição pendente.

Integração preparada no candidato: Host lança runner via fronteira nativa; trabalho é snapshot numa pasta efémera separada de Store, com Store explicitamente negado à identidade da tarefa. Só Host regista estado, stdout e artefacto PDF delimitado/hash verificado após terminar o Job. Runner direto também confina. MCP direto usa stdio nativo; o filho de runner herda identidade/Job sem autorização por variável de ambiente. MCP só aceita input.bin da pasta atribuída. Java/LibreOffice diretos recusam execução fora da fronteira; descendentes mantêm os limites.

OpenNotebook: a chamada HTTP fixa e delimitada é feita pelo Host antes da validação isolada; só output/model_id/transformation_id são copiados, sem palavra-passe, sessão ou capacidade de rede. Health ACE/Forge usa o mesmo princípio para GETs fixos sem mutação. Recuperação conserva EXECUTING antes da chamada e usa resultado durável sem repetir ferramentas nem criar aprovação humana. Leitores state/list_runs passam a usar o lock dos escritores, para eliminar a corrida Windows read/os.replace; novo stress faz 500 substituições com quatro leitores (4.000 snapshots + listas), sem promover. A causa de todo PermissionError histórico não é presumida resolvida sem repetir.

O gate de 22 alvos foi adaptado apenas ao novo ponto de lançamento/pasta de trabalho: injeta o mesmo worker hostil, mantém APIs/DACL/token/Job reais, lê as observações do stdout durável e conserva os 24 critérios. Não é substituído por mocks de proteção. Duplos unitários de output/timeout e sentinelas de não reexecução apontam ao novo launcher, separados do gate nativo. Manifesto/fingerprint inclui windows_sandbox.py.

NOT RUN/PENDENTE: resultados do CI deste conjunto, perfil de crash/limpeza, instaladores/launchers externos e confinamento avatar/modelo/GPU físicos. Nenhum desses limites é substituído pelos 10.000 testes de autoridade.

Commit f01ca4a, [run 37370540374](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37370540374), Server 2022: criação/token/Job passou, mas Python terminou com 0xC0000022 (ACCESS_DENIED) sem output, antes do payload. Nenhuma operação desse ensaio conta como PASS. Implementação testa registryRead (capacidade oficial só de leitura) e acesso RO do SID aos DLLs System32, usados pelo arranque LPAC; não dá rede/escrita/COM. A verificação de token exige exatamente registryRead e recusa capacidades adicionais. Acrescentado canário de escrita no registo HKCU sintético, com original invariável. A hipótese de arranque só é resolvida depois da repetição.

## Revisão do código e segurança Windows — 05-10-2026

SHA executável revisto: `dcef003f7c3e93ed8bdfe1730ce5870f1b818e09`. A presente revisão documental não altera esse runtime. Pedido de Pedro: conferir o código real e aproveitar as proteções nativas do Windows nos bastidores, mantendo a Folha simples; não redefinir a arquitetura já fechada.

| Gate observado nesse SHA | Evidência |
|---|---|
| Nexus Windows | [SUCCESS](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37304293988): Core 140, Blocks 1068, All 1386, Practical 40 PASS |
| Integration Stress | [SUCCESS](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37304293836): blocos 100K, MCP, E2E controlado e regressão 1386 PASS |
| Avatar | [SUCCESS](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37304294007): 165 PASS em Windows e 165 em Ubuntu |
| Auditoria | [SUCCESS](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37304293869): 34 históricos e 11 de persistência PASS |
| Confinamento Windows | **[FAIL](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37304294214): 22 acessos proibidos ALLOWED; 2 controlos PASS**. Contratos de autoridade da aplicação: 26 PASS |

As contagens sobrepõem-se e não devem ser somadas. O novo Practical verde não identifica a causa do PermissionError anterior; a falha histórica continua conservada abaixo. O E2E controlado e os ensaios de avatar não substituem backend/modelo/GPU físicos completos. O gate de confinamento correu em runner Windows Server 2025, com alvos sintéticos; não é prova no PC de Pedro.

### O que o código realmente faz

- `host.py::_run` chama `subprocess.Popen` com cwd/env reduzidos e CREATE_NO_WINDOW. Não escolhe conta Nexus/token restrito, não aplica ACL e não associa Job Object. A tool mantém a identidade corrente. O gate hostil confirmou a consequência em 20 operações de escrita e 2 leituras proibidas de ensaio.
- `mcp_client.py::_open_session` usa `stdio_client` com command/args/env. A allowlist limita nomes de tools; não restringe os direitos Windows do servidor. O percurso efetivo é Host → runner → MCP → adaptador → subprocesso ou API externa.
- `adapters/office.py` e `adapters/languagetool.py` lançam os executáveis sem seleção de identidade restrita. Perfil LibreOffice por tarefa, validação de pacotes, heap Java e timeout são controlos reais, mas não isolamento de ficheiros.
- `lab/open_notebook_avatar/notebook_avatar/service.py::command` cria processos e grupos, com limites e captura de output. Não aplica a fronteira Windows do Host. O comentário do código atribui a sandbox de SO à camada externa; essa ligação ainda falta.
- `windows/sync-nexus-pc.ps1` arranca ACE-Step/Forge com Start-Process; `install-media-tools.ps1` pode usar winget e uv python install sem fixar todas as localizações/caches a ToolsRoot. Não há prova de instalação confinada; não foi executado nenhum instalador nesta revisão.
- `instance.py` e `app.py` já usam proteções Windows reais: bloqueio do diretório por msvcrt e exclusividade da porta por SO_EXCLUSIVEADDRUSE. Os gates de arranque passam; estas proteções têm âmbito diferente do isolamento de ferramentas.
- `Host.authorize` passa uma sessão Unicode diretamente a hmac.compare_digest. Ensaio do método real extraído por AST: sessão válida ACCEPTED; falsa ASCII Blocked; falsa Unicode TypeError; tipo errado Blocked. Prova de componente, sem importação/execução completa do Host. Correção local preparada não equivale a correção publicada.

### Contrato preservado e diferença de implementação

O comportamento exigido já está em [F008](F008-ISOLAMENTO-WINDOWS.md) e [Windows como hospedeiro](SCHEMAS-E-WINDOWS.md). A pessoa usa linguagem normal; Kernel/Host/Store aplicam autorização e regras; o Host lança uma tarefa delimitada; o Windows faz cumprir os direitos do processo; o Host verifica o retorno e escreve no destino permitido. A gestão de contas, ACLs, tokens e processos não pertence ao percurso normal da Folha. A pessoa continua a ver decisões humanas materiais quando exigidas.

A evidência [WINDOWS-TWO-FOLDERS](WINDOWS-TWO-FOLDERS-EVIDENCE.json), de 01-10, regista identidade Nexus, escrita permitida e leitura/escrita protegida recusadas. É válida para as duas pastas artificiais. O código atual não integra esse lançamento com credenciais no Host. Não inferir que o PC ou todas as ferramentas continuam protegidos a partir desse ensaio antigo.

**Estado: requisito definido; integração de segurança nativa incompleta; execução confinada FAIL.** Próximo microprocesso: ligar a execução real a uma fronteira Windows verificada, delimitar trabalho versus estado do Host, cobrir descendentes, acesso entre tarefas, rede e bancada/modelo; repetir o gate hostil e regressão sem enfraquecer critérios. Não é necessário redesenhar M1–M14 para reconhecer esta lacuna.

### Trabalho ainda não entregue

- Contenção de emergência e correção de sessão Unicode: preparadas numa cópia local separada, **não publicadas nem validadas no CI**. O HEAD publicado continua a executar como antes. Bloquear execução seria contenção, não PASS de sandbox funcional.
- 40.000 inputs adversariais adicionais: ficheiro local preparado, **NOT RUN**. Não os contar como testes passados nem como 40.000 provas independentes do Windows.
- PC, contas, permissões, serviços e ficheiros pessoais não foram alterados por esta revisão.
- Verificação local da cópia publicada: 29 hashes do manifesto conformes; sintaxe dos 74 ficheiros Python Nexus válida. Estes dois controlos não executam o software nem demonstram segurança de SO.

## Revisão observada em 05-10-2026, 10:09 Lisboa

SHA analisado: `7faead619e14d15e5590f84e1d52ac68d1e58bc4`. A revisão documental posterior não constitui correção do runtime nem transfere PASS para o novo commit.

| Gate | Resultado nesse SHA |
|---|---|
| [Auditoria](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37274701729) | SUCCESS |
| [Integration Stress](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37274701734) | SUCCESS; regressão 1386 PASS |
| [Avatar Windows/Ubuntu](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37274701774) | 165 PASS em cada OS |
| [Nexus Windows](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37274701714) | **FAIL**: Core 140 PASS, Blocks 1068 PASS, All 1386 PASS, Practical **39 PASS / 1 FAIL** |

Falha: `test_real_windows_result_back_to_original_and_folha_after_restart[binary-attachment]`, em `test_reverse_flow.py`. A leitura de `runs/<id>/state.json` em `store.state()` devolveu `PermissionError`; o pedido HTTP terminou em `RemoteDisconnected`. `INTEGRITY=PASS`. Não é o controlo negativo de Python inexistente. Possível acesso concorrente/bloqueio de ficheiro é hipótese, não causa demonstrada.

Próximo gate: diagnosticar/reproduzir esta falha, corrigir minimamente quando a causa estiver identificada e repetir Practical, regressão e E2E. Um rerun verde isolado não prova resolução da causa. **Este SHA não tem PASS global.** As suites sobrepõem-se; não somar contagens.

## Última baseline funcional validada antes da limpeza documental

A baseline funcional `7e1ec9b6ce1804123c1cb4bd198ea2dfff5bd98a` passou duas execuções independentes dos gates principais:

- Kernel stress: 100.000 casos PASS;
- linguagem/ambiguidade: 100.000 casos PASS;
- MCP stdio: 1.000 operações PASS;
- OpenNotebook Kernel E2E: PASS;
- ACE-Step/Forge MCP health: 17 PASS;
- regressão completa: 1386 PASS;
- Core Windows: 140 PASS;
- Blocks: 1068 PASS;
- Practical: 40 PASS;
- avatar OpenNotebook: 165 PASS Windows + 165 PASS Ubuntu;
- auditoria histórica: 34 PASS;
- persistência ativa: 11 PASS.

A limpeza posterior é documental/organizacional. O HEAD resultante só passa a nova baseline depois de repetir os mesmos workflows e regressões.

## PC físico

O repositório já contém `nexus/windows/sync-nexus-pc.ps1` para atualizar uma única árvore Git local, validar o Nexus, instalar ACE-Step/Forge externamente e executar health checks.

O gate físico só fica fechado quando existirem, no PC:

- `C:\Nexus-Tools\pc-bootstrap.json`;
- `C:\Nexus-Tools\media-health.json`.

Sem esses relatórios, CI/GitHub PASS não é apresentado como PASS do hardware local.

## Pendências técnicas ainda reais

1. Fechar o confinamento Windows real acima antes de recomendar instalação/execução no PC; diagnosticar também o PermissionError histórico, mesmo com o Practical atual verde.
2. Fechar o E2E físico OpenNotebook 1.15 + SurrealDB + modelo local + Kernel + Creative + Human Gate + Canonical.
3. Escolher e validar um checkpoint Forge com licença conhecida antes de geração real.
4. Continuar os contratos ainda abertos em #3 (IMP-001) e #4 (G10/IMP-019 + eliminação controlada).
5. Integrar outras ferramentas externas apenas pelo mesmo processo: contrato → FAIL real → correção mínima → regressão → teste prático → E2E.

## Percurso do desenvolvimento

A [genealogia de decisões](../../DECISIONS.md) explica por fase o problema, a alteração, a razão e a evidência: receção/persistência, ferramentas existentes, Folha/bancada, testes Windows, simplificação Python/MCP e multimédia. Datas e resultados históricos não são apresentados como validação do HEAD atual.

## Documentação que permanece por função

### Contratos e fundamentos
- `F001.md` … `F013-PROVENIENCIA-INVERSA.md`
- `FUNDACAO-REVISTA-2026-10-01.md`
- `SCHEMAS-E-WINDOWS.md`
- `CONTRATO-RELATORIOS-MICROPROCESSO.md`
- `REGRA-PYTHON-MINIMO-FRONTDOOR-2026-10-04.md`

### Relatórios/evidência
- `RELATORIO-STRESS-100K-2026-10-04.md`
- `RELATORIO-APRENDIZAGEM-RECOVERY-2026-10-04.md`
- `RELATORIO-LAB-TESTES-POR-FASES-2026-10-04.md`
- `RELATORIO-AVATAR-2026-10-04.md`
- `AVATAR-CI-2026-10-04.json`
- `AVATAR-SYNC-CI-2026-10-04.json`
- `RELATORIO-FINAL-WIKI-100K.md`

### Comparações históricas preservadas
- `RELATORIO-KERNEL-SPIFF-CONDUCTOR-FASE1-2026-10-04.md`
- `RELATORIO-PERFORMANCE-CONDUCTOR-2026-10-04.md`

Estes dois últimos são evidência histórica e não descrevem o runtime ativo.

## Regra de continuidade

Uma alteração só passa a baseline se:
1. o bloco afetado passar;
2. qualquer FAIL for preservado e diagnosticado;
3. a correção mínima passar;
4. regressão completa passar;
5. testes práticos aplicáveis passarem;
6. E2E aplicável passar;
7. a PR #23 for atualizada com o resultado.

Não criar novas cópias de estado/continuidade para cada sessão. Atualizar este documento e a PR #23.

## Organização documental — pedido humano de 05-10-2026

Pedido: resumir, limpar e organizar o repositório. Revisão limitada a README principal, README Nexus, AGENTS, DECISIONS e este documento; sem apagar contratos, relatórios, comparações ou histórico. Corrigidas referências a executor retirado e documento removido; indicação explícita de candidato versus main, princípio versus composição histórica e PASS versus FAIL. PR #23 acompanha a entrega. Não foram alterados runtime, testes, licenças ou regras de autoridade.
