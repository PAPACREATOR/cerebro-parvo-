# Arquitetura consolidada — v0.3, 2026-09-22

Prevalece a decisão expressa de Pedro: **dois cofres separados**, com aprovação antes do último; **dois SQLite distintos**, um interno no cofre final e outro espelhado; e escrita normal no Logseq, sem input Markdown exigido ao utilizador. Ver `ARQUITETURA-CORRIGIDA-2026-09-22.md`. A versão v0.1 SQLCipher está preservada no histórico.

## Núcleo

Python-first, orientado a eventos, com estado explícito, relógio lógico, regras determinísticas, event log append-only, snapshots, replay e auditoria.

## Memórias e conhecimento

- **Working Memory:** estado temporário necessário ao ciclo atual.
- **Behavioral Memory:** regras e preferências confirmadas, versionadas e auditáveis.
- **Cofre criativo Logseq Classic/File Graph:** lugar de escrita normal, relações, rascunhos e conhecimento em evolução. Usar as funções nativas de blocos, páginas, referências, tarefas e queries; não as reconstruir no núcleo. O utilizador não escreve Markdown como input técnico.
- **Cofre final separado:** só recebe versões aprovadas. Contém a representação Markdown gerida pelo sistema **e um SQLite interno**, que vive no cofre e participa na memória/lógica determinística. Não presumir que todos os dados internos derivam do Markdown.
- **SQLite espelhado:** segunda base distinta, derivada segundo contrato a fechar; não é o SQLite interno nem recebe autoridade de promoção por ser espelho. Conteúdo, direção, acesso e recuperação ainda não foram especificados.

Staging/quarantine é uma fronteira de entrada, não um terceiro cofre.

## Ciclo e autoridade de escrita

`escrita normal → Logseq/cofre criativo → proposta/candidato → decisão humana → promoção determinística → cofre final (Markdown + SQLite interno) → SQLite espelhado sob contrato`

Para uma entrada vinda da internet: `web → Activepieces/pesquisa → bruto/candidato → Logseq criativo → [brainstorming opcional conforme input/pedido] → decisão humana → cofre final`. Brainstorming e IA não são obrigatórios em cada entrada; a IA fica inativa até chamada permitida. O cofre final não é alimentado só porque a automação encontrou ou classificou algo.

Um item não aprovado permanece no cofre criativo até Pedro decidir: aprovar, manter apenas ali ou apagar. RAW/Candidate de pesquisa externa é quarentena, nunca entrada automática no final. A aprovação liga-se ao item, versão/hash e destino. O sistema não interpreta mera classificação, palavra temática ou conclusão de workflow como autorização.

O mecanismo de promoção deve ser recuperável se falhar entre decisão, escrita Markdown, transação SQLite interna e espelhamento; não há transação atómica única entre filesystem e as duas bases. Especificar autoridade por campo, IDs estáveis, ordem, idempotência e reconciliação antes de implementar F2. Preservar o original até haver política explícita e teste para eliminação. Aprovação e apagamento são decisões distintas.

Activepieces é o «interior vivo» operacional: horários, pesquisa, APIs, espera, retry e retoma de workflows. Não é autoridade sobre o cofre final nem substitui o EventLog semântico. Inputs externos observados são congelados como eventos; a mesma sequência de eventos e regras versionadas produz a mesma transição do núcleo. Python implementa só as regras específicas, validação e adaptação indispensáveis.

## Entradas externas

`fonte → staging → hash → deduplicação → proveniência → validação → evento → núcleo`

F3 deve usar outbox/retry com estados explícitos para impedir eventos presos entre staging e ingestão. Nenhuma integração pode depender de duas escritas sem recuperação observável.

## IA efémera e confinada em sandbox

`necessidade → contexto mínimo → sandbox → capability lease → chamada → PROPOSTA → evento de resultado → validação determinística → aplicar/rejeitar → auditoria → revogação`

**Invariante:** a IA é componente não confiável, substituível e confinado. `AIOutput = Proposal`, nunca autoridade. O modelo não escreve diretamente nas memórias criativa ou canónica, não altera objetivos humanos, regras constitucionais, permissões ou estado persistente, não apaga conhecimento e não executa ações externas diretamente.

A sandbox expõe apenas contexto e capacidades mínimas. Rede, filesystem, processos, dispositivos e credenciais são negados por defeito e concedidos apenas por contrato explícito, mínimo e temporário.

**Docker não é requisito arquitetural. A sandbox é.** A implementação deve comparar Docker endurecido/rootless, isolamento nativo do sistema operativo e, se necessário, sandbox/VM dedicada. Em Windows, AppContainer/Win32 App Isolation é candidato prioritário por fornecer isolamento nativo de ficheiros, rede, processos e recursos sem obrigar o utilizador a gerir Docker. Docker continua candidato quando trouxer vantagem operacional mensurável. Um contentor por si só não demonstra uma fronteira de segurança suficiente.

A escolha deve minimizar: superfície de ataque + permissões + RAM/CPU + dependências + instalação + manutenção + recuperação + esforço humano. Modelos e fornecedores são substituíveis. Cline + Gemini é ferramenta de construção, não componente do produto.

## Princípio humano e adaptação

O humano usa a máquina; a máquina não usa o humano. A pessoa trabalha em linguagem natural e o sistema adapta progressivamente linguagem, recuperação, apresentação e automação ao indivíduo. Comportamento observado pode ser evidência de preferência/interesse, mas não cria silenciosamente novos objetivos humanos.

A finalidade permanece humana. O sistema pode derivar apenas subobjetivos instrumentais rastreáveis a objetivos humanos. Quanto mais aprende sobre uma pessoa, mais capaz deve ficar de a servir, não de a governar.

A memória persistente preserva dois regimes: **criativo**, que conserva o grafo/processo que produziu ideias, hipóteses, alternativas, erros e relações; e **canónico**, que conserva conhecimento consolidado por decisão humana. Consolidar um resultado não apaga nem consome o grafo criativo que o originou. O canónico pode informar criação futura, mas não limita o que o criativo pode questionar: **consolidar o conhecimento sem consolidar o pensamento**.

## Interface

Experiência semelhante a conversa/documento contínuo sobre uma superfície Logseq, sem dashboard ou parede de botões. A pessoa **não precisa de conhecer Markdown**: escreve e decide normalmente, sem manipular sintaxe, ficheiros, YAML ou SQL; o sistema trata da representação técnica sem a expor no fluxo principal. Linguagem natural é traduzida para contratos determinísticos; não substitui as regras. Esta experiência ainda exige protótipo/teste, não é uma capacidade já verificada do Logseq sem adaptação.

## Domínios

Cada domínio é composto por representação Logseq, ferramenta/adaptador, regras e testes. Adicionar um domínio não redesenha o núcleo.

Logseq liga-se ao núcleo por um adaptador fino e uma API estável. O núcleo não depende do DOM nem da implementação interna da interface; quando aplicável, o adaptador deve ser testado contra o modo baseado em ficheiros e o modo de base de dados suportado.
