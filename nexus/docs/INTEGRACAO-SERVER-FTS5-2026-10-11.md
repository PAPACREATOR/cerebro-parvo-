# 11/10/2026 — server.js → Host Python e índice FTS5 sem segunda autoridade

Estado: **implementação parcial em PR #55; NÃO integrado / NÃO validado no PC físico**.

## Decisão

Conservar o `server.js` como *gateway HTTP local, opcional e sem estado*. A Folha comunica com o gateway, que encaminha os bytes de cada pedido para o `nexus/app.py` ativo; este autentica sessão e chama o Host/Store existentes. O gateway **não é injetado no Kernel**, não importa Store, não cria tickets, não seleciona ferramentas, não interpreta texto, não aprova e não grava memória.

```text
Folha (nexus/ui/app.js; sessão emitida pelo Python Host)
  → [opcional] server.js / Express / 127.0.0.1, sem armazenamento
  → nexus/app.py / 127.0.0.1, verifica Host, Origin e X-Nexus-Session
  → Host + Kernel / contratos + políticas + runtime Windows delimitado
  → Store (input original, Creative, Canonical, decisão humana, proveniência)
                      ↑
          FTS5 = índice derivado, reconstruível e sem autoridade
```

O lançamento oficial direto da Folha por `nexus/app.py` continua válido sem Node. O gateway é uma opção de desenvolvimento/apresentação, não dependência do produto Windows.

## Verificação da solução no código existente

- `nexus/app.py` já oferece `/api/interpret`, `/api/prepare-run`, `/api/confirm-run`, `/api/runs`, `/api/runs/<id>`, `/api/pdf/<id>`, `/api/prepare` e `/api/approve`. Impõe Host/Origin loopback e sessão emitida pelo Host.
- O Host gere a execução e a aprovação, enquanto o Store conserva entrada original, hashes, resultados, proveniência, Creative e Canonical. Uma confirmação de execução não é uma aprovação de Canonical.
- O novo `server.js` encaminha status, cabeçalhos e corpo de resposta; não permite `/api/run` de diagnóstico; não tem `Map()` de memória nem `generateSimplePdf`; está ligado só a `127.0.0.1`.
- `nexus/ui/index.html` regressa aos bytes selados no manifesto existente. Não se modificam os ficheiros Kernel, Host, Store, parser ou `integrity.json`.
- O arranque opcional precisa de uma porta Python fixa e `NEXUS_BACKEND_PORT` compatível. A sessão só pode ser a emitida pelo Python; a URL simples do gateway **não emite** sessão. Reutilizar a sessão não equivale a partilhá-la com ferramentas externas.
- Se a porta Python não responder ou a sessão for recusada, o gateway falha fechado e não faz trabalho de substituição.

## Memória única e FTS5 — código já existente

O laboratório `nexus/lab/wiki/kernel_bridge.py` já implementa um `WikiBridge(store, lab_root)` com:

1. `rebuild()`: lê pacotes do Store, verifica conteúdo e proveniência, recria SQLite/FTS5 em diretório separado;
2. `search(query, allowed_ids, include_creative=False, limit=8)`: escopo de IDs obrigatório, consulta literal parametrizada, limite e revalidação do conteúdo pelo Store; por defeito apenas Canonical;
3. `prepare`/`revalidate`: pacote com ID, autoridade e hashes de conteúdo, proveniência e input;
4. `save_experiment`/`reverse`/`uses`: evidência experimental; não cria aprovação e não escreve Canonical.

**Três memórias lógicas, uma autoridade:** trabalho transitório; processos/regras versionados; conhecimento persistente Creative+Canonical. O SQLite/FTS5 não é um novo cofre nem uma quarta memória: é uma *vista materializada* da memória existente, descartável e reconstruível. O original e a proveniência permanecem nos ficheiros geridos pelo Store.

Reutilizar o laboratório, e não copiar o SQLite do Sir Thaddeus: o Sir Thaddeus documenta uma separação útil entre contrato de memória e armazenamento FTS5, mas inclui políticas de permissões `Session`/`Always` inadequadas à confirmação humana por operação do Nexus.

## Lacuna real para pesquisa na Folha

O bridge FTS5 **ainda não está registado num endpoint autenticado da Folha**. Ligar o gateway apenas torna acessíveis as rotas **já existentes**; não acrescenta `/api/search`. Seria falso afirmar que o botão de pesquisa usa FTS5 nesta PR.

A próxima integração produtiva precisa de um contrato de *pesquisa read-only* protegido pelo Host: sessão, seleção de escopo, limites, revalidação pelo Store, Creative explícito, respostas com refs/hashes/proveniência e gestão de índice desatualizado. Ao estender o backend selado, é obrigatório atualizar o manifesto com hashes verdadeiros e repetir os gates no mesmo SHA. **Não fazer alterações clandestinas a app.py, Host, Kernel, Store ou parser nesta PR**; preparar esta passagem como microprocesso separado e aprovado.

O índice pode conter texto derivado sensível em disco: manter ACL de acesso locais e diretório fora do Git, não anexar à UI sem autenticação, não expor `/api/search` no Express sem validação e não usar o índice como origem autoritativa. A reconstrução deve tolerar corrupções e ser revalidada contra Store; testes de concorrência/crash/ACL e recuperação no Windows continuam necessários.

## Testes por SHA

A PR acrescenta `nexus/tests/gateway_transport.test.cjs` (encaminhamento real HTTP para stub que representa o backend, verificação de sessão/Host/Origin, corpo, PDF, recusas e memória só do backend) e `nexus/tests/test_single_runtime_boundary.py` (inexistência de estado independente, contrato do gateway, HTML selado). A CI isolada executa Linux e Windows e repete também `nexus/lab/wiki/test_kernel_bridge.py` contra Store real com dados de ensaio. Estes testes não demonstram um E2E do gateway contra `nexus/app.py` real, nem Writer real no PC do utilizador.

Não fazer merge de PR #55 até todos os gates exigidos no mesmo SHA estarem PASS. O código original do AI Studio e do Sir Thaddeus permanecem em repositórios próprios; usar como referências e não como autoridade no Nexus.
