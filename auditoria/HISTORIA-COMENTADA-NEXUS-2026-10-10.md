# História comentada do Cérebro / Nexus — 22-09 a 10-10-2026

**Estado:** estudo documental auditável, de âmbito histórico. **Não** é Constituição nova, decisão arquitetural, licença para instalar componentes, relatório de PASS global ou confirmação de cópia do PC.

**Objetivo:** permitir que um colaborador compreenda *por que razão* o Nexus evoluiu, *o que se preservou*, *o que foi substituído* e *onde está a prova*. Complementa [docs/GENEALOGIA.md](../docs/GENEALOGIA.md), que descreve sobretudo as etapas até 27/09, sem alterar arquivos ou falsear datas.

**Fotografia de referência:** 10-10-2026. A árvore `main` consultada foi `aeeb6f662a8282b3793708aa3e6782ef20d2d0ca`. PRs abertas são propostas e provas da sua branch; não fazem automaticamente parte de `main`. Consultar [inventários por SHA](MANIFESTO-DOCUMENTOS-BRANCHES-2026-10-10.json) e [estado da Fase 1](FASE-1-INVENTARIO-DOCUMENTAL-2026-10-10.md).

## Ler a história sem confundir versões

1. **Origem/proposta:** aquilo que uma fonte defendia *na sua data*, mesmo que utilize «final», «atual» ou «PASS».
2. **Decisão humana posterior:** pode substituir a composição técnica anterior, não apaga o motivo nem as evidências da escolha original.
3. **Implementado numa branch:** código/contratos existentes nesse SHA; não garante integração noutra branch.
4. **Testado:** resultado limitado ao teste, sistema operativo, dados e SHA indicados. Uma suite verde não é produto completo.
5. **Integrado/aceite:** exige candidato único, gates relevantes no mesmo HEAD, revisão e aceite humano; PC físico tem aceitação separada.
6. **Reservado/não publicado:** ausência no GitHub não autoriza criar um substituto nem publicar fontes locais potencialmente privadas.

## Cronologia fundamentada

