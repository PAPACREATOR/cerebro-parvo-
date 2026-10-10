# Evidência e auditoria — guia

Não somar testes de SHA, branches, matrizes, sistemas operativos ou ambientes diferentes como se fossem uma única prova.

**Vocabulário:**
- PASS: teste identificado, no commit e ambiente declarados, com resultado verificável.
- FAIL: falha observada; não se torna PASS por nova narrativa.
- BLOCKED: condição ou autorização necessária impede prova.
- NOT RUN: não testado; pode estar implementado ou apenas planeado.
- UNKNOWN: informação insuficiente.
- Draft: proposta em revisão, sem integração automática.

A [matriz datada de PRs](MATRIZ-PRS-2026-10-10.md) serve de índice. Os logs/SHA e o [ponto de situação](../../nexus/docs/PONTO-DE-SITUACAO.md) são necessários para claims concretos. As auditorias da PR #46 incluem revisão estática de ligações e amostras de privacidade, **não** uma certificação de ausência de segredos.

O material de GitHub e as árvores publicadas não substituem inventário integral com hashes SHA-256 dos ficheiros de C:\\Nexus ou ensaios físicos de Windows, Writer, GPU, OpenNotebook e recuperação de energia.