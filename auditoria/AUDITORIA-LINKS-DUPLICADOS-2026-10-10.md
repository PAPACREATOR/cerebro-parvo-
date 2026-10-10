# Auditoria de ligações e duplicações — snapshot GitHub main (10-10-2026)

## Âmbito e método
- Fonte lida: árvore Git da branch `main`, SHA `aeeb6f662a8282b3793708aa3e6782ef20d2d0ca`, resposta `truncated=false`.
- 208 entradas totais, 177 blobs; 100 ficheiros Markdown lidos individualmente pelo conector GitHub.
- Em Markdown, localizaram-se referências relativas com a sintaxe `[texto](destino)`, `![alt](destino)` e definições `[ref]: destino`. Os destinos foram normalizados relativamente à pasta de origem e comparados à árvore de `main`.
- Verificação **estática/parcial**: não resolve URLs externas, âncoras `#...`, HTML `href`, wikilinks, ligações escritas apenas em prosa, ligações geradas dinamicamente ou ficheiros presentes apenas noutras branches/disco local. Não equivale a auditoria de completude do projeto ou do PC.

## Resultado da verificação estática
| Classe | Ficheiros Markdown lidos | Referências relativas encontradas | Destinos não encontrados |
| --- | ---: | ---: | ---: |
| Fora de `historico/` | 67 | 97 | 0 |
| Sob `historico/` | 33 | 2 | 1 |
| **Total** | **100** | **99** | **1** |

**Referência histórica em falta:** `historico/repositorio-2026-09-24/README.md`, linha 3, aponta para `MEMORIA-DE-TRABALHO.md` na mesma pasta. O caminho não consta da árvore da branch `main`. Por ser material histórico, **não criar conteúdo inventado, não apagar nem alterar a fonte**. Procurar o documento original no espelho local/Library quando o Codex concluir a cópia; se não existir, manter a referência marcada como não materializada numa nota de índice.

## Duplicações byte-idênticas na árvore Git
Dois pares de blobs têm o mesmo identificador Git (mesmo conteúdo como objeto Git):
- `implementacao/ativa-2026-09-28/cerebro/__init__.py` e `implementacao/candidata-2026-09-27/cerebro/__init__.py`; blob `bb67a43fa4e5791ab58e7e40260bc3df8b6bc7cc`.
- `implementacao/ativa-2026-09-28/cerebro/core.py` e `implementacao/candidata-2026-09-27/cerebro/core.py`; blob `e8747447b47a187d55f781a7e61a871c090a485a`.

**Não apagar:** pertencem a snapshots/versionamento de implementação distintos. Igualdade de blobs não autoriza eliminar documentação, provas ou versões históricas; não são duplicações do cofre de dados do utilizador.

## Divergência de estado atual e sobreposição evitada
- Em `main`, `README.md` e `DECISIONS.md` ainda refletem Conductor como executor candidato e simplificação de 30/09.
- A PR [#41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41) (aberta) propõe uma reconciliação de 09/10 e classifica Activepieces como referência, Conductor fora do produto candidato, Spiff apenas opcional e MCP Python como transporte subordinado ao Kernel.
- A issue [#33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) fixa a convergência do runtime `nexus/` com portões transacionais, sem presumir que a PR #31 e a PR #32 tenham as mesmas provas.
- **A PR #46 não deve editar `README.md`, `STATUS.md`, `DECISIONS.md` ou as secções de navegação da PR #41** para não criar alterações paralelas. Depois da consolidação, atualizar o índice com base num único HEAD e evidência de merge/revisão.

## Verificação adicional — secções de navegação da PR #41
- Ref analisada: `docs/external-navigation-20261009`, SHA `46c6b6722028017b5c174986128be4a151588ae7` (PR #41 aberta).
- Oito ficheiros da nova estrutura `docs/00-start-here`, `10-current`, `20-architecture`, `30-help`, `90-research` e `99-history` foram lidos.
- Catorze referências Markdown relativas analisadas; **zero destinos em falta** na árvore da própria PR #41, segundo o mesmo método estático.
- Esta amostragem não audita todos os restantes ficheiros adicionais daquela branch, nem âncoras, URLs externos e links noutras sintaxes. Não implica aprovação/merge.

## Limites de segurança da revisão
A inspeção de nomes de ficheiros não identificou nomes óbvios de credenciais na árvore `main`; **não** houve varrimento completo de conteúdo por segredos, dados pessoais, licenças ou binários do PC. Não fazer publicação adicional de dados do disco sem controlo prévio.

## Exclusões por decisão humana
Integração Sandy: **SUSPENSA** em 10/10/2026, mantendo apenas crédito histórico ao seu autor. Não criar tarefa de implementação ou testes Sandy. Codex mantém cópia local→GitHub e clonagem Sir Thaddeus em responsabilidade separada.

## Gate documental ainda não fechado
- [x] Listagem técnica estática da árvore `main` e 49 branches (ficheiros JSON na pasta `auditoria/` desta PR).
- [x] Verificação estática de destinos de links Markdown nos 100 documentos publicados em `main`.
- [x] Identificação e registo dos dois pares de blobs idênticos, sem eliminação.
- [ ] Resolver referência histórica com proveniência, quando houver fonte.
- [ ] Rever PR #41 e #45 no HEAD final e reconciliar autoridade documental sem duplicar trabalho.
- [ ] Validar cópia de PC / hashes e procurar documentos ausentes após entrega do Codex.
- [ ] Executar varrimento de dados sensíveis antes de qualquer exposição do espelho do PC.
- [ ] Validar links externos, âncoras e formatos não-Markdown se exigido para fecho total.

**Estado: PARCIAL.** Este relatório não prova o produto, segurança ou espelho completo.
