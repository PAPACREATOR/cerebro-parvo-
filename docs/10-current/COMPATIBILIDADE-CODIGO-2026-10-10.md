# Compatibilidade documental com o código — fotografia de 10/10/2026

**Resultado: COMPATIBILIDADE PARCIAL / RECONCILIAÇÃO DOCUMENTAL NECESSÁRIA.** Esta é uma leitura estática, não uma execução do Nexus. A documentação está em [PR #49](https://github.com/PAPACREATOR/cerebro-parvo-/pull/49), derivada da [PR #41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41). A referência técnica é a [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), commit integral `66027af7f2ea084bc62d85b840d1fc3113e60a97`; a [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32), `da86b6dd181d00fd7a87addaa01a12ec3a14e57b`, é a baseline anterior. As branches não se tornam uma única árvore por esta comparação.

## Hierarquia de prova

1. **Regra humana/constitucional:** fixa os limites; não comprova código.
2. **Código no SHA indicado:** demonstra uma implementação estática; não comprova execução.
3. **Teste/CI no mesmo SHA:** demonstra apenas o cenário, plataforma e alcance do teste.
4. **Aceitação real num Windows físico:** continua necessária onde o CI não reproduz o ambiente do PC.
5. **Release:** só após revisão, convergência, gates aplicáveis e decisão humana. Nenhuma PR Draft significa release.

## Matriz código → documentação

| Contrato/capacidade | Onde está no código da PR #45 | Verificação estática | Limite da afirmação |
| --- | --- | --- | --- |
| Entrada da Folha | [`nexus/app.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/app.py), [`nexus/ui/`](https://github.com/PAPACREATOR/cerebro-parvo-/tree/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/ui) | Servidor HTTP em `127.0.0.1`, sessão do Host, rotas delimitadas | Não é prova de aceitação física ou de todas as intenções |
| Parser | [`frontdoor.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/frontdoor.py), [`frontdoor_rules.json`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/frontdoor_rules.json) | Sete prefixos; interpretação natural/clarificação; sem autoridade | Reconhecer uma intenção não é executar a operação |
| Ponte linguagem/Markdown | [`natural_bridge.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/natural_bridge.py) | Cabeçalho e hash do texto, ida/volta; fronteira de candidatos cognitivos | Não prova integração de toda a ponte na interface HTTP |
| Operação natural exposta | [`app.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/app.py), [`frontdoor_rules.json`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/frontdoor_rules.json) | `/api/prepare-run` e `/api/confirm-run` só admitem `verify` a partir da proposta natural com anexo | **Não** há correspondência pública automática de sete intenções a dez processos |
| Execução direta | [`app.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/app.py) | `/api/run` só quando `allow_direct_run=True`; `application()` usa a predefinição `False` | Rota de teste/diagnóstico; não a declarar como execução normal da Folha |
| Host e integridade | [`host.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/host.py) | Manifesto de hashes, sessão, execução e verificação de artefactos | O manifesto não substitui revisão/aceitação integral do PC |
| Estado e promoção | [`store.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/store.py), [`approval_binding.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/approval_binding.py) | Pastas de runs, Creative e Canonical; decisão humana vinculada ao conteúdo; recuperação/atomicidade | Existência da lógica não substitui testes de crash, corrupção e Windows real |
| Despachante interno | [`adapters/runner.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/adapters/runner.py) | `PROCESS_TO_TOOL` define dez processos e despacha diretamente dentro da fronteira | **Não** significa dez ações naturais integradas na Folha |
| Isolamento Windows | [`windows_sandbox.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/windows_sandbox.py) | AppContainer, ACL e Job Object, recusa se Windows não disponível | Limita processos que o Host lança; não governa o Windows inteiro |
| MCP opcional | [`mcp_client.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/mcp_client.py), [`requirements-mcp.txt`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/requirements-mcp.txt) | Allowlist, transporte stdio delimitado; SDK separado para MCP | O runner interno **não exige** relay MCP para cada operação |
| OpenNotebook | [`adapters/notebook.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/adapters/notebook.py), [`adapters/product_routes.py`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/adapters/product_routes.py) | Adapter local HTTP e normalização de candidato | Serviço, SurrealDB e modelos físicos não comprovados por esta leitura; não é obrigatório para `verify` |
| Instalação completa | [`windows/install-nexus-complete.ps1`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/windows/install-nexus-complete.ps1) | Percurso completo de provisão externo, com requisitos próprios e `llama.cpp` | Não confundir instalador completo com arranque mínimo; `llama.cpp` **não é Ollama** |

## Os dez processos definidos no despacho

A enumeração de [`schemas/request.json`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/schemas/request.json) coincide com [`PROCESS_TO_TOOL`](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/adapters/runner.py): `verify`, `interpret`, `proofread`, `convert_pdf`, `video`, `podcast`, `visual_podcast`, `book`, `music`, `web`.

**Estado por interface, não por marketing:**

| Família | Implementação encontrada | Entrada natural pública | Aceitação |
| --- | --- | --- | --- |
| `verify` | Runner direto, Host/Store | Proposta delimitada via prepare/confirm, com anexo e confirmação humana | CI parcial da PR #45; aceitação física separada |
| `interpret`, `proofread`, `convert_pdf`, `book` | Adapters internos definidos | Não exposta por mapeamento natural geral da Folha no SHA examinado | Integrações dependem de ferramentas e gates; Writer/LPAC real conserva FAIL na evidência disponível |
| `video`, `podcast`, `visual_podcast` | Rotas internas para planeamento OpenNotebook | Não expostas pelo mesmo mapeamento | Plano/JSON não é vídeo/podcast físico gerado |
| `music`, `web` | Rotas internas que devolvem candidatos estruturados | Não expostas pelo mesmo mapeamento | Não confundir candidatos locais com síntese musical/pesquisa pública reais |

A configuração de regras só tem uma `operation_rule` natural de `verify`; portanto **sete intenções reconhecidas ≠ sete operações autorizadas ≠ dez rotas públicas**.

## Dois momentos de autorização

- **Antes de executar:** a API prepara uma proposta, emite ticket temporário (180 segundos no código), compara o digest exato do pedido na confirmação e só depois chama `Host.start`. Recusa e alteração do pedido não executam.
- **Antes de promover conhecimento:** `Host.prepare_approval`, `Host.approve` e `Store.promote` exigem outra decisão humana ligada à versão/hash do conteúdo.

A confirmação de executar `verify` **não** autoriza, sozinha, passagem para Canonical. A presença do portão no código requer ainda ensaio de regressão no mesmo SHA e, quando aplicável, PC físico.

## Divergências documentais a evitar

- `STATUS.md` e apontamentos de `nexus/docs/PONTO-DE-SITUACAO.md` foram escritos enquanto a PR #32 era a candidata mais avançada. A #32 **continua baseline**, mas a #45 passou a ser uma **integração posterior**, isolada e ainda Draft.
- Documentos de 28/09 a 04/10 com Activepieces/Conductor/Spiff descrevem fases reais, **não requisitos atuais**.
- Descrever MCP como único executor oculta o runner `nexus/python-direct` e a sandbox Windows.
- Não chamar `book` de Writer editorial completo, nem `web` de pesquisa externa pronta, nem `music` de geração musical comprovada.
- Não converter `SUCCESS` em CI de um subconjunto em `PASS` do produto inteiro.

## Próximos gates de reconciliação

1. Reavaliar a matriz no **HEAD definitivo**, já que esta leitura é de `66027af7...`.
2. Comparar documentação, política, schemas, runner e rotas HTTP após convergência; corrigir desvios **no código apenas por outra equipa autorizada**, nunca pela frente documental.
3. Separar resultados de Linux, Windows CI, Windows físico e modelos/serviços reais.
4. Preservar a causa do Writer/LPAC como ainda não demonstrada definitivamente; ver [issue #36](https://github.com/PAPACREATOR/cerebro-parvo-/issues/36).
5. Validar ligações, anchors, privacidade, licenças e revisão humana antes de merge de documentos.

**Âmbito desta auditoria:** só leitura de código, PRs e documentos do GitHub; não foram corridos testes e não houve leitura nem alteração do disco físico do utilizador.
