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
| T010 | fsync do temporário | test_real_process_crash_after_temp_fsync_resumes_safely | PASSA | PASS Ubuntu + Windows | Processo morre com exit 99 após fsync; partial contém bytes completos |
| T011 | Substituição atómica/durável | test_after_replace_crash_leaves_prepared_until_reconcile + test_windows_replace_is_write_through_and_persists_target | PASSA | PASS Ubuntu + Windows | POSIX os.replace; Windows MoveFileExW WRITE_THROUGH |
| T012 | Persistência do diretório/rename | suite Windows + POSIX | PASSA | PASS | POSIX fsync(dir); Windows durable MoveFileExW |
| T013 | Ficheiro final verificado | test_write_creative / reconcile | PASSA | PASS | Hash final verificado |
| T014 | COMMITTED só após persistência | test_after_replace_crash_leaves_prepared_until_reconcile | PASSA | PASS | BD permanece PREPARED após replace |
| T015 | Evento de sucesso só após COMMITTED | test_core_to_persistence_commits_before_success_event | PASSA | PASS | Evento construído após receipt COMMITTED |
| T016 | Crash antes do commit recupera | test_real_process_crash_after_prepared_is_recoverable | PASSA | PASS | Processo real |
| T017 | Crash após replace reconcilia | test_real_process_crash_after_replace_reconciles | PASSA | PASS | Processo real |
| T018 | Replay é idempotente | test_idempotent | PASSA | PASS | Mesmo operation_id/conteúdo |
| T019 | Proveniência não altera conteúdo | test_provenance_does_not_modify_candidate_content | PASSA | PASS | Candidate intacto |
| T020 | Original nunca é apagado | test_ingest_preserves_bytes_exactly | PASSA | PASS | Originais intactos |
| T021 | Symlink malicioso bloqueado | test_symlink_escape_is_blocked_without_writing_outside | PASSA | PASS | Sem escrita externa |
| T022 | Colisão/adulteração de hash não inventa sucesso | test_committed_tamper_requires_recovery + test_equal_digest_never_overrides_byte_comparison | PASSA | PASS Ubuntu + Windows | Digest igual nunca substitui comparação byte-a-byte; adulteração exige recovery |
| T023 | Concorrência mantém integridade | test_same_operation_concurrent_processes_remain_idempotent | PASSA | PASS original + 3 reruns Windows consecutivos no run 37658064553 | 8 subprocessos por execução; retry de leitura Windows limitado a 0,5 s; nenhum novo FAIL |
| T024 | Permissões restritas tratadas explicitamente | test_real_permission_denial_does_not_commit + test_windows_acl_write_denial_does_not_commit | PASSA | PASS Ubuntu + Windows | chmod POSIX e ACL icacls Windows reais; sem mock |
| T025 | core.py + persistência E2E | test_core_to_persistence_commits_before_success_event | PASSA | PASS | Camada mínima integration.py |
