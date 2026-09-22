# Comparação dirigida — ResearchVault, Will e Cérebro Independente

Data: 2026-09-22. Análise documental para Pedro Alexandre Caldas Coelho. Não é teste dos projetos nem parecer de patente/originalidade. Base: READMEs públicos consultados nesta data e a arquitetura corrigida de Pedro em `ARQUITETURA-CORRIGIDA-2026-09-22.md`.

## Semelhanças e diferenças verificáveis

| Questão | ResearchVault (Piet Stam) | Will (Mindot) | Cérebro Independente de Pedro |
| --- | --- | --- | --- |
| Objetivo | Fluxo de investigação: recolher, filtrar e transformar fontes num wiki de conhecimento. | Motor de mente/agente persistente, autónomo e multissistema. | Ecossistema pessoal adaptável; escrita humana fluida, conhecimento curado e processos determinísticos com peças maduras. |
| Superfície diária | Zotero/inbox, leitor de feeds, Claude Code/Obsidian segundo README. | SDK, canais de comunicação, HTTP/MCP, entre outros. | Logseq Classic como cofre criativo; pessoa escreve normalmente sem introduzir Markdown. |
| Entrada no conhecimento | Go/No-go humano para fonte antes de bundle canónico; revisão adicional de rascunhos wiki. | Motores consolidam memória/identidade no ciclo autónomo. | Versão concreta só entra no **cofre final separado** depois de aprovação expressa; fontes e IA apenas propõem. |
| Memória e representação | Bundles Markdown, notas, wiki gerado; usa SQLite do Zotero como biblioteca de fontes, não descreve o par de SQLite de Pedro. | Memórias e artefacto portátil de identidade; não descreve dois cofres humanos nem par de SQLite. | Cofre criativo Logseq; cofre final com Markdown **e SQLite interno vivo**; segundo SQLite espelhado. Contrato exato do espelho por fechar. |
| IA | Síntese local por modelo no backend padrão; há configurações que podem usar cloud. | LLM é componente recrutado em certas condições; mock sem chave e muitos ticks sem inferência. | Núcleo funciona sem IA; F4 usa IA efémera por pedido ou evento concreto necessário, sem poderes de ação. |
| Automação/determinismo | Scripts, feed agendado, pontuação semântica e backend de síntese; não promete o replay semântico do núcleo de Pedro. | Tick, outbox/ack e replay reproduzível com seed e clock fixados; README diz que produção usa normalmente relógio de parede. | Activepieces executa workflows; núcleo regista eventos/regras para transições reprodutíveis; aprovação final é humana. |

## O que realmente validam

**ResearchVault** é o precedente mais próximo da cadeia **fonte → candidato/revisão humana → artefacto Markdown**, com Zotero e um wiki. A existência do filtro humano é importante: não afirmar que só Pedro o inventou. A diferença relevante é a composição total e a função da IA: ResearchVault descreve uma investigação alimentada por síntese LLM e uma experiência ligada a Zotero/Claude Code/Obsidian; não demonstra o cofre criativo Logseq, o SQLite interno vivo do final, um segundo SQLite espelhado nem o núcleo sem IA escolhido por Pedro. A sua documentação pública também especifica que o comportamento de privacidade depende do backend configurado. [README oficial](https://github.com/pjastam/ResearchVault).

**Will** é o precedente mais próximo da ideia de **cognição/persistência que não equivale a um prompt nem precisa de chamar o LLM a cada ciclo**. O README mostra mecanismos de seed/clock para replay e outbox com confirmação de efeitos. A diferença é tão importante quanto a semelhança: Will visa uma entidade autónoma com faculdades, objetivos e effectors; Pedro quer um sistema de conhecimento humano com aprovação obrigatória do final, IA sem ações em F4, Logseq e um par de SQLite. Não copiar as dezenas de motores de Will: isso contrariaria `USE > ADAPT > CREATE`. [README oficial de Will](https://github.com/mindot-ai/will).

**Estratégia de reaproveitamento de Pedro:** identificar um mecanismo pequeno e delimitado, verificar licença/dependências, adaptar só se necessário e testar encaixe no contrato local. ResearchVault fornece precedentes para entrada de fontes e filtro humano; Will para eventos/replay/outbox. A base que os cimenta é o fluxo humano de Pedro, não um fork combinado. Nenhum código dos dois foi ainda incorporado.

## O que não se pode concluir

- Os dois projetos **aumentam a plausibilidade por mecanismo**, não provam que a integração de Pedro já funciona, que é inédita no mundo ou que cabe num prazo específico.
- A comparação é com documentação pública dos autores, não auditoria linha a linha nem testes reproduzidos nesta máquina.
- Não há percentagem honesta de sucesso sem SPEC, versões, ensaios de falha, medições de tempo e critérios PASS. Semelhança arquitetónica não é um valor de probabilidade.
- Licença de repositório não transfere automaticamente direitos sobre dependências, marcas, dados ou código de terceiros. Qualquer reutilização exige análise separada. ResearchVault declara MIT; Will declara Apache-2.0 nos READMEs consultados.

## Testes que transformariam a comparação em evidência própria

1. Escrever em linguagem normal no Logseq e verificar que a pessoa não introduz Markdown nem usa uma parede de botões para o fluxo essencial.
2. Produzir uma proposta de fonte e confirmar que nada entra no final sem decisão associada a item e versão.
3. Aprovar uma vez, repetir o mesmo evento e confirmar uma só promoção consistente em Markdown e SQLite interno.
4. Verificar que o SQLite espelhado respeita o âmbito decidido, segue o interno sem obter autoridade inversa e recupera de interrupção. O contrato do espelho deve ser aprovado antes deste teste.
5. Repetir a mesma sequência de eventos e regras e comparar estados/hashes; repetir com IA desligada e provar continuidade das funções essenciais.
6. Interromper um workflow Activepieces em curso; confirmar retoma sem criar promoção duplicada. Replay de execução não substitui replay do estado semântico.

Fontes: [ResearchVault](https://github.com/pjastam/ResearchVault), [Will](https://github.com/mindot-ai/will), [Activepieces Durable Execution](https://www.activepieces.com/docs/install/architecture/durable-execution), [SQLite Online Backup API](https://www.sqlite.org/backup.html).
