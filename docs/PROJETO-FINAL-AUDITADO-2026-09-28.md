# Projeto final auditado — 28-09-2026

Estado: arquitetura operacional consolidada após comparação com o repositório, Activepieces, Open Notebook e o ecossistema Obsidian. Este documento não declara o produto concluído. Distingue desenho escolhido, código existente e prova executada.

## 1. Critério

Nada é mantido por apego tecnológico. Cada função é avaliada por esta ordem:

1. usar mecanismo maduro existente;
2. adaptar apenas o que falta;
3. criar código próprio só quando a função é específica do Cérebro ou a solução externa viola as regras;
4. medir por comportamento e testes, não por número de módulos.

Os IMP-001–026 continuam úteis como contratos/testes da família de importação. Não obrigam a criar 26 módulos Python nem a reproduzir no Core aquilo que Activepieces ou outra capacidade já faz com segurança.

## 2. Arquitetura final mínima

~~~mermaid
flowchart TD
    P[Pessoa] --> UI[Activepieces Chat / Folha Única]
    UI --> C[Core determinístico M1–M14]
    C --> AP[Activepieces Flows / Subflows / Pieces]
    AP --> EXT[MCP / API / CLI / programas externos]
    AP --> ON[1 espaço Open Notebook]
    ON --> T[Tiny IA isolada e temporária]
    T --> U[Resultado + fontes: UNTRUSTED]
    EXT --> U
    U --> C
    C --> CMP[3 comparadores]
    CMP --> CR[Creative Markdown]
    CR --> H[Portão humano quando aplicável]
    P --> H
    H --> CA[Canonical Markdown]
    C --> SQ[SQLite: eventos, IDs, relações e índices]
~~~

A regra central é: **o Core governa; Activepieces executa; Open Notebook pensa sob trela; a pessoa decide autoridade**.

## 3. O que fica nosso

### Três memórias

1. Working Memory — contexto transitório da tarefa.
2. Behavioral/Procedural Memory — preferências, regras, correções e rotinas versionadas.
3. Persistent Knowledge Memory — conhecimento duradouro dividido por autoridade entre Creative e Canonical.

Não são três bases de dados. São três funções de memória.

### Dois cofres

- Creative: hipóteses, alternativas, rascunhos, contradições, rejeições, resultados em evolução.
- Canonical: versão atualmente aprovada/consolidada pela pessoa.

Usam a mesma mecânica de escrita e formatos abertos. A diferença é de autoridade. Promoção não elimina Creative nem genealogia.

### Três comparadores

- determinístico/matemático: hashes, estados, datas, valores, regras, idempotência;
- semântico: significado, possível equivalência, incompatibilidade e contradição candidata;
- relacional: fontes, documentos, dependências, versões, temporalidade e caminhos.

Semântico não significa “LLM sempre”. Primeiro usam-se regras, texto, fuzzy/FTS e relações; a tiny é chamada apenas quando acrescenta valor.

### M1–M14

Mantêm-se como responsabilidades e invariantes. Não precisam de existir como 14 serviços ou 14 pastas. Implementar por contratos e funções mínimas.

## 4. Activepieces é a oficina, não o cérebro

Usar primeiro capacidades nativas já maduras:

- Chat/Folha quando suficiente;
- triggers e schedules;
- routers/branches;
- Subflows;
- retries;
- waitpoints/approvals;
- webhooks;
- Pieces;
- MCP Client;
- MCP Server;
- testes de flows;
- sandbox de execução do próprio Activepieces.

Não construir motor de workflow, sistema de retries, sistema de waits, catálogo de integrações ou editor visual próprios.

O registo de capacidades do Core começa como simples configuração:

CAPACIDADE -> flow/subflow/provider

Não criar um subsistema separado enquanto uma tabela/configuração resolver.

## 5. Um único espaço cognitivo

Open Notebook é uma bancada cognitiva, não memória e não autoridade.

Por tarefa:

