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