| Período | Pergunta / dificuldade | Solução ou estudo daquele momento | O que sobreviveu / o que mudou | Fonte e limite |
| --- | --- | --- | --- | --- |
| **22/09** | Escrever naturalmente e impedir que pesquisa/IA alterem conhecimento aprovado | Logseq Classic como superfície criativa, Activepieces, dois domínios SQLite e cofre final protegido | Autoridade humana, Creative/Canonical, proveniência, persistência e decisão explícita permanecem; a topologia concreta foi depois substituída | [Decisões de 22/09](../historico/repositorio-2026-09-24/DECISIONS.md), [mapa de cofres e versões](../historico/repositorio-2026-09-24/MAPA-DE-VERSOES-COFRES-ACTIVEPIECES.md). O mapa descreve alterações dentro do próprio dia |
| **23/09** | Como usar cognição sem lhe delegar autoridade | Estudo Soar/ACT-R, memórias, comparadores, pesquisa, sandbox Windows e inspiração ELIZA | Três memórias/comparadores como papéis lógicos; saída IA = proposta; isolamento e decisão humana | [Decisões históricas](../historico/repositorio-2026-09-24/DECISIONS.md), [nota cognitiva](../historico/repositorio-2026-09-24/NOTA-COGNITIVA-MEMORIAS-COMPARADORES-LINGUAGEM-NATURAL-2026-09-23.md), [estudo AppContainer/LPAC](../historico/repositorio-2026-09-24/PESQUISA-SANDBOX-WINDOWS-APPContainer-LPAC-2026-09-23.md). Estudo ≠ confinamento implementado |
| **24/09** | Reduzir manutenção e número de programas necessários | Joplin substitui Logseq como UI candidata; Activepieces deixa de ser requisito; Core Python, Markdown/EventLog/SQLite, tiny NL→Proposal | UI deve ser substituível, SQLite não precisa ser duplicado, IA não pode decidir | [Migração de 24/09](../historico/repositorio-2026-09-24/MIGRACAO-ARQUITETURAL-2026-09-24.md), [DECISIONS original](../historico/repositorio-2026-09-24/DECISIONS.md). Joplin foi depois substituído como opção principal de UI |
| **26/09** | Interface demasiado técnica; falta de contrato completo de comportamento | Folha Única e descrição M1–M14, regras de importação IMP-001–026, microprocessos, testes de falha e recuperação | **Folha** sem Markdown/IDs visíveis; Kernel e leis não dependem da UI; preservar bytes, hashes, versões, eventos, Creative/Canonical, comparadores e Human Gate | [Prompt mestre congelado em 26/09](../docs/baseline/CEREBRO_PROMPT_MESTRE_CURSOR_2026-09-26.md). Baseline conceptual, não implementação de todos os IMP |
| **27/09** | Recuperar e testar protótipo de ingestão de fontes | Candidato de nove ficheiros, contratos de importação, revisão adversarial e reconciliação de contradições dos resumos | FAIL e bloqueios preservados; não declarar IMP-001 ou M1–M14 concluídos com a suite parcial | [Reconciliação](../docs/RECONCILIACAO.md), [implementação candidata](../implementacao/README.md), [resultados](RESULTADOS.md), [inventário histórico](../docs/INVENTARIO-HISTORICO.md). Copiar ficheiros sem perdas não equivale a completar o produto |
| **28/09** | Reutilizar o máximo de ferramentas maduras | Activepieces Community + Memory Provider/MCP como blocos candidatos; OpenNotebook e outras ferramentas por capacidades | «LIGAR > CONFIGURAR > ADAPTAR > CRIAR» sobrevive; a plataforma específica foi superada | [Plano datado de 28/09](../docs/PROJETO-FINAL-AUDITADO-2026-09-28.md), [matriz P01–P16](../docs/PENDENCIAS.md). **“Final” no título é histórico**, não release |
| **30/09** | Evitar que workflow engine ou notebook sejam proprietários da memória | Nexus Minimal, Folha, Conductor **candidato** e Open Notebook como bancada descartável | Memória soberana Nexus, capacidades desmontáveis, pequenos processos reutilizáveis; a escolha de executor ainda iria evoluir | [DECISIONS na main de 30/09](../DECISIONS.md). As palavras «vigente» no texto são relativas àquela versão da main |
| **01–04/10** | Arranque Windows, ferramentas reais, recuperação e navegação de conhecimento | Núcleo e Host Windows, LanguageTool, PDF Writer, experiências Spiff+Conductor, wiki e Front Door em laboratórios; suites e problemas registados | Reusar capacidades reais e preservar gates. Uma wiki validada em laboratório não está automaticamente integrada na Folha e no Host | [Ponto de situação por versões](../nexus/docs/PONTO-DE-SITUACAO.md), [F007](../nexus/docs/F007-LIBREOFFICE.md), [F008](../nexus/docs/F008-ISOLAMENTO-WINDOWS.md), [PR #17](https://github.com/PAPACREATOR/cerebro-parvo-/pull/17) |
| **04–05/10** | Remover dependências redundantes sem perder autoridade/recovery | [PR #21](https://github.com/PAPACREATOR/cerebro-parvo-/pull/21) propôs runtime Python mínimo, sem Conductor/Spiff/YAML como executor; MCP Python e adaptadores delimitados | Kernel/Host/Store, Creative/Canonical, transporte MCP sem IA, documentação técnica comparativa preservada | PR #21 **fechada, não integrada por merge**: evidência e SHA de branch, não prova sobre a `main`; consultar também [PR #23](https://github.com/PAPACREATOR/cerebro-parvo-/pull/23) |
| **06–08/10** | Convergir persistência e Windows em vez de manter dois produtos paralelos | [PR #31](https://github.com/PAPACREATOR/cerebro-parvo-/pull/31) auditou Core transacional; [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32) candidata Windows, sem transplantar automaticamente o Kernel antigo; [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) governa convergência; [PR #34](https://github.com/PAPACREATOR/cerebro-parvo-/pull/34) reconcilia documentação | Provas de atomicidade, recusa, replay, idempotência e fronteira LPAC a manter; **Writer Windows ainda apresentou FAIL**; não há PASS global nem aceitação do PC | As PRs têm bases e HEADs distintos. Resultados de uma branch não validam outra |
| **09/10** | Linguagem natural acessível, risco de executar sem confirmação, integração única | [PR #43 — Work](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43) liga apenas `verify` a confirmação pré-execução; [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45) candidata integrada Draft; [PR #41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41) prepara navegação de colaboradores | Confirmação pré-execução distinta de Creative→Canonical; bypass anterior de `/api/run` registado e posteriormente corrigido, ainda dependente de gates e revisão | [Comentários da PR #43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43). PR #45 é laboratório de integração, não release |
| **09–10/10** | Aproveitar trabalho externo em vez de reconstruir UI/Windows; preservar contribuições | [Sir Thaddeus](https://github.com/raydeStar/sir-thaddeus) estudado para *possível* reutilização técnica; [Sandy CLI](https://github.com/ahrvoje/sandy_cli) contribuiu investigação LPAC/LibreOffice por Hrvoje Abraham | Não substituir autoridade do Kernel/Host por executores terceiros. Clonagem de Sir Thaddeus atribuída ao Codex; **integração Sandy suspensa** por decisão humana | [Investigação da PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45) e [crédito/Sandy suspenso](CONSOLIDACAO-2026-10-10.md). Estudo ≠ integração, contribuição externa ≠ coautoria Nexus |
| **10/10** | Evitar documentação incoerente e conflitos entre agentes | [PR #46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46) apenas com `auditoria/`: manifestos Git, análise de links, árvore/branches, índices de vigência e triagem de exposição parcial | Manter `main`, PR #41, Work/Codex e runtime intocados; consolidar apenas após verificação do espelho PC e HEAD definitivo | [Fase 1](FASE-1-INVENTARIO-DOCUMENTAL-2026-10-10.md), [comparação de branches](COMPARACAO-BRANCHES-2026-10-10.md). Ainda parcial |

## Evolução por decisão — aquilo que não deve ser ressuscitado por engano

| Tema | Alternativas datadas | Situação de leitura em 10/10 | Qual é a continuidade? |
| --- | --- | --- | --- |
| **Superfície humana** | Logseq (22/09) → Joplin (24/09) → Folha Única (26/09) | Folha é a intenção humana atual; Logseq/Joplin não são interfaces obrigatórias | Ocultar formatos técnicos sem remover proveniência/segurança |
| **Execução** | Activepieces → Conductor/Spiff investigados → Kernel/Host/Store Python com adaptadores | Na [PR #41, DECISIONS atualizado](https://github.com/PAPACREATOR/cerebro-parvo-/blob/docs/external-navigation-20261009/DECISIONS.md), Activepieces e Conductor não são dependências candidatas; Spiff laboratório opcional. Isto ainda não é merge em `main` | Autoridade do Kernel; prova de comportamento antes de escolher executor |
| **Persistência** | Dois SQLite físicos → cofres lógicos Creative/Canonical + EventLog/estado/indexação SQLite | Não inferir dois serviços ou duas bases apenas porque são dois cofres | Original byte-a-byte, SHA, genealogia, eventos, recovery, aprovação |
| **IA** | Tiny efémera NL→proposta → OpenNotebook delimitado por tarefa + tiny eventual | Ferramenta auxiliar, nunca dona de memória, regras ou Canonical; Ollama não é requisito | Processo determinístico quando chega; IA só dentro do escopo autorizado |
| **Conhecimento/wiki** | Logseq grafo → estudos GBrain/Will/Pith → Wiki/FTS5 e índices reconstruíveis | Benchmarks e laboratórios não são E2E da Folha | Três memórias, três comparadores, relações/proveniência em ambas as direções |
| **Isolamento Windows** | Estudo AppContainer/LPAC → provas em laboratórios/Host → problemas Writer reais | Um PASS sintético ou CI não valida a máquina pessoal | Proteção Windows como fronteira limitada, fail-closed e sujeita a teste |
| **MCP** | Mecanismo possível → validação stdio Python sem IA → transporte opcional/limitado | Não recebe Store, Canonical nem política. Nem toda ferramenta exige MCP | Kernel valida antes/depois da chamada |
| **Sir Thaddeus / Sandy** | Estudos externos de 09/10 | Sir Thaddeus sob clonagem Codex; Sandy **suspenso**; nenhuma integração aprovada por esta PR | Atribuir corretamente, fixar fonte/versão/licença antes de qualquer reutilização |

## O que nunca foi descartado

A evolução das bibliotecas e runtimes **não revogou** estes princípios: finalidade e autoridade humanas; invariantes M1–M14; Folha como experiência principal; Creative e Canonical com portão humano; três memórias e três comparadores como responsabilidades; bytes e fontes preservados; proveniência, eventos, integridade, atomicidade, replay e recovery; regras/contratos; decisões explícitas perante contradição e incerteza; recusa segura; mínima dependência de IA e ausência de publicação não aprovada. O conteúdo normativo exato deve ser lido na Constituição/contratos aplicáveis ao HEAD selecionado — este quadro é guia, não substituto.

## Não confundir PASS, histórico e entrega

- [PR #17](https://github.com/PAPACREATOR/cerebro-parvo-/pull/17): relatou PASS remoto em laboratórios, incluindo wiki, mas a wiki **não estava integrada no produto oficial**; a PR foi fechada sem merge.
- [PR #21](https://github.com/PAPACREATOR/cerebro-parvo-/pull/21): testes de simplificação Python declarados na branch, mas PR fechada sem merge.
- [PR #31](https://github.com/PAPACREATOR/cerebro-parvo-/pull/31): provas transacionais para o núcleo antigo não transferem automaticamente cobertura ao runtime `nexus/`.
- [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32): 8 SUCCESS / 1 FAIL Writer Windows no SHA declarado; sem aprovação global.
- [PR #43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43): um bypass pré-execução foi encontrado num SHA e corrigido em outro; consultar os gates **do SHA exato** antes de aceitar.
- [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45): candidato integrado ainda Draft, sem aceitação total.
- [PR #46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46): auditoria documental, não testa Windows nem publica o espelho local.

**Regra:** nunca somar contagens entre suites repetidas, sistemas diferentes ou commits diferentes. Um documento antigo que diz «final» não equivale a um produto entregável em 10/10.

## Mapa de localização e preservação

| O que procurar | Local |
| --- | --- |
| 35 ficheiros originais do snapshot de 24/09, com proveniência | [inventário histórico](../docs/INVENTARIO-HISTORICO.md) + [manifesto SHA-256](manifesto-preservacao.json) |
| Texto original da mudança Logseq/Activepieces → Joplin/Python | [migração 24/09](../historico/repositorio-2026-09-24/MIGRACAO-ARQUITETURAL-2026-09-24.md) |
| Constituição conceptual, M1–M14 e 26 microprocessos | [prompt mestre 26/09](../docs/baseline/CEREBRO_PROMPT_MESTRE_CURSOR_2026-09-26.md) |
| Lacunas, correções IMP e revisões de 27/09 | [reconciliação 27/09](../docs/RECONCILIACAO.md) + [resultados de auditoria](RESULTADOS.md) |
| Histórico de ideias Activepieces, memória e providers | [proposta 28/09](../docs/PROJETO-FINAL-AUDITADO-2026-09-28.md) e [decisões 30/09](../DECISIONS.md) |
| Registos e handoffs de 04/10 que estão apenas noutra branch | [árvore de evolução na PR #41 (SHA fixo)](https://github.com/PAPACREATOR/cerebro-parvo-/tree/46c6b6722028017b5c174986128be4a151588ae7/historico/evolucao-2026-10-04) |
| Contratos de ferramentas e evidência Windows | [nexus/docs](../nexus/docs/) e PRs específicas do laboratório/integração |
| Ordens de Work, Codex e PRs em concorrência | [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33), [PR #43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45) |
| Política de documentação e divergências abertas | [índice de vigência](INDICE-DE-VIGENCIA-DOCUMENTAL-2026-10-10.md) + [audit links/branches](PR41-AUDITORIA-LIGACOES-2026-10-10.md) |

## Proveniência dos originais preservados em 27/09

O [manifesto de preservação](manifesto-preservacao.json) existente em `main` contém **47 entradas** com caminho, origem declarada e campo SHA-256 de 64 algarismos hexadecimais:

| Grupo original | Entradas do manifesto | Proveniência declarada |
| --- | ---: | --- |
| `historico/repositorio-2026-09-24/` | **35** | GitHub `main@83d478a982cfb515e7bd90b86a7d502b0965ca57` |
| `docs/baseline/` | **3** | Ficheiros Markdown recuperados da Library em 26/09 |
| `implementacao/candidata-2026-09-27/` | **9** | ZIP revisto de 27/09, preservado como candidato, não release |
| **Total** | **47** | Três origens diferentes; não são 47 versões do mesmo documento |

Nesta auditoria verifiquei a **estrutura JSON do manifesto, a existência dos 47 caminhos na árvore publicada de `main` e o formato dos campos SHA-256**. **Não recomputei os SHA-256 dos 47 conteúdos a partir dos bytes originais**, nem comparei a Library ou o disco `C:\Nexus`. Logo, é uma validação de inventário, **não** uma nova prova criptográfica de equivalência byte-a-byte.

Os 35 ficheiros do arquivo antigo permanecem em paths estáveis. O documento `MEMORIA-DE-TRABALHO.md` não consta desse conjunto e é excluído pelo `.gitignore`; não é um «36.º ficheiro» comprovadamente perdido.

## Lacunas identificadas (não reconstruir por imaginação)

- `historico/repositorio-2026-09-24/README.md` aponta para `MEMORIA-DE-TRABALHO.md`; esse documento **não** existe na árvore publicada. O `.gitignore` atual exclui-o expressamente. **Não copiar nem publicar** conteúdo reservado só para reparar um link histórico.
- A PR #41 conserva dez referências relativas para documentos outrora em `nexus/docs/` que quebram após deslocar os apontamentos para `historico/evolucao-2026-10-04/`. Os destinos candidatos existem, mas a equivalência contextual deve ser confirmada. [Relatório com as onze referências](PR41-AUDITORIA-LIGACOES-2026-10-10.md).
- [`pc-full-mirror-20261004`](https://github.com/PAPACREATOR/cerebro-parvo-/tree/pc-full-mirror-20261004) é snapshot anterior, não confirmação da cópia atual do computador. Codex gere essa tarefa.
- Não está validado que todos os DOCX, PDFs, originais privados ou ficheiros do computador tenham sido transferidos. A preservação do repositório público não se confunde com backup privado.
- Sem HEAD único aprovado, os relatórios de estado de diferentes datas podem ser contraditórios e ainda assim representar corretamente a respetiva versão.

**Decisão documental:** manter os originais imutáveis, adicionar notas/índices datados e corrigir apenas a navegação quando houver fonte e revisão; não apagar estudos superados nem «normalizar» retroativamente o passado.
