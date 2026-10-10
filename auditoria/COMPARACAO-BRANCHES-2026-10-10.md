# Divergência de branches — inventário documental do GitHub em 10-10-2026

**Objetivo:** mostrar por que razão a branch `main` não basta para declarar «tudo está no GitHub» ou «o Nexus está unificado». É uma fotografia verificável dos caminhos publicados, não valida código nem copia o PC.

## Comparação de árvores Git (blobs/fichas)
| Ref consultada | SHA de referência | Ficheiros publicados | Caminhos apenas nessa ref versus `main` | Caminhos presentes em `main` mas ausentes nessa ref |
| --- | --- | ---: | ---: | ---: |
| `main` | `aeeb6f662a8282b3793708aa3e6782ef20d2d0ca` | 177 | 0 | 0 |
| `docs/external-navigation-20261009` (PR #41) | `46c6b6722028017b5c174986128be4a151588ae7` | 374 | 211 | 14 |
| `integration/nexus-unified-candidate-20261009` (PR #45) | `66027af7f2ea084bc62d85b840d1fc3113e60a97` | 372 | 209 | 14 |
| `pc-full-mirror-20261004` | `1e9e6127564a9247e562029552f73d56a8b9d3a7` | 175 | 0 | 2 |

As contagens comparam **caminhos**, não diferenças de conteúdo dos caminhos partilhados. As árvores destas quatro refs indicaram `truncated=false`. O «full mirror» datado de 04/10 é mais antigo do que `main` e não prova a cópia atual do PC.

## Comparação documental precisa — PR #41 e PR #45

Os documentos Markdown foram comparados por caminhos e hashes de blob Git:
- PR #41: 149 ficheiros Markdown; PR #45: 142 ficheiros Markdown.
- **137 caminhos apresentam bytes idênticos** em ambas as branches, comprovados pelo mesmo blob SHA Git.
- Quatro caminhos diferem em conteúdo: `CONTRIBUTING.md`, `DECISIONS.md`, `README.md`, `STATUS.md`.
- PR #45 acrescenta `nexus/docs/WINDOWS-ACCEPTANCE-ISOLATED.md`, ausente na PR #41.
- Os oito documentos de navegação `docs/00-start-here`, `10-current`, `20-architecture`, `30-help`, `90-research`, `99-history` pertencem à PR #41 e não surgem na árvore da PR #45.
- Os **cinco documentos exclusivos/alterados da PR #45** foram lidos, com **11 referências relativas Markdown e 0 destinos ausentes**, excluindo blocos de código e código inline.
- Não declarar validação completa dos 142 documentos da PR #45: os 137 partilhados não foram todos testados contra as diferenças de caminhos entre as branches. As 11 falhas históricas identificadas na PR #41 requerem conferência na PR #45.

Consultar [manifesto por caminho/blob](MANIFESTO-DOCUMENTOS-BRANCHES-2026-10-10.json) para reprodução. Estas conclusões não integram nem aprovam código.

## Riscos documentais concretos
- **Main incompleta face ao candidato:** a PR #41 e a PR #45 contêm centenas de caminhos adicionais, incluindo testes, contratos, relatórios e documentação de continuidade. Não migrar nem apagar por comparação apenas com `main`.
- **Conflito de estado arquitetural:** `main` ainda expõe Conductor como candidato; a documentação de 09/10 na PR #41 considera Kernel/Host/Store + MCP Python sem Activepieces ou Conductor como requisitos de runtime. A issue #33 exige verificação no mesmo SHA antes de declarar produto único.
- **Sobreposição das PRs:** a PR #41 altera documentação de entrada e navegação; a PR #45 altera runtime/testes Windows. A PR #46 fica reservada à auditoria documental sem reescrever as outras.
- **Referência histórica ausente:** `historico/repositorio-2026-09-24/README.md` aponta para `MEMORIA-DE-TRABALHO.md`, ausente destas árvores consultadas; não inventar o conteúdo.
- **Dados privados:** conteúdo local, bases SQLite, modelos, contas e segredos não devem ser enviados para o repositório público sem filtragem; o inventário Git não demonstra que isso tenha sido feito.

## Próxima reconciliação permitida
1. Acompanhar Codex e recolher o SHA/manifestações verificáveis da cópia local, incluindo hashes e mapa de exclusões de ficheiros sensíveis.
2. Escolher o HEAD candidato de integração, sem fazer merge automático; confrontar `main`, PR #41, PR #45 e restantes PRs relevantes, preservando garantias.
3. Atualizar o índice de vigência documental para o HEAD escolhido e repetir a análise de links aí, incluindo novos documentos.
4. Só declarar Fase 1 concluída quando toda a documentação selecionada e o manifesto do PC tiverem proveniência, localização e estado coerentes.

**Sandy:** integração suspensa por instrução humana; o reconhecimento a Hrvoje Abraham mantém-se histórico.

**Estado da fase:** PARCIAL. Nenhum ficheiro do runtime foi modificado por esta comparação.
