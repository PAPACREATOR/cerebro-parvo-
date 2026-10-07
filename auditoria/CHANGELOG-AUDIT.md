# CHANGELOG — AUDITORIA

## Ciclo 0
- Data: 2026-10-07
- Problema: Os ficheiros obrigatórios de estado persistente não existiam no repositório.
- Causa: Processo anterior não mantinha auditoria no formato agora exigido.
- Hipótese: Criar estado neutro, sem marcar PASS sem execução, permite retomar trabalho sem depender da conversa.
- Ficheiros alterados: auditoria/WORK_STATE.md; auditoria/TEST_MATRIX.md; auditoria/CHANGELOG-AUDIT.md
- Teste criado/alterado: Nenhum teste funcional; apenas matriz inicial marcada NÃO TESTADO.
- Comando executado: Nenhum comando de teste neste ciclo de inicialização.
- Resultado: Estado persistente inicial criado; comportamento funcional continua NÃO TESTADO.
- Revisão do diff: Apenas documentação de estado/auditoria; nenhuma alteração funcional.
- Regressões: NÃO TESTADO.
- Decisão: ACEITE
- Próxima ação: Ler árvore/código/testes reais do núcleo e executar os testes relacionados com a implementação atual antes de alterar código.

## Ciclo 1
- Data: 2026-10-07
- Problema: Os testes existentes de crash usavam RuntimeError no mesmo processo e não provavam interrupção real.
- Causa: RecoverableMarkdownWriter.write só tinha failpoint simulado.
- Hipótese: Um crashpoint explícito que termina o subprocesso com os._exit permite provar persistência PREPARED e recuperação após replace sem mock do sistema de ficheiros.
- Ficheiros alterados: implementacao/ativa-2026-09-28/cerebro/persistence.py; implementacao/ativa-2026-09-28/tests/test_persistence.py.
- Teste criado/alterado: test_real_process_crash_after_prepared_is_recoverable; test_real_process_crash_after_replace_reconciles.
- Comando executado: python -m pytest -q --color=no tests/test_persistence.py -k 'real_process_crash'; depois python -m pytest -q --color=no tests/test_persistence.py.
- Resultado: Antes da correção 2 FAIL por TypeError hard_crashpoint inexistente; após correção 2 PASS específicos e 13 PASS na unidade.
- Revisão do diff: Alteração limitada ao writer e ao teste; failpoints simulados antigos mantidos; novo crashpoint valida apenas after_prepared/after_replace.
- Regressões: Unidade de persistência 13/13 PASS local.
- Decisão: ACEITE
- Próxima ação: Executar regressão CI completa e prosseguir para ingestão byte-a-byte.

## Ciclo 2
- Data: 2026-10-07
- Problema: A regressão GitHub Actions falhava antes de instalar pytest/executar suites.
- Causa: ferramentas/verificar_documentacao.py exige a string M1 em README.md; o README vigente não a continha.
- Hipótese: Restaurar a declaração factual M1–M14 no README satisfaz o verificador sem alterar arquitetura nem código funcional.
- Ficheiros alterados: README.md.
- Teste criado/alterado: Nenhum teste de produto; reutilizado workflow Auditoria e suites.
- Comando executado: GitHub Actions pull_request, run 37612649448/37612938346; inspeção dos jobs/logs.
- Resultado: Falha reproduzida em “Verificar preservacao e links ativos”: Missing architecture reference: README.md. Correção publicada em 7be6d92b83c50858311af3f2935e9607df3682f1; workflow posterior passou.
- Revisão do diff: Uma frase adicionada; sem mudança de arquitetura ou execução.
- Regressões: Auditoria e CodeQL PASS.
- Decisão: ACEITE
- Próxima ação: Iniciar FASE 2 com testes reais de bytes.

## Ciclo 3
- Data: 2026-10-07
- Problema: Receção/quarentena/hash tinham código, mas faltava prova direta dos casos byte-a-byte exigidos.
- Causa: Suite ativa estava concentrada no writer recuperável.
- Hipótese: Testes de I/O real sobre normal, vazio, Unicode, binário, grande e inexistente provam o contrato sem tocar no Kernel.
- Ficheiros alterados: implementacao/ativa-2026-09-28/tests/test_ingest_real.py. Fora do Kernel, descrição do PR #29 corrigida para refletir runtime Ollama-free.
- Teste criado/alterado: test_ingest_preserves_bytes_exactly; test_ingest_large_file_preserves_hash_and_bytes; test_receive_missing_file_fails_explicitly; test_empty_rejected_when_policy_disallows.
- Comando executado: suite real de ingestão 7 casos; GitHub Actions Auditoria e suites + CodeQL no head 1ffe4923dfc3216910a12e8079f89782302af717.
- Resultado: 7/7 ingestão PASS; CI Auditoria PASS; CodeQL PASS.
- Revisão do diff: Apenas novo teste de ingestão; nenhuma mudança de lógica do Kernel neste ciclo. O ramo de instalação já continha testes explícitos que proíbem Ollama e exigem llama.cpp.
- Regressões: Nenhuma observada nos gates executados.
- Decisão: ACEITE
- Próxima ação: Testar concorrência real e symlink malicioso; alterar código apenas se o teste falhar pelo motivo esperado.


