# CHANGELOG — Auditoria de Trabalho

## Ciclo 0 — 2026-10-07
- Problema: Os ficheiros obrigatórios de estado persistente definidos pelo contrato atual não existiam na branch de trabalho.
- Causa: O estado operacional anterior era mantido noutro documento e o contrato atual introduz três artefactos específicos.
- Hipótese: Criar os três ficheiros sem alterar arquitetura nem código permite retomar de forma verificável e independente da conversa.
- Ficheiros alterados: `auditoria/WORK_STATE.md`, `auditoria/TEST_MATRIX.md`, `auditoria/CHANGELOG-AUDIT.md`.
- Teste criado/alterado: Nenhum; ciclo de bootstrap documental.
- Comando executado: Inspeção GitHub REST da branch, árvore, PR #23, documentos de estado e commits.
- Resultado: Branch `lab/windows-full-install-20261006` confirmada 124 commits à frente do HEAD da PR #23 e como descendente direto dessa baseline; ficheiros de estado obrigatórios ausentes.
- Revisão do diff: Apenas três novos documentos de auditoria; sem alteração de runtime.
- Regressões: NÃO EXECUTADAS neste ciclo documental.
- Decisão: ACEITE.
- Próxima ação: Diagnóstico do núcleo real e execução dos testes relacionados antes de qualquer correção de código.

## Ciclo 1
### Problema
O estado persistente dizia que nenhum teste tinha sido executado, mas a branch já continha cinco commits de TDD no PR #30 e CI real executado. Além disso, a durabilidade foi corrigida em `nexus/store.py`, mas o writer recuperável ativo ainda mantém uma fronteira mais fraca no Windows.

### Evidência
HEAD `d51858cef2d395dd8bc97729eb0f6998b8475177`. PR #30 aberto/draft/mergeable. Auditoria e suites run `37607954581` terminou SUCCESS: documentação 47 ficheiros/84 ligações; 5 testes documentais PASS; `nexus/tests/test_atomic_durability.py` 3 PASS/1 SKIP Windows em Linux; suite histórica 34 PASS; writer ativo 11 PASS. Nexus Windows Confinement Gate run `37607954542` terminou SUCCESS em windows-2022 e windows-latest. Leitura do writer mostra `os.replace(tmp,target); self._fsync_dir(...)` e `_fsync_dir` retorna imediatamente em Windows.

### Alteração
Reconciliação dos três ficheiros de estado com o código e CI reais. Nenhum runtime alterado neste ciclo.

### Teste criado ou atualizado
Nenhum neste ciclo de diagnóstico. Foi identificado o teste que falta: substituição durável real no `RecoverableMarkdownWriter`, com filesystem real e sem mocks de I/O.

### Comando executado
GitHub: leitura do PR #30, commits, árvore e ficheiros; leitura dos logs dos runs `37607954581` e `37607954542`; inspeção de `nexus/store.py`, `nexus/tests/test_atomic_durability.py`, `nexus/tests/test_startup.py`, `nexus/tests/test_kernel_crash_contract.py`, `nexus/tests/test_vaults.py`, `nexus/security_tests/test_state_concurrency.py`, `implementacao/ativa-2026-09-28/cerebro/persistence.py` e respetivos testes.

### Resultado real
PASS parcial e lacuna reproduzida por inspeção do código: a fronteira `nexus.store.atomic` tem durabilidade explícita; a fronteira do writer ativo não tem write-through Windows. Os testes de crash do writer são sintéticos e não satisfazem o critério final atual.

### Revisão
Não foi atribuído PASS a crash/restart, ingestão, writer Windows ou E2E apenas por existirem testes antigos ou grandes contagens de stress. C21 foi marcado PASSA porque `test_state_concurrency.py` foi efetivamente executado no gate Windows e o comando terminou PASS.

### Decisão: ACEITE
### Estado persistente atualizado: SIM
### Próxima ação
Criar e executar um teste FAIL de filesystem real para a fronteira durável do `RecoverableMarkdownWriter`; só depois corrigir o writer e reexecutar unidade + regressão Linux/Windows.
