# Outubro de 2026 — runtime, convergência e isolamento de frentes

**Tipo:** índice histórico datado; testes só valem para o SHA e ambiente indicados.

## 01–05/10 — capacidades e comparadores reais

Foram estudados e ensaiados LanguageTool, LibreOffice, Conductor/Spiff, transporte MCP Python e multimédia. **Razão das experiências:** descobrir o mínimo de integração necessário com Windows, Creative/Canonical e recuperação. A presença de testes PASS por bloco não implica produto aceite.

## 06–08/10 — um runtime, não dois Kernels

A [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) confronta a PR #31 (núcleo transacional anterior) com a PR #32 (runtime Windows). **Escolha:** PR #32 como baseline, usando os contratos da #31 como testes, sem copiar o código antigo. [ADR](../../40-decisions/ADR-2026-10-07-CONVERGENCIA.md).

## 09/10 — interface, confirmação e ferramentas

A PR #43 propôs verify natural com confirmação pré-execução; a PR #45 integrou-a apenas num candidato Draft, passou de FAIL-first a testes parciais. A [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42) fixou OpenNotebook como ferramenta especializada selecionada pelo Kernel/Host, sem autoridade própria nem obrigatoriedade. [ADRs](../../40-decisions/README.md).

## 10/10 — auditoria, segurança e colaboração

PR #41 organiza documentação; #46 verifica documentos/links/privacidade; #48 **comprova clone Git integral de Sir Thaddeus em Linux**, verifica 1.446/1.446 ficheiros e inventaria seis árvores Nexus públicas. **Limite:** nada disso certifica os ficheiros Windows do PC, nem prova execução Sir Thaddeus.

Em paralelo, o laboratório [Writer PR #1](https://github.com/PAPACREATOR/nexus-writer-lab/pull/1) demonstrou a diferença real entre pipe legado (WinError 5) e namespace `LOCAL` sob LPAC. A nova [Writer PR #2](https://github.com/PAPACREATOR/nexus-writer-lab/pull/2) testa a solução pública Sandy de Hrvoje Abraham numa bancada descartável. **A integração de Sandy no Nexus continua suspensa**, mas o ensaio isolado de diagnóstico foi autorizado. A primeira execução A/B **terminou FAIL** (SHA `fa8d65c4`, [run 38047795468](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795468)): o caso A atingiu o prazo e falhou a prova de limpeza/terminação, pelo que o caso B foi corretamente bloqueado e não executado. Um novo ensaio em SHA `40d29078` encontrava-se em curso na leitura posterior; isto não prova Writer/PDF funcional nem altera o candidato PR #45. [Fontes e SHA](../../60-evidence/CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md).

A frente de documentação não altera código nem as branches de implementação.

Fontes: [matriz por PR](../../60-evidence/MATRIZ-PRS-2026-10-10.md), [situação datada](../../10-current/ESTADO-DOCUMENTAL-2026-10-10.md), [decisões superadas](../DECISOES-SUPERADAS-E-PORQUE.md).