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

**Esta nota é fotografia documental de 10/10/2026, antes do resultado terminal do ensaio A/B.** Resultados posteriores exigem ligação a run, SHA, relatório e mudança de estado explícita; nunca converter por antecipação IN PROGRESS ou NOT RUN em PASS.
