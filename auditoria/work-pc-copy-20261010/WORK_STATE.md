# Clonagem e inventário — execução Work, 10-10-2026

**Resultado da missão: PARCIAL. Fase 1 no PC e cópia PC → GitHub: BLOCKED / NOT RUN.**

O registo de clonagem abaixo corresponde ao commit `bc1935d9707c125509d914fd7eb3e4f35ec584a5`. A continuação de limpeza está em [CLEANUP.md](CLEANUP.md), com datas e verificações em `CLEANUP.json`.

Esta sessão dispõe de um ambiente Linux e acesso ao GitHub. Não dispõe de uma ligação ao filesystem ou shell do computador Windows de Pedro. `C:\Nexus`, `C:\Nexus-Tools` e outras raízes Windows não foram lidas, copiadas ou alteradas. A ausência desses caminhos no Linux não demonstra a sua ausência no PC.

## Operações efetivamente executadas

| Operação | Resultado observado | Limite |
|---|---|---|
| Clone Git completo de Nexus numa pasta Linux nova | Concluído; `is-shallow-repository=false`; `git fsck --full --strict` terminou com código 0 | Origem GitHub; não é backup do PC |
| Recolha de referências Git de Nexus | 49 branches remotas observadas, com SHA congelado no inventário | Não revela branches locais nem alterações não registadas do Windows |
| Inventário de seis árvores Nexus publicadas | 1.461 registos de ficheiro com caminho relativo, dimensão, Git SHA-1, SHA-256, classificação e indicação de componente | Ficheiros repetidos entre árvores são contados por árvore; não são 1.461 ficheiros distintos |
| Clone Git completo de Sir Thaddeus | Concluído no Linux; 1.029 commits alcançáveis nas refs recolhidas; checkout detached no SHA abaixo | Não foi clonado no Windows |
| Verificação da árvore Sir Thaddeus | 1.446/1.446 ficheiros comparados byte a byte com os blobs Git; checkout limpo; `git fsck --full --strict` código 0 | Não foram instaladas dependências, descarregados assets de releases, compilados projetos ou executados programas/testes do projeto |
| Comparação de duplicados públicos | 16 grupos dentro dos snapshots, confirmados byte a byte | Grupos repetidos entre snapshots; nenhuma eliminação |
| Divergência/ausência entre seis árvores públicas | 288 caminhos com versão diferente ou ausentes em pelo menos uma árvore | Não comprova ficheiros ausentes no PC |
| Triagem de segredos nos blobs públicos inventariados | Zero correspondências em três padrões: chave privada, formato de token GitHub e access key AWS | Heurística incompleta; não autoriza publicar ficheiros privados nem prova ausência de segredos/dados pessoais |
| Preservação da baseline nesta cópia | 177/177 ficheiros de `main` iguais byte a byte; diff dos ficheiros existentes vazio | Só adições nesta pasta de auditoria; nenhum transplante de runtime |

## Fontes congeladas

| Repositório/ref | SHA | Ficheiros | Bytes dos blobs |
|---|---|---:|---:|
| Nexus `main` | `aeeb6f662a8282b3793708aa3e6782ef20d2d0ca` | 177 | 716.279 |
| Nexus PR #32, `cleanup/llamacpp-only-20261007` | `da86b6dd181d00fd7a87addaa01a12ec3a14e57b` | 366 | 2.056.532 |
| Nexus PR #45, `integration/nexus-unified-candidate-20261009` | `66027af7f2ea084bc62d85b840d1fc3113e60a97` | 372 | 2.094.116 |
| Nexus PR #46, `audit-consolidation-20261010` | `979a4cbfc374fa02589bb6c8042b962da6b266a3` | 182 | 777.179 |
| Nexus `pc-full-mirror-20261004` | `1e9e6127564a9247e562029552f73d56a8b9d3a7` | 175 | 714.480 |
| Nexus `pc-snapshot-tooling-20261004` | `7cc6a05d358d988c1bcd71486aaee51d3741eaf6` | 189 | 797.092 |
| Sir Thaddeus `master` | `974b5d7d258a687f99062425ef40e54b1eefc034` | 1.446 | 33.668.703 |

