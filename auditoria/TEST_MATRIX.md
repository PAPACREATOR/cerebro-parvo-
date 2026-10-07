# Matriz de Testes

| ID | Comportamento | Teste | Estado | Último resultado | Observação |
|----|---------------|-------|--------|------------------|------------|
| T001 | Receção preserva bytes normais | A localizar/criar | NÃO TESTADO | — | Próximo ciclo |
| T002 | Receção preserva ficheiro vazio | A localizar/criar | NÃO TESTADO | — | Próximo ciclo |
| T003 | Receção preserva Unicode | A localizar/criar | NÃO TESTADO | — | Comparar bytes |
| T004 | Receção preserva binário | A localizar/criar | NÃO TESTADO | — | Comparar bytes |
| T005 | Ficheiro grande | A localizar/criar | NÃO TESTADO | — | Sem mocks |
| T006 | Inexistente falha explicitamente | A localizar/criar | NÃO TESTADO | — | Sem engolir erro |
| T007 | Path traversal ../ bloqueado | test_escape_rejected | PASSA | 2 casos PASS em pytest local | I/O real; ../ e x/../../ |
| T008 | Hash da entrada correto | A localizar/criar | NÃO TESTADO | — | Hash do writer não substitui hash de ingestão |
| T009 | Estado PREPARED antes da materialização final | test_real_process_crash_after_prepared_is_recoverable | PASSA | PASS; após exit 97 reconcile=NOT_COMMITTED | SQLite PREPARED sobreviveu à morte real |
| T010 | fsync do temporário | A criar | NÃO TESTADO | — | Código chama os.fsync; falta prova específica |
| T011 | Substituição atómica | A criar | NÃO TESTADO | — | Código usa os.replace; falta prova específica |
| T012 | fsync do diretório pai | A criar | NÃO TESTADO | — | Linux executa; Windows retorna sem fsync |
| T013 | Ficheiro final verificado | test_write_creative / reconcile | PASSA | PASS | Hash final verificado pelo writer |
| T014 | COMMITTED só após persistência | A criar | NÃO TESTADO | — | Falta prova explícita de ordenação |
| T015 | Evento de sucesso só após COMMITTED | A criar | NÃO TESTADO | — | Evento E2E ainda não integrado |
| T016 | Crash antes do commit recupera | test_real_process_crash_after_prepared_is_recoverable | PASSA | PASS; subprocess terminou 97; resume COMMITTED | Processo real, sem mock I/O |
| T017 | Crash após replace reconcilia | test_real_process_crash_after_replace_reconciles | PASSA | PASS; subprocess terminou 98; reconcile COMMITTED | Processo real, sem mock I/O |
| T018 | Replay é idempotente | test_idempotent | PASSA | PASS | Mesmo operation_id/conteúdo não duplica materialização |
| T019 | Proveniência não altera conteúdo | A localizar/criar | NÃO TESTADO | — | Contrato separado |
| T020 | Original nunca é apagado | A localizar/criar | NÃO TESTADO | — | Exige fluxo de ingestão |
| T021 | Symlink malicioso bloqueado | A criar | NÃO TESTADO | — | Segurança |
| T022 | Colisão de hash não inventa sucesso | A criar | NÃO TESTADO | — | Segurança/integridade |
| T023 | Concorrência mantém integridade | A criar | NÃO TESTADO | — | Escritas simultâneas |
| T024 | Permissões restritas tratadas explicitamente | A criar | NÃO TESTADO | — | OSError real |
| T025 | core.py + persistência E2E | A criar | NÃO TESTADO | — | Integração |