## Ciclo 4
### Problema
Symlink malicioso e concorrência real ainda estavam marcados NÃO TESTADO.
### Evidência
Teste preliminar com filesystem real bloqueou um symlink de CREATIVE para fora do cofre. Oito processos reais escreveram simultaneamente a mesma operação e terminaram com uma única materialização válida.
### Alteração
Apenas testes; nenhuma alteração em core.py ou persistence.py.
### Teste criado ou atualizado
test_symlink_escape_is_blocked_without_writing_outside; test_same_operation_concurrent_processes_remain_idempotent.
### Comando executado
GitHub Actions “Auditoria e suites” no commit a78f2f05b6c464c1429fc705022b04983fff47e5.
### Resultado real
PASS. O workflow concluiu SUCCESS.
### Revisão
O diff deste ciclo altera só test_persistence.py e os ficheiros obrigatórios de estado. Não muda semântica do Kernel.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Testar permissões reais, proveniência imutável e a ordem PREPARED→COMMITTED; alterar código apenas perante FAIL real.


## Ciclo 5
### Problema
Ordem PREPARED→COMMITTED, adulteração pós-commit, permissões reais e imutabilidade da proveniência ainda não tinham prova direta.
### Evidência
Foram adicionados testes que matam o processo após o replace e inspecionam SQLite diretamente, adulteram o ficheiro já COMMITTED, removem permissão de escrita no filesystem POSIX e comparam o candidato antes/depois de criar proveniência.
### Alteração
Apenas testes; core.py e persistence.py não foram alterados.
### Teste criado ou atualizado
test_after_replace_crash_leaves_prepared_until_reconcile; test_committed_tamper_requires_recovery; test_real_permission_denial_does_not_commit; test_provenance_does_not_modify_candidate_content.
### Comando executado
GitHub Actions “Auditoria e suites” no commit 8f76d4113a414f9e9ae2c3f5bc4edf761552285d.
### Resultado real
PASS. Workflow completo SUCCESS.
### Revisão
Os testes confirmam que o estado continua PREPARED após a substituição física até reconcile/commit, adulteração força RECOVERY_REQUIRED e proveniência não modifica o candidato. A prova de permissões é POSIX; Windows continua pendente.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Criar e executar o teste E2E core + persistência; confirmar FAIL do stub materialize e implementar apenas uma camada mínima de integração fora do Kernel existente.


## Ciclo 6
### Problema
Não existia integração executável entre os eventos preparados do core e o writer recuperável; core.materialize permanecia fail-closed.
### Evidência
Foi criado primeiro test_integration_e2e.py. O GitHub Actions falhou com ModuleNotFoundError: No module named 'cerebro.integration', provando a ausência concreta da fronteira de integração.
### Alteração
Criado apenas cerebro/integration.py. core.py e persistence.py permaneceram byte-a-byte inalterados neste ciclo. A camada valida correlação/autoridade, chama o writer real e só devolve CREATIVE_CANDIDATE_COMMITTED após receipt.state == COMMITTED.
### Teste criado ou atualizado
test_core_to_persistence_commits_before_success_event.
### Comando executado
GitHub Actions “Auditoria e suites” no commit de teste 1f71bc6474a3196ef47b2bd50d4a7a69759a3a7e e novamente após correção no commit d503a0eb6f9eafa85e1b63d9fb12bed4bd4680c9.
### Resultado real
Primeiro run: FAIL esperado na recolha por ausência de cerebro.integration. Segundo run: PASS completo.
### Revisão
A correção acrescenta um único ficheiro de cola; não altera regras de autoridade, persistência, core.py nem persistence.py. O evento de sucesso é construído apenas depois do writer devolver COMMITTED.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Abrir gate Windows específico para fsync do diretório pai e corrigir apenas a implementação privada _fsync_dir se o teste falhar como esperado.


