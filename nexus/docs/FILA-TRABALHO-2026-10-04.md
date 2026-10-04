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
| T01 | Crash após resultado do executor e antes de Store.accept | GPT/revisor | EM CURSO | restart reconcilia sem reexecutar Conductor, preserva proveniência, PASS bidirecional |
| T02 | Crash antes da execução externa | GPT/revisor | PENDENTE | reinício conserva pedido e não inventa resultado |
| T03 | Crash depois de Creative e antes do estado final | GPT/revisor | PENDENTE | estado reconciliado sem duplicar efeitos |
| T04 | Idempotência de reentrada | GPT/revisor | PENDENTE | mesmo operation/run não duplica Creative/Canonical |
| T05 | Human Gate adversarial | GPT/revisor | PENDENTE | bypass, ticket antigo, conteúdo alterado e restart bloqueados |
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
