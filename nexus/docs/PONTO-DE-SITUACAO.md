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

1. Executar e validar a baseline atual no PC físico/RTX 2080.
2. Fechar o E2E físico OpenNotebook 1.15 + SurrealDB + modelo local + Kernel + Creative + Human Gate + Canonical.
3. Escolher e validar um checkpoint Forge com licença conhecida antes de geração real.
4. Continuar os contratos ainda abertos em #3 (IMP-001) e #4 (G10/IMP-019 + eliminação controlada).
5. Integrar outras ferramentas externas apenas pelo mesmo processo: contrato → FAIL real → correção mínima → regressão → teste prático → E2E.

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
