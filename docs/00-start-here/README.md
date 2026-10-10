# Começar aqui — Nexus / Cérebro Local

**Nexus é um projeto Windows pensado para ajudar uma pessoa a criar, organizar e trabalhar com informação sem entregar a uma IA ou a serviços externos o controlo do seu conhecimento.** A interface pretendida é uma Folha simples: a pessoa escreve o que quer fazer; o sistema verifica o pedido, limita a execução e apresenta os resultados para revisão.

**Primeiro contacto?** Esta página explica o essencial em cerca de cinco minutos. Não é necessário ler todo o histórico nem instalar o projeto para compreender como ajudar.

> **Estado em 10/10/2026:** existe código candidato e testes por componentes, mas **ainda não existe uma release integralmente validada**. A [PR #45 — integração candidata](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), no commit `66027af7f2ea084bc62d85b840d1fc3113e60a97`, é a referência técnica posterior à [PR #32 — baseline Windows](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32). Ambas são trabalhos separados; a #45 permanece **Draft, não integrada** na verificação de 10/10. Consultar [estado e limitações por SHA](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) antes de fazer afirmações sobre funcionalidades.

## 1. O que o Nexus pretende resolver

Uma pessoa pode querer verificar um ficheiro, organizar fontes, rever um texto ou preparar um livro. Habitualmente, isso exige aplicações e passos dispersos. O Nexus pretende reunir o pedido numa única entrada e usar ferramentas especializadas **sem as tornar donas dos dados nem das decisões**.

O percurso conceptual é:

```text
Pessoa → Folha → Parser e regras → Kernel / Host / Store
                                          ↓
                            Ferramenta autorizada e isolada
                                          ↓
                            Resultado candidato (Creative)
                                          ↓
                                Decisão humana explícita
                                          ↓
                            Conhecimento aprovado (Canonical)
```

- **Folha:** superfície de escrita e pedidos, sem obrigar a pessoa a programar.
- **Parser:** reconhece a intenção; reconhecer **não** equivale a executar.
- **Kernel / Host / Store:** guardam a autoridade, integridade, proveniência, estado e recuperação.
- **Ferramentas:** LibreOffice, LanguageTool, Zotero, OpenNotebook e outras podem ser usadas dentro de limites explícitos. O runner interno pode chamar adaptadores diretamente; **MCP é opcional**, não uma passagem obrigatória.
- **Creative / Canonical:** resultados candidatos ficam separados do conhecimento aprovado; a promoção exige autorização humana associada ao conteúdo.

A confirmação **antes de executar** uma operação é diferente da aprovação **antes de promover** algo para Canonical. Nenhuma ferramenta, agente ou modelo recebe essa autoridade.

## 2. O que existe hoje — e o que ainda não se deve prometer

| Componente | Situação verificável no candidato da PR #45 | Não confundir com |
| --- | --- | --- |
| Folha / parser | Reconhece **sete prefixos/intencionalidades**; há uma regra natural pública delimitada para `verify` com anexo e confirmação | Sete intenções executáveis pela interface |
| Host, Store e runner | Há implementação de integridade, execução delimitada, Creative/Canonical e **dez processos internos** definidos | Dez ferramentas prontas para o utilizador final |
| Proteção Windows | O código delimita processos lançados pelo Host através da fronteira de isolamento Windows | Controlo absoluto sobre todo o sistema operativo |
| Ferramentas especializadas | Existem adaptadores e contratos, incluindo OpenNotebook, Writer e media | Todos os serviços reais e produtos multimédia comprovados E2E |
| Testes | Existem provas datadas, PASS parciais e falhas conhecidas | Release, instalação pessoal ou aceitação física integral |

**Exemplo concreto da diferença:** pedir na Folha a verificação de integridade de um ficheiro é o percurso natural público identificado no código analisado; a execução exige confirmação. O facto de o runner conhecer também `book`, `music` ou `podcast` **não** demonstra que a Folha já consegue entregar um livro, música ou podcast completo.

Ver [matriz código ↔ documentação](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md), [fotografia do estado](../10-current/ESTADO-DOCUMENTAL-2026-10-10.md) e [evidências PASS/FAIL por PR](../60-evidence/MATRIZ-PRS-2026-10-10.md). Números históricos só valem para o commit e o ambiente em que foram obtidos.

## 3. Quero contribuir. Por onde começo?

**Não é preciso redesenhar o Nexus nem tocar no Kernel para ser útil.** Uma contribuição pequena, reproduzível e isolada vale mais do que acrescentar uma dependência ou reescrever a arquitetura.

1. Leia as [tarefas abertas e as regras de colaboração](../30-help/README.md). As [issues de ajuda](https://github.com/PAPACREATOR/cerebro-parvo-/issues/35) são um ponto de entrada; confirme se cada issue continua aberta.
2. Escolha **uma única tarefa** e identifique a PR e o SHA a que diz respeito. Não trabalhe sobre a branch de outro colaborador.
3. Registe o resultado com um caso concreto, ambiente, entrada, comportamento esperado e comportamento observado. **FAIL, BLOCKED e NOT RUN não são PASS.**
4. Apresente o diagnóstico ou uma alteração pequena numa PR separada. Preserve os testes e o histórico original.

**Exemplo de primeira contribuição sem código:** analisar o guia de uma capacidade, identificar uma afirmação de “funcional” que não tenha prova ligada ao SHA, e propor uma correção documental com referência ao teste ou à pendência. A [issue #38 — documentação atual versus histórica](https://github.com/PAPACREATOR/cerebro-parvo-/issues/38) é um exemplo desse tipo de trabalho, sujeito ao seu estado atual.

Outros pontos de entrada: [#37 — casos adversariais PT-PT da Folha](https://github.com/PAPACREATOR/cerebro-parvo-/issues/37), [#36 — diagnóstico Writer / LPAC](https://github.com/PAPACREATOR/cerebro-parvo-/issues/36) e [#39 — revisão de evidência Windows](https://github.com/PAPACREATOR/cerebro-parvo-/issues/39). Nenhuma destas tarefas autoriza reduzir as proteções para obter um teste verde.

**Limites que não podem ser ultrapassados:** autoridade humana; separação Creative/Canonical; proveniência; validação de conteúdo e identidade; integridade e recuperação; isolamento Windows; não repetição silenciosa de efeitos externos ambíguos. O [guia de contribuição](../../CONTRIBUTING.md) explica o procedimento; mudanças ao Kernel e à arquitetura exigem justificação, revisão específica e autorização dos responsáveis.

## 4. Mapa de leitura — só quando precisar

| Preciso de perceber… | Onde ler |
| --- | --- |
| O estado técnico da implementação mais recente examinada | [Compatibilidade com a PR #45](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) |
| Porque a arquitetura é pequena e quais os seus limites | [Núcleo mínimo](../20-architecture/MINIMUM-CORE.md) |
| Como ajudar sem criar conflitos | [Colaboração](../30-help/README.md) |
| Que testes passaram ou falharam e em que SHA | [Evidências](../60-evidence/README.md) |
| Que decisões são vinculativas | [Constituição](../../CEREBRO_CONSTITUTION.md) e [decisões fundamentadas](../40-decisions/README.md) |
| Porque saíram Activepieces/Conductor e quais as experiências antigas | [História e genealogia](../99-history/README.md) |
| Onde estão o runtime candidato, contratos e testes | [Pasta `nexus/`](../../nexus/) e [índice dos contratos](../../nexus/docs/README.md) |

As pastas `historico/` e `implementacao/` preservam experiências, código antigo e decisões anteriores; **não são instruções de instalação do candidato atual**. A [reconciliação das onze referências históricas](../99-history/RECONCILIACAO-11-REFERENCIAS-2026-10-10.md) explica as correções de navegação sem fingir que uma memória reservada foi recuperada.

## 5. O que este projeto não é

O Nexus não pretende ser um agente autónomo que decide pela pessoa, um substituto para a segurança do Windows ou um sistema dependente de Ollama, Activepieces, Conductor ou qualquer motor de IA. O objetivo é integrar ferramentas **substituíveis**, com menos código próprio possível e fronteiras que não possam ser ultrapassadas por uma resposta de modelo.

A [PR #49](https://github.com/PAPACREATOR/cerebro-parvo-/pull/49) organiza **documentação apenas** e permanece separada da implementação. A documentação pode descrever um contrato ou uma intenção; **só código e testes no mesmo SHA, com evidência adequada, demonstram o comportamento observado**.

---

### English — quick start

**Nexus is a Windows, local-first, human-controlled knowledge and creation project.** A simple writing interface receives requests; the Kernel/Host enforce policy, integrity, execution boundaries and recovery; tools produce candidates; only explicit human approval can promote content to Canonical.

**Project status (10 October 2026):** [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45) is the latest examined integration candidate, still Draft. [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32) is the earlier Windows baseline. Seven recognized intents and ten internal runner processes **do not** mean ten working public features. [Read the evidence](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md), then [choose a scoped contribution](../30-help/README.md). Preserve the human-approval gates and Windows isolation; do not rewrite the core architecture or confuse historical test results with a released product.
