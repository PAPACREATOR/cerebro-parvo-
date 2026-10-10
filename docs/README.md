# Documentação Nexus — índice de leitura

Atualização documental: 10-10-2026. Esta árvore assenta na navegação da PR #41; a presente revisão é uma proposta documental isolada, não está integrada em main.

## Escolher o caminho

- [00 — Começar](00-start-here/README.md): apresentação e regras de leitura.
- [10 — Situação corrente](10-current/README.md): referência operacional e [fotografia de reconciliação de 10/10](10-current/ESTADO-DOCUMENTAL-2026-10-10.md).
- [20 — Arquitetura](20-architecture/MINIMUM-CORE.md): núcleo mínimo e [fronteiras de autoridade](20-architecture/FRONTEIRAS-DE-AUTORIDADE.md).
- [30 — Contribuir](30-help/README.md): colaboração delimitada.
- [40 — Decisões e razões](40-decisions/README.md): entradas datadas, fontes, alternativas e limites.
- [50 — Ferramentas](50-capabilities/README.md): capacidades externas e gates.
- [60 — Evidências](60-evidence/README.md): PRs, SHA e significado de PASS/FAIL.
- [90 — Investigação](90-research/): estudos não normativos por si só.
- [99 — História](99-history/README.md): cronologia, escolhas substituídas e localização das fontes originais.

## Regras de vigência

A Constituição e uma decisão humana posterior prevalecem sobre soluções de época. Código/testes do HEAD exato provam o que está implementado, não o que ficou simplesmente planeado. A fonte operacional detalhada permanece [nexus/docs/PONTO-DE-SITUACAO.md](../nexus/docs/PONTO-DE-SITUACAO.md), a reconciliar com o HEAD candidato; esta pasta não o substitui.

Os documentos antigos **não são apagados, renomeados ou movidos** sem manifesto e validação de ligações: preservar caminhos existentes evita quebrar referências e prova histórica. Os novos subdiretórios organizam interpretação e navegação, não reescrevem arquivos originais.

A frente documental não altera código, testes, scripts, configuração de execução, Kernel, Host ou Store. Não faz merge automático.