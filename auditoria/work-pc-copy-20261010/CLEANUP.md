# Limpeza verificada — 10-10-2026

Esta continuação parte do commit `bc1935d9707c125509d914fd7eb3e4f35ec584a5` da PR #48. Abrange apenas fontes GitHub e intermediários criados nesta sessão Linux. O Windows de Pedro continua inacessível; não foi feita limpeza no PC nem na instalação.

## Critérios aplicados

Datas foram cruzadas com conteúdo, finalidade e decisões. Um ficheiro antigo não é dispensável por ser antigo. Código, provas, versões distintas, matrizes e genealogia ficam preservados. A reconciliação geral de documentação permanece nas PRs #34/#41/#46, sem alterações paralelas aos seus ficheiros.

## Limpeza executada

| Item | Data verificada no Git | Ação e motivo |
|---|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | 28-09-2026 | Retirado do caminho ativo: colide por capitalização com o outro modelo no Windows. A versão integral permanece no commit de origem e no backup testado. |
| `.github/pull_request_template.md` | 08-10-2026 | Conservado, incluindo o CLA mais recente. Incorporadas as salvaguardas exclusivas do anterior: testes explícitos, FAIL/SKIP/NOT RUN, segredos/dados pessoais, autoridade humana e explicação em linguagem natural. |
| Cinco cópias soltas de CSV/JSON criadas para o inventário | 10-10-2026, intermediários próprios | Eliminadas apenas da área Linux de trabalho após comparação byte a byte com `public-inventory.zip`. Libertados 1.239.880 bytes. O arquivo publicado conserva os cinco conteúdos integrais. |
| Pares idênticos de `core.py` e `__init__.py` entre implementações de 27/09 e 28/09 | Versões distintas, verificadas por hash e bytes | Conservados: são snapshots de implementação, e esta tarefa não autoriza alterar Kernel nem versões. |
| Fontes, duplicados e ficheiros `.tmp` já versionados por Sir Thaddeus | Origem de terceiro congelada | Conservados: o clone deve continuar fiel ao upstream; não se reescreve o projeto de terceiro. |

## Recuperação

Antes de limpar, foi criado um backup dos 182 ficheiros da base e demonstrado o restauro dos 182 por SHA-256 no Linux. A cópia original do template retirado também é recuperável no [commit anterior](https://github.com/PAPACREATOR/cerebro-parvo-/commit/bc1935d9707c125509d914fd7eb3e4f35ec584a5). As cinco cópias intermédias são recuperáveis do arquivo publicado, que permanece inalterado. O teste de restauro não prova restauro físico no Windows.

## Verificação e limites

Os resultados finais, hashes e a cronologia dos 101 documentos Markdown da base constam de `CLEANUP.json`. A cronologia usa a data do último commit de cada caminho; não a confunde com decisão vigente ou validade técnica.

O verificador documental existente já falha na base com `Missing architecture reference: README.md`. Esta limpeza não altera README nem o teste para fabricar um PASS: a navegação/README pertence à PR #41. A ligação histórica para `MEMORIA-DE-TRABALHO.md` não tem alvo materializado; a fonte histórica não foi apagada ou reescrita.

Kernel/Host/Store, Folha, adaptadores, dependências, testes, workflows de CI e provas anteriores ficam fora do diff. Nenhuma branch de terceiros é apagada, fechada ou alterada; sem merge em main. **A limpeza não é aceitação do produto nem conclusão da cópia do PC.**
