# História e genealogia

O Nexus preserva decisões anteriores porque FAILs, experiências e componentes rejeitados são evidência técnica. Esta revisão organiza épocas e motivos **sem deslocar documentos originais**. Quatro páginas históricas tiveram exclusivamente reparações de navegação e avisos editoriais, mantendo versões anteriores acessíveis pelo commit Git. Preservar histórico não significa que continue ativo.

## Por mês

- [Setembro de 2026](2026-09/README.md) — estudos, baselines e redução das dependências.
- [Outubro de 2026](2026-10/README.md) — runtime Windows, convergência, gates e divisão de trabalho.

## História por fases

- [Cronologia 22/09–10/10](LINHA-DO-TEMPO-2026-09-22-A-2026-10-10.md).
- [Decisões superadas e respetivos motivos](DECISOES-SUPERADAS-E-PORQUE.md).
- [Mapa de origens](MAPA-DE-ORIGENS.md).
- [Reconciliação das 11 referências históricas da PR #46](RECONCILIACAO-11-REFERENCIAS-2026-10-10.md): dez links corrigidos e uma fonte reservada identificada sem reprodução.
- [Classificação documental por família e estatuto](CLASSIFICACAO-DOCUMENTAL-2026-10-10.md).
- [Inventário integral dos 172 Markdown do snapshot da branch](INVENTARIO-MARKDOWN-POR-CAMINHO-2026-10-10.md) — caminhos e Git blob SHA por pasta.
- [Decisões vigentes fundamentadas](../40-decisions/README.md).

## Onde está o histórico

- [historico/](../../historico/) — versões, planos e experiências anteriores.
- [implementacao/](../../implementacao/) — implementações históricas/candidatas anteriores.
- [DECISIONS.md](../../DECISIONS.md) — decisões vigentes e genealogia.
- [nexus/docs/](../../nexus/docs/) — contratos, relatórios e evidência por capacidade.

## Como interpretar

Documentos antigos podem mencionar Activepieces, Conductor, Spiff ou outras composições que já foram removidas do runtime candidato.

Use-os para:
- compreender decisões;
- reproduzir experiências;
- recuperar testes;
- comparar abordagens.

Não os use como instruções para reinstalar dependências sem um FAIL atual que o justifique.

## Regra

História é evidência. O [ponto de situação técnico](../../nexus/docs/PONTO-DE-SITUACAO.md) conserva relatos por ciclo; a PR #32 é **baseline Windows** e a PR #45 é **integração posterior em Draft**, não release. Ver [compatibilidade por SHA](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md).
