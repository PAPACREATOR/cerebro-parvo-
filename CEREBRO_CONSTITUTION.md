# Constituição do Cérebro Independente

Versão: 0.3 — 2026-09-22
Autor declarado: Pedro Alexandre Caldas Coelho

## Identidade

O Cérebro Independente é um sistema cognitivo determinístico contínuo com IA generativa efémera. «Nexus» e «LocalNest» são nomes históricos, não o nome atual do produto.

Não é um chatbot, um agente LLM permanente, uma coleção de scripts ou uma aplicação dependente de um fornecedor de IA.

## Regras invioláveis

1. A pessoa é a autoridade final e recebe `HumanDecisionRequest` quando regras, evidência ou limites de risco não permitem decidir.
2. O núcleo funciona sem IA, cloud ou GPU NVIDIA.
3. Há dois cofres separados: o criativo é o grafo do Logseq Classic/File Graph, usado pelas suas funções nativas; o final recebe apenas conhecimento aprovado e contém Markdown tratado pelo sistema **e um SQLite interno vivo**, parte da memória/lógica determinística. Há um **segundo SQLite espelhado**, distinto. Nenhum dos SQLite é um terceiro cofre.
4. Nada entra no cofre final sem aprovação expressa da pessoa para uma versão concreta. Fontes externas, IA, Activepieces e classificadores não escrevem diretamente nele.
5. Activepieces é a automação externa escolhida; não substituir por n8n por conveniência.
6. Logseq é a superfície cognitiva escolhida; não substituir por Obsidian por conveniência.
7. IA começa sem capacidades e permanece **confinada em sandbox**. Cada chamada recebe apenas contexto e capacidades necessárias e permitidas, durante o tempo mínimo. `AIOutput = Proposal`: IA não é autoridade, não escreve diretamente nas memórias, não muda objetivos/regras/permissões, não apaga conhecimento e não executa ações externas diretamente.
8. Resultados não determinísticos tornam-se eventos registados e são reutilizados no replay; não se volta a chamar a origem.
9. Usar antes de adaptar; adaptar antes de criar. Código próprio é a menor categoria.
10. Alterações estruturais exigem evidência, consequências documentadas e decisão humana.
11. A pessoa escreve e decide em linguagem normal; **não precisa de saber o que é Markdown** nem de o escrever, editar, formatar ou gerir para usar o fluxo principal. Markdown, YAML, SQL, ficheiros e conversões são responsabilidade invisível da implementação. Não impor uma parede de botões.
12. O sistema adapta-se progressivamente à linguagem, preferências e modo de trabalhar de cada pessoa. Comportamento observado é evidência, não autorização automática para criar objetivos humanos.
13. A finalidade é humana. O sistema pode criar apenas subobjetivos instrumentais rastreáveis a objetivos humanos; não cria silenciosamente finalidades próprias.
14. A memória criativa persiste como grafo/genealogia mesmo depois de um resultado ser consolidado. O canónico pode alimentar criação futura, mas nunca proíbe o criativo de o questionar.
15. **Docker não é requisito; sandbox é requisito.** Soluções com Docker e sem Docker devem ser pesquisadas e testadas. A escolha é feita por isolamento efetivo e custo total, incluindo esforço de instalação, manutenção e recuperação por pessoa não técnica.

## Regra do último cofre

Enquanto não houver aprovação, o conteúdo permanece no cofre criativo; a pessoa pode aprovar, manter apenas no criativo ou pedir que seja apagado. Classificação de tema, pesquisa, fim de conversa ou sugestão da IA não são aprovação. A promoção aprovada é uma operação mecânica, determinística e auditável, identificada pelo item, versão/hash e decisão. Repetir a mesma decisão não cria nova entrada. Uma falha interrompe a promoção e fica visível; não autoriza escrita silenciosa ou perda do original. A política de apagamento, incluindo o que fazer com versões já aprovadas, exige contrato e teste próprios; não se apaga automaticamente por mera igualdade de hash.

Não se presume que o SQLite interno seja reconstruível do Markdown, nem que o espelho tenha autoridade para alterar o interno. Autoridade por campo, âmbito do espelho, privacidade em repouso, backups e proteção do cofre final terão decisão e teste específicos antes de dados reais. A formulação v0.1 que fazia de `vault.db` o cofre final único foi arquivada em `historico/ARQUITETURA-OPERACIONAL-v0.1-2026-09-22.md`.

## Determinismo

Para o núcleo determinístico:

`S(t+1) = F(S(t), E(t), R, K)`

Com o mesmo estado inicial, eventos, regras e configuração, o estado final e o seu hash devem ser iguais.

- Cada evento tem `event_id` e `event_version` explícitos.
- A idempotência por `event_id` aplica-se a todos os produtores, internos e externos.
- Transições não podem ler relógio de parede, gerar UUID ou usar aleatoriedade. Esses valores são capturados pelo produtor e congelados no evento.
- Falhas de replay nunca são escondidas para avançar de fase.

## Segurança de IA

`AIOutput = Proposal`

A IA é tratada como componente não confiável e substituível, atrás de uma fronteira de sandbox independente do modelo. Por defeito: sem escrita direta nas memórias, sem alteração de objetivos/regras/permissões, sem execução externa, sem credenciais e sem filesystem/rede/processos/dispositivos além do que um contrato temporário autorize.

A sandbox é uma propriedade de segurança, não o nome de uma tecnologia. Para o alvo Windows, **AppContainer/Win32 App Isolation** deve ser testado primeiro como hipótese de implementação simples e nativa; Docker endurecido/rootless e VM/sandbox dedicada permanecem comparadores. A decisão exige testes de permissões, rede, filesystem, processos, GPU, RAM/CPU, instalação, atualização, recuperação e operação por utilizador não técnico.

`C_i = C_needed ∩ C_permitted`

Uma ação só avança quando existem necessidade, permissão, âmbito e validação. A validação repete-se em cada fronteira: um adaptador confiável não pode executar automaticamente texto ou comandos produzidos por IA.

O Gate classifica risco de 0 a 3 e devolve `ALLOW`, `DENY` ou `ASK`. A classificação exata será versionada e testada antes de permitir ações de IA.

## Regra de desenvolvimento

`SPEC → IMPLEMENT → UNIT TEST → INTEGRATION TEST → RUN → RESULTS → REVIEW`

Commit só após revisão e quando autorizado. Cline implementa tarefas pequenas; não arbitra arquitetura nem decide que o próprio código está correto.
