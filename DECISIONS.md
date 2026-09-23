# Decisões

## 2026-09-22

- Nome atual: Cérebro Independente; Nexus e LocalNest ficam como histórico.
- Cline + Gemini Free é equipa de implementação económica, não parte da arquitetura do produto.
- Repositório e regras permanentes substituem dependência da memória dos chats.
- Git, testes, limites, rollback e STATUS precedem programação autónoma.
- `event_version`, idempotência central e pureza temporal/aleatória entram em F0.
- Outbox/retry entra em F3.
- Validação contra execução indireta de output de IA entra em F5.
- Gate de risco 0–3 devolve `ALLOW`, `DENY` ou `ASK`; a tabela de risco terá versão e testes próprios.
- F6 terá um conjunto de avaliação congelado e uma meta inicial de aceitação de intervenções de 80%, sujeita a revisão com dados reais.
- F7 usa adaptador Logseq fino; o núcleo permanece independente da implementação da interface.
- Percentagens externas sem amostra ou modelo calibrado não são previsão do projeto; gerir por riscos, marcos e testes observáveis.
- Gemini Free não recebe documentação confidencial ou acervo histórico.
- GitHub Copilot Free pode ser usado como revisor pontual, não como segundo escritor simultâneo. Limites e tratamento de dados exigem o mesmo recorte de contexto e revisão humana.
- Decisão posterior: simplificar a equipa para Cursor Pro como único programador de volume e Codex como engenheiro/revisor. Cline e Copilot ficam inativos para evitar configuração e concorrência desnecessárias.
- Decisão mais recente de Pedro: começar com Cursor Hobby gratuito; os 23 euros referidos são uma possibilidade futura, não uma compra autorizada. Cursor continua como único escritor automático, Codex como engenheiro/revisor. Instalação ainda por concluir.
- Interpretação anterior, **revogada em 2026-09-22**: “fase 4” foi lida como fase 4 funcional (quatro capacidades). Pedro corrigiu expressamente: o alvo é **F4 do Plano Mestre técnico, IA efémera sem ação**, depois de F-1/F0–F3. O objetivo é um protótipo técnico limitado F4; F5–F9/Alpha completo não estão autorizados agora. A arquitetura do produto fica intacta; o anexo F12 foi arquivado e comparado em `AUDITORIA-DOCUMENTAL-P4.md`.
- Pedro pediu repositório GitHub **privado** e confirmou o nome `PAPACREATOR/cerebro-parvo-`. O repositório foi criado por Pedro; o primeiro commit documental `e44dfac` foi enviado para `main` após revisão dos ficheiros e exclusões. Acervo, dossier jurídico, memória interna e segredos não foram incluídos. Isto não é validação de F0 nem autorização para publicar mais material reservado.
- Esclarecimento de Pedro sobre F4: IA generativa **efémera, por pedido explícito ou evento concreto necessário**, apenas quando as regras não resolvem. O núcleo continua entre chamadas; não há chamada automática a cada evento/tick, nem capacidade de ação na F4. “Efémera” refere-se ao contexto/permissões da chamada, não obriga a descarregar fisicamente o modelo após cada resposta.
- Copilot via GitHub.com pode ser usado no plano Free para pareceres pontuais, sem repositório privado ou informação reservada. Pro a US$ 10/mês é apenas opção futura; nenhuma subscrição foi aprovada. Gemini API fica isolada com contexto mínimo.
- **Decisão estrutural intermédia, corrigida pela linha seguinte:** são dois cofres separados, ambos com Markdown: criativo no Logseq Classic/File Graph e final apenas para conteúdo aprovado. A passagem é determinística após aprovação expressa do item/versão. Antes disso, o conteúdo fica no criativo; Pedro escolhe aprovar, manter só ali ou apagar. Nesta altura o assistente descreveu erradamente SQLite como um único índice/espelho mais estado. Activepieces executa o fluxo vivo, sem autoridade de escrita no final. A formulação anterior `Final Vault SQLCipher` foi preservada historicamente. Não se decidiu ainda a política de cifragem nem o protocolo de apagar conteúdo já aprovado.
- **Correção expressa posterior de Pedro, prevalece sobre a linha anterior:** existem **dois SQLite**, não um. O primeiro vive **no cofre final** e participa na memória/lógica do cérebro; o segundo é **espelhado**. O criativo é o cofre nativo do Logseq, sem recriação das suas funções. O utilizador escreve normalmente: Markdown é representação da implementação, não input exigido. A descrição anterior de SQLite como apenas índice/espelho do Markdown final fica revogada. O âmbito e a política técnica do segundo SQLite permanecem por especificar. Ver `ARQUITETURA-CORRIGIDA-2026-09-22.md`.


