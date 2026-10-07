# Matriz de Testes

| ID | Comportamento | Teste | Estado | Último resultado | Observação |
|----|---------------|-------|--------|------------------|------------|
| T001 | Receção preserva bytes normais | test_ingest_preserves_bytes_exactly | PASSA | PASS | I/O real |
| T002 | Receção preserva ficheiro vazio | test_ingest_preserves_bytes_exactly | PASSA | PASS | Política permite vazio |
| T003 | Receção preserva Unicode | test_ingest_preserves_bytes_exactly | PASSA | PASS | Comparação byte-a-byte UTF-8 |
| T004 | Receção preserva binário | test_ingest_preserves_bytes_exactly | PASSA | PASS | 0..255 repetido |
| T005 | Ficheiro grande | test_ingest_large_file_preserves_hash_and_bytes | PASSA | PASS | 8 MiB, bytes + SHA-256 |
| T006 | Inexistente falha explicitamente | test_receive_missing_file_fails_explicitly | PASSA | PASS | ContractError RECEIVE_FAILED |
| T007 | Path traversal ../ bloqueado | test_escape_rejected | PASSA | PASS | ../ e x/../../ |
| T008 | Hash da entrada correto | test_ingest_preserves_bytes_exactly / test_ingest_large_file_preserves_hash_and_bytes | PASSA | PASS | SHA-256 recalculado no teste |
| T009 | Estado PREPARED antes da materialização final | test_real_process_crash_after_prepared_is_recoverable | PASSA | PASS | exit 97; reconcile NOT_COMMITTED |
| T010 | fsync do temporário | A criar | NÃO TESTADO | — | Código chama os.fsync; falta prova específica |
| T011 | Substituição atómica | A criar | NÃO TESTADO | — | Código usa os.replace; falta prova específica |
| T012 | fsync do diretório pai | A criar | NÃO TESTADO | — | Linux executa; Windows retorna sem fsync |
| T013 | Ficheiro final verificado | test_write_creative / reconcile | PASSA | PASS | Hash final verificado |
| T014 | COMMITTED só após persistência | A criar | NÃO TESTADO | — | Falta prova explícita de ordenação |
| T015 | Evento de sucesso só após COMMITTED | A criar | NÃO TESTADO | — | Evento E2E ainda não integrado |
| T016 | Crash antes do commit recupera | test_real_process_crash_after_prepared_is_recoverable | PASSA | PASS | Processo real, sem mock I/O |
| T017 | Crash após replace reconcilia | test_real_process_crash_after_replace_reconciles | PASSA | PASS | Processo real, sem mock I/O |
| T018 | Replay é idempotente | test_idempotent | PASSA | PASS | Mesmo operation_id/conteúdo |
| T019 | Proveniência não altera conteúdo | A criar | NÃO TESTADO | — | Próximo ciclo |
| T020 | Original nunca é apagado | test_ingest_preserves_bytes_exactly | PASSA | PASS | Originais permanecem byte-a-byte nos casos exercitados |
| T021 | Symlink malicioso bloqueado | test_symlink_escape_is_blocked_without_writing_outside | PASSA | PASS no CI | Sem escrita no destino externo |
| T022 | Colisão/adulteração de hash não inventa sucesso | A criar | NÃO TESTADO | — | Segurança/integridade |
| T023 | Concorrência mantém integridade | test_same_operation_concurrent_processes_remain_idempotent | PASSA | PASS no CI | 8 subprocessos, mesma operação e payload |
| T024 | Permissões restritas tratadas explicitamente | A criar | NÃO TESTADO | — | OSError real |
| T025 | core.py + persistência E2E | A criar | NÃO TESTADO | — | Integração |
