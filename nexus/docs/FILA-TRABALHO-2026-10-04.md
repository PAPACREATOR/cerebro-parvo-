# Fila de trabalho — auditoria, integração e testes bidirecionais

Data: 2026-10-04.
Branch de trabalho: `work/audit-bidirectional-20261004`.
Regra: não alterar leis nem arquitetura congelada sem FAIL estrutural reproduzido e decisão humana.

## Método obrigatório por tarefa

1. Auditar estado atual e trabalho do Work.
2. Comparar contrato, código, teste e evidência.
3. Criar/reproduzir FAIL antes de corrigir quando existir lacuna.
4. Fazer correção mínima.
5. Testar ida e volta.
6. Testar falha/restart/bypass quando aplicável.
7. Registar PASS/FAIL/BLOCKED/NOT RUN.
8. Comunicar no PR #7.
9. Só depois avançar.

## Fila

| ID | Tarefa | Dono | Estado | Critério de fecho |
|---|---|---|---|---|
| T01 | Crash após resultado do executor e antes de Store.accept | GPT/revisor | PASS | run 37197610565: 1197 PASS; sem reexecução, workflow fixado, Canonical vazio |
| T02 | Crash antes da execução externa | GPT/revisor | PASS | teste Work existente conserva input, marca interrupção e não cria Canonical |
| T03 | Crash depois de Creative e antes do estado final | GPT/revisor | PASS | run 37198248236: 1206 PASS; Creative completo reconciliado; 8 danos ficam BLOCKED e preservados |
| T04 | Idempotência de reentrada | GPT/revisor | PARCIAL | accept idempotente após crash e promoção repetida já cobertos; escala/property-based pendente |
| T04A | Binding resultado ↔ workflow fixado | GPT/revisor | PASS | run 37198721444: 1207 PASS; trace com hash diferente é rejeitado |\n| T05 | Human Gate adversarial | GPT/revisor | PASS | run 37199085733: 1210 PASS; sessão inválida não consome ticket, ticket cruzado bloqueado, restart invalida ticket pendente |
| T06 | Comparação Conductor-only vs Spiff+Conductor | GPT/Work | BLOQUEADO PELO ESPELHO LOCAL | mesmos contratos efémeros; persistência fora da comparação |
| T07 | Integração Windows LAB | Codex/PC | NOT RUN | commit testado em C:\Nexus-Lab, relatório PASS/FAIL devolvido |
| T08 | Isolamento Windows por capability | Work/PC | PENDENTE | mínimo privilégio + ACL/processo + bypass testado |
| T09 | Capabilities externas uma a uma | Work/PC | PENDENTE | cada ligação ida/volta/falha/restart e proveniência |
| T10 | Matriz 100000 casos | GPT/Work | PENDENTE | property-based + crash + idempotência + diferencial, sem 100k processos pesados |
| T11 | Snapshot/auditoria PC completa | GPT/Codex | PENDENTE | inventário, hashes, Git, ACLs, testes, cloud ref |
| T12 | Hardening final + encriptação + móvel | Final | PENDENTE | depois da integração funcional e regressão global |

## Estado atual conhecido

- Work PR #7: Windows CI e auditoria PASS no HEAD conhecido.
- Branch `integration-lab-20261004` nasceu idêntica ao Work HEAD.
- `C:\Nexus` é produção/KNOWN_GOOD e não deve receber experiências.
- `C:\Nexus-Lab` é destino para testes Windows reais.
- GitHub = coordenação e código; Drive = snapshots/artefactos; PC = execução real.
- Persistência/restart/reconciliação pertencem ao Kernel/Store, nunca ao executor.


## Evidência desta sessão

- FAIL real T01: `1 failed, 1196 passed` — run 37197119992.
- T01 corrigido: `1197 passed in 55.49s` — run 37197610565.
- FAIL real T03: `1 failed, 1197 passed` — run 37197826991.
- T03 + adversarial: `1206 passed in 47.22s` — run 37198248236.
- FAIL real binding de workflow: `1 failed, 1206 passed` — run 37198491684.
- Binding corrigido: `1207 passed in 39.51s` — run 37198721444.
- Em todos os PASS finais: `NEXUS PASS | COMPLETE` e wrapper PowerShell PASS.

- T05 Human Gate adicional: `1210 passed in 51.73s` — run 37199085733; nenhuma alteração ao Host necessária.