## 2026-09-23 — sandbox, adaptação humana e regra Docker/sem Docker

- IA generativa passa a ter uma fronteira constitucional explícita: **componente não confiável, substituível e confinado em sandbox**. `AIOutput = Proposal`; não possui autoridade direta sobre memórias, objetivos humanos, regras, permissões, apagamento ou ações externas.
- **Docker não é requisito do produto. A sandbox é requisito.** A pesquisa deve comparar Docker endurecido/rootless com soluções sem Docker. No alvo Windows, AppContainer/Win32 App Isolation entra como primeira hipótese a testar por ser isolamento nativo de processo/ficheiros/rede/recursos e potencialmente reduzir dependências e esforço de instalação.
- Docker continua candidato quando simplificar empacotamento/portabilidade ou oferecer vantagem mensurável, mas um contentor por si só não prova isolamento suficiente. Em Linux, rootless + seccomp é uma referência de endurecimento; gVisor/microVM são alternativas de isolamento mais forte a estudar apenas se o risco justificar a complexidade.
- Critério de escolha: isolamento efetivo + mínimo privilégio + RAM/CPU + dependências + passos de instalação + atualização + recuperação + portabilidade + esforço humano.
- O humano usa a máquina; a máquina adapta-se à pessoa. Linguagem natural é a camada principal de controlo humano; estruturas técnicas ficam invisíveis no uso normal.
- Adaptação individual pode aprender linguagem, preferências e comportamento, mas comportamento observado não cria silenciosamente objetivos humanos.
- A iniciativa do sistema é instrumental e rastreável a objetivos humanos; não há finalidade autónoma da máquina.
- O criativo e o canónico são dois regimes persistentes: consolidar não apaga o grafo criativo; o canónico pode informar criação futura sem a limitar. Regra: **consolidar o conhecimento sem consolidar o pensamento**.
- Estas linhas consolidam hipóteses/regras de investigação; não constituem validação experimental nem autorização para implementar fases adicionais.


### Evidência adicional — casos reais de isolamento Windows

- A Microsoft publicou em 2024 um caso explícito de **CPython 3.12 em Win32 App Isolation**, incluindo execução de código não confiável e ataques relacionados com LLMs entre os cenários motivadores. Isto reduz o risco da hipótese Python-first + sandbox nativa, mas não prova compatibilidade com o nosso runner/GPU.
- O **Chromium** usa no Windows uma arquitetura de sandbox broker/target e acrescenta tokens **AppContainer/LowBox** a processos sandboxed; a ausência da capability de Internet é usada como proteção adicional de rede. Isto é evidência de produção para o mecanismo, embora o Chromium use defesa em profundidade e não apenas AppContainer.
- **AppContainer/LPAC** e **Win32 App Isolation moderno** não devem ser confundidos. AppContainer existe desde Windows 8; a documentação atual do Win32 App Isolation integrado indica Windows 11 24H2/build 26100+ e a funcionalidade continua marcada como preview.
- Prioridade experimental corrigida: testar primeiro um processo de IA lançado por **AppContainer/LPAC ou API nativa equivalente**, com acesso apenas ao canal de I/O e aos pesos estritamente necessários. Se empacotamento, versão do Windows, IPC ou GPU/CUDA tornarem esta via pior, comparar imediatamente com Docker endurecido e alternativas.
- Teste obrigatório antes de decisão: runner/modelo + RTX 2080/CUDA; bloqueio de cofres/SQLite/credenciais/rede/processos; RAM/CPU/latência; instalação limpa; atualização; falha/recuperação; comparação equivalente com Docker.
- Esta evidência aumenta a plausibilidade técnica da via sem Docker, **não altera formalmente a confiança global histórica aproximada de 85%**.
