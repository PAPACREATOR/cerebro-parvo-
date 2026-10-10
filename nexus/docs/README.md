# Índice técnico do Nexus (contratos, relatórios, ensaios)

Este diretório reúne documentos de vários momentos do projeto; não confundir um contrato de capacidade com integração testada. Navegação principal: [documentação Nexus](../../docs/README.md). Compatibilidade com código do candidato: [matriz 10/10](../../docs/10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md).

## Ponto de situação

- [PONTO-DE-SITUACAO.md](PONTO-DE-SITUACAO.md) — relato operacional **acumulado e datado**, cuja abertura documenta trabalhos de 08/10. A PR #45 é candidata posterior em Draft; comparar [matriz de PRs](../../docs/60-evidence/MATRIZ-PRS-2026-10-10.md) antes de afirmar «último estado».
- [WINDOWS-ACCEPTANCE-ISOLATED.md](WINDOWS-ACCEPTANCE-ISOLATED.md) — procedimento de **aceitação isolada**, não instalação no PC comprovada.
- [WINDOWS-STACK-COMPATIBILITY-2026-10-07.md](WINDOWS-STACK-COMPATIBILITY-2026-10-07.md) — compatibilidade estudada no âmbito próprio.

## Contratos de capacidades

- [F001](F001.md), [F002](F002.md), [F003](F003.md), [F004](F004.md) — primeiros contratos/etapas.
- [F005 — Cognição](F005-COGNICAO.md); [F006 — LanguageTool](F006-LANGUAGETOOL.md); [F007 — LibreOffice](F007-LIBREOFFICE.md).
- [F008 — Isolamento Windows](F008-ISOLAMENTO-WINDOWS.md); [F009 — Objetos Markdown](F009-OBJETOS-MARKDOWN.md); [F010 — Prompt literal](F010-PROMPT-LITERAL.md).
- [F011 — Arranque único](F011-ARRANQUE-UNICO.md); [F012 — Hash Windows isolado](F012-HASH-WINDOWS-ISOLADO.md); [F013 — Proveniência inversa](F013-PROVENIENCIA-INVERSA.md).
- [CAPABILITY-WRITER-EDITORIAL.md](CAPABILITY-WRITER-EDITORIAL.md) — contrato editorial W001–W020; não declarar Writer completo até gate real.
- [PROTECTED-PROVISIONING-CONTRACT.md](PROTECTED-PROVISIONING-CONTRACT.md) — limitações de instalação externa.
- [product-flows-20261006.md](product-flows-20261006.md) — definição de fluxos/produtos da fase correspondente.

## Wiki, interpretação, investigação

- [CONTRATO-LAB-WIKI-KERNEL-FLOWS.md](CONTRATO-LAB-WIKI-KERNEL-FLOWS.md), [ESTUDO-LIGACAO-WIKI-KERNEL-FLOWS-2026-10-04.md](ESTUDO-LIGACAO-WIKI-KERNEL-FLOWS-2026-10-04.md), [LAB-WIKI-KNOWLEDGE-2026-10-04.md](LAB-WIKI-KNOWLEDGE-2026-10-04.md).
- [COMPLEMENTO-WIKI-INFORMACAO-GERADA-2026-10-04.md](COMPLEMENTO-WIKI-INFORMACAO-GERADA-2026-10-04.md) e [REVISAO-CONTRATOS-WIKI.md](REVISAO-CONTRATOS-WIKI.md).
- [CONTRATO-RELATORIOS-MICROPROCESSO.md](CONTRATO-RELATORIOS-MICROPROCESSO.md).

## Ensaios e resultados datados

- [RELATORIO-FINAL-WIKI-100K.md](RELATORIO-FINAL-WIKI-100K.md), [RELATORIO-STRESS-100K-2026-10-04.md](RELATORIO-STRESS-100K-2026-10-04.md), [RELATORIO-LAB-TESTES-POR-FASES-2026-10-04.md](RELATORIO-LAB-TESTES-POR-FASES-2026-10-04.md).
- [RELATORIO-KERNEL-SPIFF-CONDUCTOR-FASE1-2026-10-04.md](RELATORIO-KERNEL-SPIFF-CONDUCTOR-FASE1-2026-10-04.md), [RELATORIO-PERFORMANCE-CONDUCTOR-2026-10-04.md](RELATORIO-PERFORMANCE-CONDUCTOR-2026-10-04.md), [RELATORIO-APRENDIZAGEM-RECOVERY-2026-10-04.md](RELATORIO-APRENDIZAGEM-RECOVERY-2026-10-04.md).
- [RELATORIO-AVATAR-2026-10-04.md](RELATORIO-AVATAR-2026-10-04.md), [REVISAO-NUCLEO-2026-10-01.md](REVISAO-NUCLEO-2026-10-01.md), [TESTES-ADVERSARIAIS.md](TESTES-ADVERSARIAIS.md).
- [PUBLICACAO-2026-10-01.md](PUBLICACAO-2026-10-01.md), [FUNDACAO-REVISTA-2026-10-01.md](FUNDACAO-REVISTA-2026-10-01.md), [WIKI-INSTALACAO.md](WIKI-INSTALACAO.md), [MERCADO-2026-10-04.md](MERCADO-2026-10-04.md).

## Confinamento e diagnósticos

- [CONTRATO-ISOLAMENTO-2026-10-05.md](CONTRATO-ISOLAMENTO-2026-10-05.md), [SCHEMAS-E-WINDOWS.md](SCHEMAS-E-WINDOWS.md), [REGRA-PYTHON-MINIMO-FRONTDOOR-2026-10-04.md](REGRA-PYTHON-MINIMO-FRONTDOOR-2026-10-04.md).

## Limites obrigatórios

Os resultados PASS/FAIL de um relatório pertencem ao respetivo ambiente/commit. OpenNotebook/SurrealDB/modelos físicos, Writer real em LPAC e todas as ferramentas do PC não ficam automaticamente aprovados pela existência de testes ou documentos. Nenhum documento deste diretório concede autoridade a IA, Conductor, Spiff, MCP ou ferramentas externas. [Método de validação](../../docs/60-evidence/PROTOCOLO-VERIFICACAO-DOCUMENTAL.md).

Não foram movidos os documentos originais; este índice é uma **ponte de leitura**.
