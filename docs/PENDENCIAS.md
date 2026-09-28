# Pendências e portões — 28-09-2026

A arquitetura operacional foi simplificada. As pendências abaixo são implementação/prova, não convite para voltar a expandir o desenho.

| ID | Lacuna | Fecho mínimo |
| --- | --- | --- |
| P01 | Writer G10/IMP-019 | Implementar PREPARED -> Markdown atómico -> hash -> COMMITTED -> reconcile; testar crash/retry/replay |
| P02 | Vertical slice Activepieces | Chat/trigger -> Core -> resultado -> Creative real, com correlação e erro explícito |
| P03 | Human Gate | Decisão humana autenticada/específica -> Canonical; preservar Creative/genealogia |
| P04 | Open Notebook + tiny | Um espaço reutilizável, sessão/contexto por tarefa, budget real, duas áreas temáticas, saída UNTRUSTED |
| P05 | 3 comparadores integrados | Provar determinístico/semântico/relacional num caso real e preservar contradição |
| P06 | Pesquisa/derivados | FTS/cache reconstruível e política com índice sujo |
| P07 | Sandbox/fronteiras | Activepieces sandbox para flows; Open Notebook/tiny sem acesso direto aos cofres; temporários para ferramentas |
| P08 | Recovery operacional | restart, recibos, estado divergente, backup e restore testado |
| P09 | Windows/UX | instalação no PC alvo e uso sem Markdown/SQL/IDs visíveis |
| P10 | Terceiros | Fixar versão/licença/origem apenas dos componentes realmente integrados |
| P11 | Release/licenciamento | rever THIRD_PARTY_NOTICES, contribuição/dual licensing e segredos antes de tornar público |
| P12 | Eliminação | Fora do MVP; IMP-024–026 continuam bloqueados até política futura específica |

## Importação

IMP-001–026 continuam como matriz de contratos da família de importação. Não bloquear a prova do produto inteiro à espera de os transformar em módulos independentes. Quando uma vertical slice toca num IMP, os critérios desse IMP aplicáveis têm de passar.

## Regra

Resolver por dependência e evidência. Se uma ferramenta madura já resolver a mecânica, integrar e testar em vez de reimplementar.

[Projeto final](PROJETO-FINAL-AUDITADO-2026-09-28.md) · [Plano](../IMPLEMENTATION_PLAN.md)
