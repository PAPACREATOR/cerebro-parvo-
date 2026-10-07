# Matriz de Testes

| ID | Comportamento | Teste | Estado | Último resultado | Observação |
|----|---------------|-------|--------|------------------|------------|
| C01 | Ingestão de ficheiro normal | Por localizar/criar | NÃO TESTADO | — | Revalidar no HEAD atual |
| C02 | Preservação byte-a-byte | Por localizar/criar | NÃO TESTADO | — | Inclui binário e Unicode |
| C03 | Hash da entrada e verificação final | Por localizar/criar | NÃO TESTADO | — | Hash não pode substituir verificação de bytes |
| C04 | Estado PREPARED antes da escrita final | implementacao/ativa-2026-09-28/tests/test_persistence.py | NÃO TESTADO | 11 PASS na suite do writer, mas sem crash de processo real | Os failpoints atuais são sintéticos; não contam como prova final |
| C05 | Ficheiro temporário + fsync | nexus/tests/test_atomic_durability.py + writer ativo | NÃO TESTADO | Nexus atomic Linux executado; writer ainda sem prova isolada completa | Requer prova explícita no fluxo alvo |
| C06 | replace atómico + persistência do diretório pai | nexus/tests/test_atomic_durability.py + writer ativo | A FALHAR | Nexus atomic: 3 PASS/1 SKIP em Linux; writer usa os.replace direto e _fsync_dir é no-op Windows | Próximo bloqueio selecionado |
| C07 | COMMITTED só após verificação final | implementacao/ativa-2026-09-28/tests/test_persistence.py | NÃO TESTADO | 11 PASS, mas sem prova de crash real | Revalidar com processo interrompido |
| C08 | Crash antes do commit | Por criar com subprocesso/process kill real | NÃO TESTADO | Testes existentes usam failpoint/monkeypatch | Não contam para o critério atual |
| C09 | Crash após replace antes de COMMITTED | Por criar com subprocesso/process kill real | NÃO TESTADO | Testes existentes usam failpoint/monkeypatch | Não contam para o critério atual |
| C10 | Replay/reconcile idempotente | Por revalidar sem mocks após crash real | NÃO TESTADO | Há testes unitários, insuficientes para este contrato | — |
| C11 | Proveniência sem alterar conteúdo | nexus/tests/test_reverse_flow.py + integração específica por validar | NÃO TESTADO | Gate Windows de confinamento passou, mas não é prova isolada deste critério | — |
| C12 | Original nunca apagado | nexus/tests/test_vaults.py + ingestão específica por validar | NÃO TESTADO | Há teste existente, mas ainda não revalidado como gate deste contrato | Eliminação continua bloqueada no runtime |
| C13 | Ficheiro vazio | Por localizar/criar | NÃO TESTADO | — | Caso limite |
| C14 | Unicode | Por localizar/criar | NÃO TESTADO | — | Bytes preservados |
| C15 | Binário arbitrário | Por localizar/criar | NÃO TESTADO | — | Sem decode implícito |
| C16 | Ficheiro grande | Por localizar/criar | NÃO TESTADO | — | Limites reais |
| C17 | Ficheiro inexistente | Por localizar/criar | NÃO TESTADO | — | Falha explícita |
| C18 | Path traversal ../ | nexus/tests/test_paths_100k.py + teste específico por validar | NÃO TESTADO | Stress existente não foi ainda registado como execução específica deste critério no ciclo | Não herdar PASS por contagem genérica |
| C19 | Symlink malicioso | nexus/tests/test_kernel_crash_contract.py + teste de ingestão por criar | NÃO TESTADO | Existem casos de state/executor symlink; falta ingestão/source symlink | Segurança |
| C20 | Colisão/alteração de hash | Por localizar/criar | NÃO TESTADO | — | Detetar adulteração |
| C21 | Concorrência | nexus/security_tests/test_state_concurrency.py | PASSA | Windows Confinement run 37607954542: comando conjunto authority_10000 + state_concurrency terminou 5 PASS em windows-latest; job também SUCCESS em windows-2022 | Prova concorrência de Store/estado; writer ainda será testado separadamente |
| C22 | Permissões restritas | nexus/tests/test_startup.py + security tests | NÃO TESTADO | Há falhas reais de filesystem no código de teste; aguarda regressão Windows completa do HEAD | — |
| C23 | Core + persistência E2E | Por criar/ligar | A FALHAR | core.py materialize() continua PolicyUndefined | Bloqueio funcional objetivo |
| C24 | Regressão completa | GitHub Actions do PR #30 | NÃO TESTADO | Auditoria e Confinement SUCCESS; Nexus Windows e parte de Integration Stress ainda em execução | Só PASSA quando todos os gates relevantes terminarem |