1. Core identifica tema, objetivo, perfil, regras e permissões.
2. Core recupera/rankeia fontes relevantes.
3. Calcula um orçamento de contexto a partir da janela real do modelo.
4. Reserva espaço para instruções e resposta; envia apenas o lote que cabe.
5. Activepieces chama o mesmo espaço Open Notebook.
6. A tiny executa a tarefa delimitada.
7. Resultado e fontes regressam como UNTRUSTED.
8. Core valida/compara.
9. Se a evidência for insuficiente, seleciona o próximo lote e repete.
10. A sessão/contexto cognitivo da tarefa não se torna memória autoritativa.

A tiny pode saltar de jurídico para escrita, finanças ou outro tema porque a especialização vem do contexto e das regras, não de um modelo permanente diferente.

### Trela obrigatória da tiny

- contexto mínimo e temático;
- fontes permitidas;
- regras específicas do tema;
- objetivo fechado;
- schema/formato de saída;
- limites de tokens/tempo;
- sem acesso geral aos cofres;
- sem publicação/escrita direta;
- sem aumentar permissões;
- sem decisão Canonical;
- sem memória oculta entre tarefas.

## 6. Persistência e G10 — desenho mínimo escolhido

G10 deixa de ser um problema de “transação mágica entre três sistemas”. O desenho escolhido é coordenar a mutação com SQLite e materializar Markdown de forma recuperável.

Protocolo proposto:

1. preparar a nova versão Markdown em ficheiro temporário;
2. calcular hash do conteúdo e alvo;
3. transação SQLite grava evento/intenção PREPARED com operation_id, autoridade, alvo, hash, payload necessário ao replay e proveniência;
4. fechar a transação PREPARED;
5. fazer replace/rename atómico do temporário para o destino no mesmo filesystem;
6. nova transação confirma hash observado e marca COMMITTED;
7. só depois atualizar FTS/cache.

Reconciliação após crash:

- PREPARED + destino ausente: NOT_COMMITTED ou retry seguro;
- PREPARED + destino com hash esperado: completar COMMITTED;
- PREPARED + hash divergente: RECOVERY_REQUIRED;
- COMMITTED + destino ausente/divergente: RECOVERY_REQUIRED e rematerialização apenas a partir de evidência autoritativa congelada.

O mesmo writer serve Creative e Canonical. SQLite coordena eventos/recibos/IDs/relações; não é um terceiro cofre humano. Markdown continua a representação aberta e portátil.

**Estado:** decisão de desenho selecionada; ainda não é PASS. Só fecha G10/IMP-019 após testes reais de crash, replay e idempotência.

## 7. Sandbox sem reinventar sandbox

- Flow/code steps: usar o isolamento/sandbox fornecido pelo Activepieces.
- Open Notebook/tiny: serviço/container separado, sem mount direto dos cofres; recebe apenas material preparado.
- Programas externos: trabalhar em diretório temporário/dedicado e devolver resultado ao Core.
- Rede: mínima por capacidade; sem acesso externo quando a tarefa não precisa.
- Segredos: ficam nos mecanismos próprios do executor/conector, nunca no contexto enviado à tiny.

## 8. O que sai do caminho principal

Não são “maus projetos”; apenas deixaram de justificar a complexidade no runtime:

- Obsidian, Joplin e Logseq como UI ou dependência obrigatória;
- frontend próprio na primeira versão;
- motor de workflow próprio;
- vários notebooks/agentes permanentes por domínio;
- RAG/vector DB próprio no Core;
- LLM global com acesso ao sistema;
- custom Pieces quando MCP/API/CLI existente resolve;
- duplicação de regras entre Core e Activepieces;
- eliminação automática de originais no MVP;
- modelo grande sempre ligado;
- dezenas/centenas de flows próprios antes de existir necessidade observada.

Obsidian pode continuar como viewer/editor opcional de Markdown para utilizadores técnicos, mas não faz parte do contrato do produto.

## 9. Famílias iniciais de flows

Começar pequeno:

- RECEBER
- PESQUISAR
- TRABALHAR
- COMPARAR
- CRIAR
- VALIDAR
- APRESENTAR
- PEDIR_APROVAÇÃO
- EXECUTAR_AÇÃO
- REGISTAR

Criar Subflow apenas quando reduz repetição, melhora teste ou isolamento.

Cada flow deve ter uma explicação equivalente em linguagem natural. Exemplo: “quando chegar uma fatura, liga-a ao contrato, regista a despesa e pergunta-me antes de concluir”.

