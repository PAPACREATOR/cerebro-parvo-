# Matriz de trabalhos e autoridade das provas

Retrato de 10-10-2026. Todas estas PRs encontravam-se abertas/Draft na consulta relevante, salvo evolução posterior que exige nova verificação.

| Ref | Âmbito | O que há | O que **não** prova |
| --- | --- | --- | --- |
| [#31](https://github.com/PAPACREATOR/cerebro-parvo-/pull/31) | Núcleo transacional antigo | Histórico de garantias e auditoria | Que o mesmo código está no runtime atual |
| [#32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32) | Baseline Windows | 8 SUCCESS/1 FAIL Writer no SHA da descrição | Release E2E completo |
| [#41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41) | Navegação e documentos | Docs atuais em branch própria | Conteúdo já em main |
| [#43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43) | Work, verify natural | Contrato/implementação isolados | Todas as intenções, produto integrado |
| [#44](https://github.com/PAPACREATOR/cerebro-parvo-/pull/44) | OpenNotebook | Negativos com peer simulado | Serviço/modelo reais validados |
| [#45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45) | Integração candidata | FAIL-first e gates parciais PASS | Merge, aceitação PC, release |
| [#46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46) | Auditoria documental | Inventários/ref/links parcialmente verificados | Cópia Windows, scan completo ou todos os links |
| [#47](https://github.com/PAPACREATOR/cerebro-parvo-/pull/47) | Wiki/Flow Lab | Casos FAIL-first e plano de correção | Integração ou produto final |
| [#48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48) | Clones/inventário técnico | Clone Git Linux, inventário árvores publicadas | Ficheiros do PC limpos ou copiados integralmente |
| [#49](https://github.com/PAPACREATOR/cerebro-parvo-/pull/49) | Documentação e classificação histórica | Navegação + auditoria estática por ficheiro/SHA da PR #45 | Que o código foi testado/alterado, que a PR está em main ou que existe produto aprovado |

**Laboratórios externos à tabela do repositório principal:** [Writer Lab #1](https://github.com/PAPACREATOR/nexus-writer-lab/pull/1) prova a diferença de namespace de pipes sob LPAC; [Writer Lab #2](https://github.com/PAPACREATOR/nexus-writer-lab/pull/2) ensaia a solução Sandy por A/B (sem resultado terminal na consulta). [Sir Thaddeus e Writer — detalhes por SHA](CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md). Não somar os seus PASS ou resultados aos gates da PR #45.

**SHA de referência verificados no exame:** main aeeb6f662a8282b3793708aa3e6782ef20d2d0ca; #32 da86b6dd181d00fd7a87addaa01a12ec3a14e57b; #41 46c6b6722028017b5c174986128be4a151588ae7; #45 66027af7f2ea084bc62d85b840d1fc3113e60a97; #46 6ebf4912ee0ce58eece0aa9f4f26842aca177010; #48 37212f2b82d0cd4bcf2118cc4ec549a7c1da7726. São pontos de observação, não verdades para sempre.

Ver também a [matriz de compatibilidade com código](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) e o [protocolo de prova](PROTOCOLO-VERIFICACAO-DOCUMENTAL.md). A PR #49 é **somente documentação**; os seus commits não alteram nem certificam o SHA da PR #45.

Fontes complementares: [auditoria em Draft](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46), [issue de convergência](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33), [gate OpenNotebook](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42).