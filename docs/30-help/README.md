# Ajudar o Nexus

Obrigado por querer contribuir. O objetivo é facilitar contribuições concretas sem alterar o núcleo conceptual nem trabalhar por cima de outra pessoa.

Consultar [estado datado](../10-current/ESTADO-DOCUMENTAL-2026-10-10.md), [história](../99-history/README.md) e [evidência por SHA](../60-evidence/MATRIZ-PRS-2026-10-10.md). Uma branch Draft não equivale a release.

## Começar aqui

1. Leia [Start here](../00-start-here/README.md).
2. Consulte o [estado operacional](../../nexus/docs/PONTO-DE-SITUACAO.md).
3. Escolha uma issue pública já delimitada.
4. Reproduza primeiro; proponha alteração depois.

## Issues atuais recomendadas

- **#35 — Help wanted geral:** revisão, testes e contribuições sem alterar o núcleo.
- **#36 — LibreOffice Writer / LPAC:** diagnosticar timeout sem reduzir isolamento.
- **#37 — Good first issue:** frases PT-PT adversariais da Folha/ELIZA.
- **#38 — Good first issue:** documentação ativa vs histórica e duplicação real.
- **#39 — Windows gates:** revisão independente dos claims PASS/FAIL.

## Limites

Não alterar arquitetura M1–M14 sem falha estrutural reproduzível.

Não enfraquecer AppContainer/LPAC/Job/ACL para obter PASS.

Não introduzir uma dependência nova quando Kernel + MCP/API/CLI existente resolvem a função.

Não dar a uma ferramenta, modelo, workflow engine ou agente:
- acesso de escrita a Canonical;
- autoridade de aprovação;
- capacidade de contornar allowlists;
- poder de repetir automaticamente side effects cujo resultado ficou ambíguo após crash.

## Forma preferida de contribuição

- reprodução independente;
- teste que falha de forma útil;
- análise de causa;
- patch pequeno;
- PR isolado;
- evidência FAIL → correção → PASS.

Código de terceiros exige origem, versão/commit e licença.