## Ciclo 7
### Problema
O gate Windows revelou que a concorrência não era deterministicamente idempotente e que a implementação ativa não tinha uma primitiva de persistência equivalente ao fsync do diretório no Windows.
### Evidência
No commit 553f6d40566ad9bf4e5bc44210bb0869aa549f8e o job Windows falhou com sqlite3.IntegrityError: UNIQUE constraint failed em concorrência e com None no teste de flush Windows. A documentação Microsoft mostra MOVEFILE_WRITE_THROUGH como mecanismo documentado que só retorna quando o move foi efetivamente escrito em disco.
### Alteração
Em persistence.py, prepare agora adquire BEGIN IMMEDIATE antes de reler/inserir operation_id. A substituição passou para _replace_and_sync: POSIX usa os.replace + fsync(dir); Windows usa MoveFileExW com MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH. Nenhuma alteração em core.py.
### Teste criado ou atualizado
test_windows_replace_is_write_through_and_persists_target; teste concorrente existente passou a ser executado também no runner Windows.
### Comando executado
GitHub Actions “Auditoria e suites” antes e depois da correção, incluindo o job Persistência ativa — Windows.
### Resultado real
Antes: 2 failed, 25 passed, 1 skipped no Windows. Depois: job Windows PASS e job Ubuntu PASS.
### Revisão
Alteração limitada a um ficheiro de código, um ficheiro de testes e workflow de CI. A autoridade, Creative/Canonical, proveniência e contratos do Core não mudaram.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Provar interrupção real após fsync do temporário e antes do replace, incluindo recuperação sem ficheiros .partial órfãos.


## Ciclo 8
### Problema
Faltava prova de crash real entre fsync do temporário e a substituição final; o primeiro teste também revelou diferenças Windows de path canonicalization e de replace concorrente.
### Evidência
Primeiro FAIL: hard_crashpoint after_temp_fsync inexistente. Segundo FAIL: após suportar o ponto de morte, resume chegava a COMMITTED mas o .partial do processo morto permanecia. O teste foi corrigido para não exigir limpeza potencialmente destrutiva. No Windows, a mesma suite revelou prefixo \\?\ no Path.resolve e WinError 5 em replace concorrente de bytes idênticos.
### Alteração
Adicionado hard_crashpoint after_temp_fsync. No Windows, _resolve_target normaliza apenas o prefixo de caminho estendido antes da verificação commonpath. Uma falha PermissionError no replace concorrente só é tolerada quando o alvo já existe e o seu hash é exatamente o esperado; bytes divergentes continuam a propagar erro.
### Teste criado ou atualizado
test_real_process_crash_after_temp_fsync_resumes_safely; regressão de test_same_operation_concurrent_processes_remain_idempotent nos dois SO.
### Comando executado
GitHub Actions “Auditoria e suites” nos commits d395f30f..., 273f8e35..., 306fc24a... e c8c0840d..., com jobs Ubuntu e Windows.
### Resultado real
As fases intermédias falharam pelos motivos registados. No head c8c0840de83a7034cff2aa011a88dafdb2b582ae: Ubuntu PASS e Windows PASS.
### Revisão
Nenhuma alteração em core.py. As mudanças ficam confinadas a persistence.py e testes. Não há eliminação automática de .partial órfão porque isso exigiria coordenação/locking adicional e poderia apagar trabalho ainda ativo.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Testar digest igual com bytes diferentes, depois permissões Windows reais e auditoria da proibição de except Exception engolido.


## Ciclo 9
### Problema
Restavam sem prova explícita a colisão lógica de digest, a política de exceções e a eliminação de originais; o gate Windows de ACL também revelou bloqueio do teste.
### Evidência
test_equal_digest_never_overrides_byte_comparison provou que um digest forçado igual não autoriza duplicação quando os bytes diferem. A auditoria AST confirmou que handlers genéricos existentes fazem re-raise e que não há bare except/silent pass. delete_authorized_original permaneceu fail-closed e o original ficou byte-a-byte intacto.
### Alteração
Foram acrescentados apenas testes de invariantes/auditoria. Em core.py a única correção foi restringir a captura do detector ZIP a OSError, RuntimeError e zipfile.BadZipFile, sem alterar contratos ou autoridade.
### Teste criado ou atualizado
test_equal_digest_never_overrides_byte_comparison; test_generic_exception_handlers_must_reraise_explicitly; test_no_bare_except_or_silent_pass_handlers; test_original_deletion_remains_fail_closed.
### Comando executado
GitHub Actions “Auditoria e suites” e CodeQL em múltiplos heads do PR #31, com inspeção dos jobs/logs reais.
### Resultado real
PASS nos gates de digest, adulteração, exceções e eliminação fail-closed. O gate Windows de permissões continuou em diagnóstico neste ciclo.
### Revisão
Nenhuma mudança de arquitetura. Nenhuma promoção de autoridade. Nenhum mock de filesystem. Nenhum original apagado.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Isolar e diagnosticar a permissão Windows real sem alterar o Kernel por hipótese.

