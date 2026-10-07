# Matriz de Testes

| ID | Comportamento | Teste | Estado | Último resultado | Observação |
|----|---------------|-------|--------|------------------|------------|
| T001 | Receção preserva bytes normais | A localizar/criar | NÃO TESTADO | — | Exige I/O real |
| T002 | Receção preserva ficheiro vazio | A localizar/criar | NÃO TESTADO | — | Exige I/O real |
| T003 | Receção preserva Unicode | A localizar/criar | NÃO TESTADO | — | Comparar bytes |
| T004 | Receção preserva binário | A localizar/criar | NÃO TESTADO | — | Comparar bytes |
| T005 | Ficheiro grande | A localizar/criar | NÃO TESTADO | — | Sem mocks |
| T006 | Inexistente falha explicitamente | A localizar/criar | NÃO TESTADO | — | Sem engolir erro |
| T007 | Path traversal ../ bloqueado | A localizar/criar | NÃO TESTADO | — | Segurança |
| T008 | Hash da entrada correto | A localizar/criar | NÃO TESTADO | — | Recalcular no teste |
| T009 | Estado PREPARED antes da materialização final | A localizar/criar | NÃO TESTADO | — | Ordem transacional |
| T010 | fsync do temporário | A localizar/criar | NÃO TESTADO | — | Prova por comportamento real |
| T011 | Substituição atómica | A localizar/criar | NÃO TESTADO | — | os.replace ou equivalente |
| T012 | fsync do diretório pai | A localizar/criar | NÃO TESTADO | — | Obrigatório |
| T013 | Ficheiro final verificado | A localizar/criar | NÃO TESTADO | — | Hash/tamanho/bytes |
| T014 | COMMITTED só após persistência | A localizar/criar | NÃO TESTADO | — | Sem sucesso prematuro |
| T015 | Evento de sucesso só após COMMITTED | A localizar/criar | NÃO TESTADO | — | Ordem de eventos |
| T016 | Crash antes do commit recupera | A localizar/criar | NÃO TESTADO | — | Processo real |
| T017 | Crash após replace reconcilia | A localizar/criar | NÃO TESTADO | — | Processo real |
| T018 | Replay é idempotente | A localizar/criar | NÃO TESTADO | — | Sem duplicação |
| T019 | Proveniência não altera conteúdo | A localizar/criar | NÃO TESTADO | — | Contrato separado |
| T020 | Original nunca é apagado | A localizar/criar | NÃO TESTADO | — | MVP |
| T021 | Symlink malicioso bloqueado | A localizar/criar | NÃO TESTADO | — | Segurança |
| T022 | Colisão de hash não inventa sucesso | A localizar/criar | NÃO TESTADO | — | Segurança/integridade |
| T023 | Concorrência mantém integridade | A localizar/criar | NÃO TESTADO | — | Escritas simultâneas |
| T024 | Permissões restritas tratadas explicitamente | A localizar/criar | NÃO TESTADO | — | OSError real |
| T025 | core.py + persistência E2E | A localizar/criar | NÃO TESTADO | — | Integração |
