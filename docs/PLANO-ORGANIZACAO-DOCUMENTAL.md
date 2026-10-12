# Plano de organização documental

Data: 2026-10-12  
Base: `a0403808586036259cf120ef1947f6f185eb3a93`

## Objetivo

Organizar a documentação para que a realidade do projeto, a realidade do repositório e a apresentação externa fiquem coerentes, sem apagar trabalho nem genealogia.

## Regras

1. **Preservar primeiro.** Nenhum ficheiro, decisão, relatório, teste ou evidência é apagado por ser antigo, redundante ou desatualizado.
2. **Separar camadas.** Documentação vigente, trabalho interno e apresentação para outros ficam claramente distinguíveis.
3. **Histórico permanece.** Decisões substituídas passam a estar identificadas como históricas, com data e motivo; não são removidas.
4. **Eliminação excepcional.** Só se remove conteúdo que, após várias verificações independentes, não tiver qualquer valor histórico, técnico, legal ou de proveniência. Cada remoção exige registo datado do motivo e da verificação.
5. **Links e referências.** Toda a documentação ativa é auditada para links internos válidos e referências corretas ao HEAD.
6. **Evidência antes de estado.** `PASS` só pode ser afirmado com execução ou verificação observada; `FAIL`, timeout, ausência de evidência e `UNKNOWN` nunca se transformam em `PASS`.
7. **Autoridade humana.** A documentação não concede autoridade a IA, ferramentas, workflows ou agentes. Promoções e ações protegidas continuam sujeitas a Human Gate.

## Camadas documentais

| Camada | Finalidade | Exemplos atuais |
|---|---|---|
| Vigente | Estado e instruções operacionais atuais | `README.md`, `STATUS.md`, `docs/architecture/`, `docs/planning/` |
| Trabalho interno | Registo técnico, auditoria, tarefas e evidência | `auditoria/`, `tasks/`, `nexus/docs/`, `implementacao/` |
| Genealogia | Decisões, alternativas e evolução datada | `DECISIONS.md`, `docs/GENEALOGIA.md`, `docs/INVENTARIO-HISTORICO.md`, `historico/` |
| Apresentação externa | Explicação pública e estável para outras pessoas | `README.md`, `PROMOTION.md`, `COMPATIBILITY-MATRIX.md` |

## Ordem de trabalho

1. Inventariar documentos ativos e históricos.
2. Verificar links internos, referências cruzadas e instruções desatualizadas.
3. Marcar explicitamente o que é vigente, interno, histórico ou apresentação.
4. Corrigir apenas inconsistências comprovadas.
5. Propor remoções apenas quando a verificação repetida demonstrar que não há valor a preservar.
6. Registar resultado, limites e evidência antes de qualquer merge.

## Estado inicial

A raiz contém os documentos de arquitetura e decisões recuperados; `docs/` contém documentação operacional, contratos, genealogia, inventário histórico, reconciliação e pendências. Esta branch serve para organizar essas camadas sem remoções iniciais.
