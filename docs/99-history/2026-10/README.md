# Outubro de 2026 — runtime, convergência e isolamento de frentes

**Tipo:** índice histórico datado; testes só valem para o SHA e ambiente indicados.

## 01–05/10 — capacidades e comparadores reais

Foram estudados e ensaiados LanguageTool, LibreOffice, Conductor/Spiff, transporte MCP Python e multimédia. **Razão das experiências:** descobrir o mínimo de integração necessário com Windows, Creative/Canonical e recuperação. A presença de testes PASS por bloco não implica produto aceite.

## 06–08/10 — um runtime, não dois Kernels

A [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) confronta a PR #31 (núcleo transacional anterior) com a PR #32 (runtime Windows). **Escolha:** PR #32 como baseline, usando os contratos da #31 como testes, sem copiar o código antigo. [ADR](../../40-decisions/ADR-2026-10-07-CONVERGENCIA.md).

## 09/10 — interface, confirmação e ferramentas

A PR #43 propôs verify natural com confirmação pré-execução; a PR #45 integrou-a apenas num candidato Draft, passou de FAIL-first a testes parciais. A [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42) fixou OpenNotebook como ferramenta especializada selecionada pelo Kernel/Host, sem autoridade própria nem obrigatoriedade. [ADRs](../../40-decisions/README.md).

## 10/10 — auditoria, segurança e colaboração

PR #41 organiza documentação; #46 verifica documentos/links/privacidade; #48 regista clones/inventário de árvores Git em Linux. **Limite:** nada disso certifica os ficheiros Windows do PC. Suspensa a integração Sandy, conservando estudo e crédito. A frente de documentação não altera código nem as branches de implementação.

Fontes: [matriz por PR](../../60-evidence/MATRIZ-PRS-2026-10-10.md), [situação datada](../../10-current/ESTADO-DOCUMENTAL-2026-10-10.md), [decisões superadas](../DECISOES-SUPERADAS-E-PORQUE.md).