## Ciclo 10
### Problema
Dois FAIL reais apareceram na regressão: concorrência podia falhar durante PRAGMA journal_mode=WAL com sqlite3.OperationalError: database is locked; sob ACL Windows negada, tempfile.mkstemp ficava preso em _mkstemp_inner.
### Evidência
Os logs GitHub Actions mostraram a stack SQLite no PRAGMA WAL. Depois, faulthandler no subprocesso Windows mostrou bloqueio em tempfile.py::_mkstemp_inner chamado por persistence.py::write. O teste ACL usou icacls real e nenhum mock.
### Alteração
Em persistence.py foi adicionado retry estritamente limitado a OperationalError contendo “locked” durante ativação WAL, preservando WAL e propagando qualquer outro erro. No Windows, a criação do temporário usa uma única os.open exclusiva com nome opaco; POSIX mantém tempfile.mkstemp. Nenhuma alteração em core.py.
### Teste criado ou atualizado
test_same_operation_concurrent_processes_remain_idempotent; test_windows_acl_write_denial_does_not_commit; diagnóstico temporário com faulthandler.
### Comando executado
GitHub Actions “Auditoria e suites” em Ubuntu e Windows, incluindo execuções que reproduziram os FAIL e a regressão após as correções.
### Resultado real
A concorrência deixou de apresentar lock intermitente nos runs seguintes. A ACL Windows passou a falhar prontamente em vez de bloquear. A primeira regressão após essa correção revelou apenas uma expectativa de nome antigo do .partial no teste de crash.
### Revisão
As mudanças ficaram confinadas à fronteira de persistência; PREPARED/COMMITTED, autoridade, proveniência e integração não foram alterados.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Corrigir apenas a expectativa do teste de .partial Windows e repetir regressão completa.

## Ciclo 11
### Problema
test_real_process_crash_after_temp_fsync_resumes_safely procurava exclusivamente .op-hard.*.partial, mas a criação temporária Windows passou legitimamente a usar nome opaco.
### Evidência
No run 37619895907, Ubuntu passou; Windows teve 34 PASS, 1 skipped e apenas este teste falhou porque partials=[] apesar do crashpoint exit 99 ter ocorrido.
### Alteração
Apenas o teste foi atualizado para procurar um único ficheiro oculto com sufixo .partial e verificar que contém exatamente b"payload". Nenhum ficheiro de produto foi alterado neste ciclo.
### Teste criado ou atualizado
test_real_process_crash_after_temp_fsync_resumes_safely.
### Comando executado
GitHub Actions “Auditoria e suites”, run 37620145579, head e052f5d0785581951f6eb2cf368e9464bbda4fcd.
### Resultado real
SUCCESS. Job Ubuntu PASS e job “Persistência ativa — Windows” PASS. Todos os comportamentos T001–T025 estão agora PASSA com execução real.
### Revisão
O último diff é exclusivamente de teste. Ollama continua fora do percurso obrigatório; a branch de instalação lab/windows-full-install-20261006 em 90683cd3744db074c4ea3b3c170aad6218f2b8ed usa llama.cpp e tem os workflows de instalação/stress/Windows verdes já auditados.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Executar a regressão final disparada por esta atualização documental. Se verde, não alterar mais o núcleo sem novo FAIL real.


## Ciclo 12
### Problema
A regressão documental seguinte ao ciclo 11 voltou a reproduzir uma corrida rara no Windows: um dos oito processos concorrentes recebeu PermissionError ao abrir o ficheiro final para verificação de hash, depois da substituição concorrente.
### Evidência
GitHub Actions run 37620363035: Ubuntu PASS; Windows 34 PASS, 1 skipped e 1 FAIL em test_same_operation_concurrent_processes_remain_idempotent. A stack terminou em persistence.py::_hash_file, Path.open("rb"), PermissionError [Errno 13].
### Alteração
Apenas persistence.py: _hash_file repete PermissionError exclusivamente no Windows durante no máximo 0,5 s, em intervalos de 10 ms. Qualquer bloqueio persistente ou qualquer outro erro continua a propagar-se. core.py não foi alterado.
### Teste criado ou atualizado
Nenhum teste novo; reutilizado o teste concorrente real existente com oito subprocessos e toda a regressão Ubuntu/Windows.
### Comando executado
GitHub Actions “Auditoria e suites”, run 37657894986, head d7bcd4e3d17d3cd6da7939b12248317de06055c6.
### Resultado real
SUCCESS. Job “Integridade + suite histórica + persistência ativa” PASS e job “Persistência ativa — Windows” PASS.
### Revisão
Patch mínimo e localizado na leitura de hash. Não altera PREPARED/COMMITTED, replace, autoridade, proveniência, Creative/Canonical ou core.py. Erros persistentes não são escondidos.
### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Confirmar CodeQL do head funcional. Se verde, congelar o Kernel até novo FAIL real.
