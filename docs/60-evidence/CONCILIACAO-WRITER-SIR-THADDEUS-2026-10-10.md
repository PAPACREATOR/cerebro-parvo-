# 10/10/2026 — Reconciliação de provas: Writer, Sir Thaddeus e equipas

**Natureza:** inventário documental de provas externas consultadas, **não** teste executado pela frente documental e **não** certificação do Windows pessoal. Fotografias de commits e execuções; voltar às fontes antes de alterar o estado. **Código, Kernel, Host, Store, sandbox e workflows não foram modificados nesta PR.**

## O que realmente avançou

| Frente isolada | Fonte e SHA | Prova observada | Não demonstrado |
| --- | --- | --- | --- |
| **Sir Thaddeus — clone de referência** | [PR #48 Nexus](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48), SHA `37212f2b82d0cd4bcf2118cc4ec549a7c1da7726`, [relatório](https://github.com/PAPACREATOR/cerebro-parvo-/blob/37212f2b82d0cd4bcf2118cc4ec549a7c1da7726/auditoria/work-pc-copy-20261010/WORK_STATE.md) | Git clone completo **no Linux**, upstream `raydeStar/sir-thaddeus` SHA `974b5d7d258a687f99062425ef40e54b1eefc034`, `git fsck --full --strict` código 0, **1.446/1.446 ficheiros** do checkout comparados byte a byte, 1.029 commits alcançáveis nas refs recolhidas | Instalação, compilação, execução, MCP real, integração Nexus ou clone no **PC Windows** |
| **Nexus — inventário remoto** | [PR #48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48), [EVIDENCE.json](https://github.com/PAPACREATOR/cerebro-parvo-/blob/37212f2b82d0cd4bcf2118cc4ec549a7c1da7726/auditoria/work-pc-copy-20261010/EVIDENCE.json) | Seis árvores GitHub inspecionadas, **1.461 registos por versão** (não 1.461 únicos); 177/177 ficheiros de `main` preservados na experiência; duplicação analisada | Inventário e backups de `C:\Nexus`; cópia total PC→GitHub; limpeza física Windows (**BLOCKED / NOT RUN**) |
| **Writer — causa de namespace LPAC** | [PR #1 Writer Lab](https://github.com/PAPACREATOR/nexus-writer-lab/pull/1), [Windows run 37961395133](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/37961395133), SHA `2b671ab3905b81e012b267dc8e4fb37ec25cac42` | Em conta Windows standard e token LPAC real, `CreateNamedPipeW` no namespace legado devolve **WinError 5**; em `\\.\pipe\LOCAL\` devolve **PASS**. Rede bloqueada e Job sem processos órfãos no ensaio | Writer gerar PDF real dentro da mesma sandbox. O ensaio diferencial foi sintético, **não** uma conversão Writer |
| **Writer — protótipo de fonte** | [PR #1](https://github.com/PAPACREATOR/nexus-writer-lab/pull/1), [run 37962399314](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/37962399314), SHA `7eaf59e4e979a0dde1692528fc76f4240d4b0f76` | Protótipo de alteração **condicional** para namespace `LOCAL` apenas com token AppContainer, e testes estáticos PASS | **Não** compilou LibreOffice nem executou `book`/`convert_pdf` |
| **Writer — solução Sandy em ensaio A/B** | [PR #2 Writer Lab](https://github.com/PAPACREATOR/nexus-writer-lab/pull/2), SHA `fa8d65c4f62596738fd19b33c9419e1caa0b936a`, [CONTRACT.md](https://github.com/PAPACREATOR/nexus-writer-lab/blob/fa8d65c4f62596738fd19b33c9419e1caa0b936a/lab/sandy-local-pipes/CONTRACT.md) | Nova experiência com a solução pública de **Hrvoje Abraham**: Sandy v0.9994 com release hash fixado; conta standard, Writer 26.2.6.2, comparação sem e com renomeação de pipes para `LOCAL` | No instante da consulta, [run Windows 38047795468](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795468) estava **IN PROGRESS**; sem conclusão A/B e **sem PASS de PDF**. Revisitar a execução antes de declarar resolvido |
| **Candidato Nexus** | [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), SHA `66027af7f2ea084bc62d85b840d1fc3113e60a97` | Integração experimental de `verify` natural e confirmação pré-execução; gates parciais descritos na PR | Não inclui a solução do Writer Lab; PR Draft, sem prova global de release |

**CI transversal no Writer Lab PR #2:** [auditoria e suites 38047795447](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795447) **SUCCESS**; [CodeQL 38047795406](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795406) **SUCCESS** no SHA acima. Esses dois resultados **não substituem o resultado do job de conversão A/B**, que estava em curso na consulta.

## Atualização factual — run A/B concluído com FAIL

**Resultado terminal do primeiro ensaio da PR #2:** [run 38047795468](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795468), SHA `fa8d65c4f62596738fd19b33c9419e1caa0b936a`, terminou **FAIL** em 10/10/2026 às 11:20 UTC. [Artefacto preservado](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795468/artifacts/11668422448).

Os logs do job `compare` mostram:

- `synthetic_unrestricted_preparation: PASS`: preparação sintética fora do LPAC concluída.
- Caso **A sem mapeamento do pipe:** Writer lançado sob token AppContainer+LPAC real, mas conversão **FAIL**, prazo de execução **43 segundos** atingido; `pipe_observed=false`.
- `writers_terminated=false` e `dacls_unchanged=false` na verificação após o caso A; a rotina de recuperação devolveu código 0 e o container foi desregistado, mas isso **não basta** para declarar ausência de processos restantes ou igualdade de ACLs.
- O próprio ensaio recusou iniciar **B com mapeamento `LOCAL`**, antes do restauro de perfil, porque não estavam demonstradas as condições de terminação/limpeza de A: `A cleanup/termination not proved; B refused before profile restoration`.
- **Conclusão exata:** o run falhou de forma conservadora; **não existe resultado para B**, logo não se pode dizer que a solução Sandy falhou a conversão B, nem que a resolveu. Host/Human Gate, `book`/`convert_pdf` em produção, rede/clipboard/filhos comportamentais, 100+100 regressões e PC pessoal mantêm-se NOT RUN.

**Continuação identificada noutra branch, sem interferência documental:** a PR #2 avançou depois para SHA `40d29078c9b77a35466956b2dbd3399dd7d2f454`, alterando apenas o ensaio `lab/sandy-local-pipes/compare.py` para aguardar terminação real dos filhos dentro do prazo e gravar as DACL antes/depois. Novo [run Windows 38048136938](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38048136938) estava **IN PROGRESS** na consulta. A [auditoria 38048136989](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38048136989) terminou SUCCESS no novo SHA; isso não certifica B. Consultar o HEAD atual antes de nova conclusão.

## Sandy: duas decisões que não se contradizem

1. **Integração de Sandy no Host/candidato Nexus: SUSPENSA.** Não existe autorização para introduzir dependência, relaxar LPAC/Job/ACL, fazer merge de outro executor ou instalar Sandy no PC por esta revisão.
2. **Experiência isolada Writer/Sandy na PR #2: REALIZADA COMO CANDIDATO DE TESTE.** O contrato do laboratório regista o pedido humano de 10/10/2026. O uso do launcher de Hrvoje Abraham numa bancada descartável **não reabre por si a decisão de integração**.

O autor e a licença MIT do material do Sandy têm de ser preservados. Nunca reproduzir correspondência pessoal ou credenciais na documentação pública.

## O que permitiria declarar «Writer resolvido»

Um **PASS de conversão de documento sintético em PDF real** no ambiente Windows isolado, sob token LPAC/AppContainer e Job equivalente, dentro de 45 segundos, com PDF validado e extração de texto, no SHA e logs especificados. Ainda assim, seria **PASS da bancada**, não do produto.

Para dizer «Writer integrado no Nexus»: integrar por outra equipa autorizada; demonstrar `book` e `convert_pdf` reais pela fronteira Host e os gates de autoridade, proveniência, rede, filhos, clipboard, integridade, crash/recovery, regressão e Windows físico aplicáveis — **no mesmo SHA**. A pessoa continua a aprovar alterações e promoção Canonical.

## Responsabilidades sem sobreposição

- **Frente documental — PR #49:** interpretação das provas, navegação, histórico, links, ADRs. Nunca modifica runtime, testes, scripts, Kernel/Host/Store ou outras branches.
- **PR #48 — Work/cópias:** histórico e clonagem Git Linux; ainda não equivale a inventário privado do Windows.
- **Writer Lab — PRs #1/#2:** diagnóstico técnico e ensaios de isolamento. Não alterar nem incorporar o seu código pela frente documental.
- **Candidato principal — PR #45:** integração experimental separada, ainda Draft; só incorporar correção do Writer depois de ensaios e autorização.
- **Folha Lab — [PR #5](https://github.com/PAPACREATOR/nexus-folha-lab/pull/5):** outro laboratório, com provas próprias, não automaticamente incorporado na PR #45.

## Leituras e condição da fotografia

[Estado atual Nexus](../10-current/ESTADO-DOCUMENTAL-2026-10-10.md) · [Compatibilidade por SHA](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) · [Matriz de PRs](MATRIZ-PRS-2026-10-10.md) · [Índice histórico outubro](../99-history/2026-10/README.md).

**Esta nota contém duas fotografias documentais de 10/10/2026:** o estado inicial `IN PROGRESS` do SHA `fa8d65c4` e o subsequente **FAIL real**, com correção laboratorial em novo SHA `40d29078` ainda em ensaio no momento da última consulta. A leitura posterior deve seguir o último run aplicável; nunca converter IN PROGRESS ou NOT RUN em PASS por antecipação.