## 10. Comparação de mercado — Obsidian

### Obsidian puro

É muito mais maduro como editor/PKM: Markdown local, propriedades, backlinks, pesquisa, Bases, Canvas, recuperação, Sync/Publish opcionais e ecossistema de plugins.

Não devemos competir por “melhor editor de notas”.

### Obsidian + plugins locais de IA

Plugins atuais como Local LLM Hub e Local LLM Helper já demonstram:

- LLM local;
- RAG/recuperação local;
- workflows;
- MCP;
- restrição de pastas/contexto;
- histórico/rollback ou aprovação de alterações;
- envio apenas do contexto necessário em alguns fluxos.

Logo, “Markdown + IA local + workflow” por si só não diferencia o Cérebro.

### Espaço específico do Cérebro

A proposta é outra:

- UI natural sem obrigar o utilizador a gerir vault, YAML ou plugins;
- execução multiaplicação através de Activepieces;
- determinismo como caminho normal;
- tiny IA como coprocessador cognitivo isolado, não autoridade;
- 3 memórias explícitas;
- Creative/Canonical como duas classes formais de autoridade;
- 3 comparadores;
- proveniência, genealogia e contradições preservadas;
- Human Gate permanente;
- regras pessoais versionadas que nunca são ultrapassadas por comportamento aprendido;
- ferramentas substituíveis por capacidade.

O concorrente conceptual mais justo é “Obsidian + plugin local de IA + motor de automação + regras manuais de governação”. O objetivo do Cérebro é entregar esse resultado como um sistema coerente e simples para quem não quer montar essa pilha.

## 11. Onde Obsidian ganha hoje

- maturidade de produto;
- edição e navegação de conhecimento;
- experiência mobile;
- comunidade/ecossistema;
- instalação inicial simples;
- recuperação e sincronização já usadas em produção.

## 12. Onde o desenho do Cérebro pode diferenciar-se

Se for implementado como especificado:

- menor exposição da complexidade técnica ao utilizador;
- automação e integração externa de primeira classe;
- autoridade humana explícita e auditável;
- Creative/Canonical formal;
- IA substituível e descartável;
- contexto da IA controlado deterministicamente;
- processos explicáveis em linguagem natural;
- capacidade de trocar ferramentas sem trocar o conhecimento.

Isto é posicionamento de produto, não prova de superioridade. O sistema ainda precisa demonstrá-lo em uso real.

## 13. Evidência atual

No commit 3e5b61e3 do main:

- GitHub Actions concluiu com sucesso “Integridade documental e 34 testes fornecidos”;
- o candidato Python existente não regrediu com as alterações documentais;
- a suite não prova Activepieces, Open Notebook, Windows, sandbox real, G10, promoção Creative→Canonical ou M1–M14 E2E.

Não declarar release com base nesses 34 testes.

## 14. Próximos portões mínimos

1. Implementar e testar o protocolo G10 acima.
2. Criar um único flow real Activepieces: UI/trigger -> Core -> resposta.
3. Materializar Creative Markdown pelo writer recuperável.
4. Implementar Human Gate e promoção para Canonical sem apagar Creative.
5. Integrar um Open Notebook com tiny local e duas tarefas de temas diferentes; provar isolamento e budget de contexto.
6. Integrar uma capacidade externa madura por MCP/API/Piece.
7. Executar crash/restart/replay.
8. Executar E2E em Windows.
9. Só depois empacotar uma instalação para utilizador não técnico.

## 15. Critério de sucesso do MVP

Uma pessoa escreve normalmente:

“usa estes documentos, compara com o que já sei sobre o projeto e prepara uma proposta; não publiques nada.”

PASS exige:

- intenção corretamente interpretada;
- fontes selecionadas e registadas;
- tiny recebe apenas contexto permitido;
- resultado volta UNTRUSTED;
- comparadores registam confirmação/complemento/contradição/insuficiência;
- resultado entra em Creative;
- Canonical não muda sem decisão humana;
- fechar/reabrir não perde estado;
- replay não volta a chamar IA para inventar a história;
- tudo é apresentado sem exigir Markdown/SQL/IDs ao utilizador.

Se isto funcionar repetidamente, existe produto. O resto é extensão.