`main` serve apenas de pai desta branch de evidência; não foi escolhido como nova baseline de produto. A linha candidata e os laboratórios concorrentes mantêm os seus próprios estados.

Sir Thaddeus: origem [raydeStar/sir-thaddeus](https://github.com/raydeStar/sir-thaddeus), árvore `e935afeb228955bc6c43d0290012c98146d4f891`. A licença original `LICENSE` foi preservada no clone; SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`. Nenhuma parte do código foi integrada no Nexus.

## Constatação sobre os espelhos anteriores

O HEAD de `pc-full-mirror-20261004` é um commit documental que altera `STATUS.md`, `nexus/docs/PONTO-DE-SITUACAO.md` e `nexus/docs/WIKI-INSTALACAO.md`. O nome da branch não prova que represente todos os bytes do Windows.

Na branch `pc-snapshot-tooling-20261004`, `nexus/mirror/PC-SNAPSHOT-STRUCTURE.md` declara: “Estado: estrutura apenas. Ainda não executa cópia nem recolha.” O manifesto é um template com branch/commit/contagens/hashes por preencher e operações `NOT_RUN`. Não foi encontrado nesse material um inventário preenchido que permita verificar a cópia integral do PC.

## Identificação de componentes

Os CSVs classificam fonte, documentação, histórico, teste/evidência, configuração e dados/binários sujeitos a revisão. `component_hint` é uma indicação por caminho, não uma decisão arquitetónica nem prova de funcionamento.

Nas árvores #32/#45 constam `nexus/host.py`, `nexus/store.py`, `nexus/app.py`, `nexus/frontdoor.py`, regras/schemas, adaptadores e suites. As implementações anteriores em `implementacao/` permanecem registadas como versões distintas. A lógica ativa de Kernel/Host/Store, a Folha e as dependências não foram modificadas nem testadas nesta missão de cópia.

## Ficheiros de evidência

- `public-source-summary.json`: referências, contagens, dimensões, componentes e limites de cobertura.
- `public-inventory.zip`: `nexus-public-files.csv`, `sir-thaddeus-files.csv`, `exact-public-duplicates.json`, `public-branch-divergences.json` e `public-secret-triage.json`.
- `EVIDENCE.json`: operações, verificações e condições objetivas para continuar.
- `SHA256SUMS.txt`: integridade dos entregáveis desta pasta.

Os inventários contêm apenas metadados de fontes já públicas. Não contêm bytes de documentos pessoais, valores de credenciais, ficheiros `.env`, configurações privadas, cofres ou bases do PC. Não foi feita autorização automática de publicação.

## Continuação obrigatória — não saltar a Fase 1

1. Executar a recolha numa sessão efetivamente ligada ao Windows, com leitura de `C:\Nexus`, `C:\Nexus-Tools` e descoberta delimitada de outras raízes Nexus. Registar erros/permissões/reparse points sem os ocultar.
2. Guardar o inventário completo privado: caminhos reais, dimensões, SHA-256, estado Git, ficheiros ignorados/não rastreados, duplicados byte a byte, versões e exclusões. Não imprimir segredos nem publicar o inventário privado automaticamente.
3. Comparar os ficheiros reais com refs GitHub explicitamente escolhidas; não inferir equivalência a partir da branch ou do nome de um ficheiro. Ficheiros alterados durante a recolha exigem nova leitura/verificação.
4. Antes de qualquer alteração a ficheiros existentes, guardar e verificar cópia de segurança. Nesta sessão só foram criadas pastas/clones e entregáveis novos; instalações existentes não foram acessíveis.
5. Publicar exclusivamente o conteúdo versionável revisto numa branch nova, preservando as instalações, alterações locais e branches dos outros. Sem merge, force-push, reset destrutivo, Sandy, Activepieces ou execução Sir Thaddeus.
6. Verificar remotamente, por caminho e hash, cada ficheiro publicado e registar os excluídos/pendentes. Só então declarar a fase de cópia concluída.

Até existir essa evidência: **inventário Windows, diferenças PC/GitHub, backup do PC e cópia integral PC → GitHub continuam NOT RUN. Sem PASS global.**
