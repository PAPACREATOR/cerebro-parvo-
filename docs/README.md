# Documentação Nexus — índice de leitura

Atualização documental: 10-10-2026. Esta árvore assenta na navegação da PR #41; a presente revisão é uma proposta documental isolada, não está integrada em main.

## Escolher o caminho

- [00 — Começar](00-start-here/README.md): apresentação e regras de leitura.
- [10 — Situação corrente](10-current/README.md): fotografia de 10/10 e [auditoria direta do código da PR #45](10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md).
- [20 — Arquitetura](20-architecture/MINIMUM-CORE.md): núcleo mínimo e [fronteiras de autoridade](20-architecture/FRONTEIRAS-DE-AUTORIDADE.md).
- [30 — Contribuir](30-help/README.md): colaboração delimitada.
- [40 — Decisões e razões](40-decisions/README.md): entradas datadas, fontes, alternativas, limites e [superfícies de execução](40-decisions/ADR-2026-10-10-SUPERFICIES-DE-EXECUCAO.md).
- [50 — Ferramentas](50-capabilities/README.md): capacidades externas e gates.
- [60 — Evidências](60-evidence/README.md): PRs, SHA, significado de PASS/FAIL, [protocolo de verificação](60-evidence/PROTOCOLO-VERIFICACAO-DOCUMENTAL.md) e [o que ficou demonstrado hoje no Writer/Sir Thaddeus](60-evidence/CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md).
- [90 — Investigação](90-research/): estudos não normativos por si só.
- [99 — História](99-history/README.md): cronologia, escolhas substituídas, [catálogo documental](99-history/CLASSIFICACAO-DOCUMENTAL-2026-10-10.md), [inventário dos caminhos Markdown](99-history/INVENTARIO-MARKDOWN-POR-CAMINHO-2026-10-10.md) e [reconciliação das 11 referências](99-history/RECONCILIACAO-11-REFERENCIAS-2026-10-10.md), além das fontes originais.

## Regras de vigência

A Constituição e uma decisão humana posterior prevalecem sobre soluções de época. Código/testes do HEAD exato provam o que está implementado, não o que ficou simplesmente planeado. O [ponto de situação acumulado](../nexus/docs/PONTO-DE-SITUACAO.md) preserva relatos por ciclo, incluindo material anterior à PR #45. A [matriz código-documentação](10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) explicita o HEAD examinado. Estas fontes devem ser lidas em conjunto, não por substituição automática.

Os documentos antigos **não são apagados, renomeados ou movidos**. Quatro páginas de época receberam só correção de ligações e aviso editorial de versão; os originais estão preservados no Git por SHA, com registo antes→depois na [reconciliação](99-history/RECONCILIACAO-11-REFERENCIAS-2026-10-10.md). Os novos subdiretórios organizam interpretação e navegação; não convertem decisões antigas em instruções atuais.

A frente documental não altera código, testes, scripts, configuração de execução, Kernel, Host ou Store. Não faz merge automático.