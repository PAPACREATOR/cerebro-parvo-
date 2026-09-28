# Matriz de fronteiras — estado real

| Fronteira | Contrato exigido | Evidência atual |
| --- | --- | --- |
| Folha/Activepieces Chat → Core | Intenção/referência, linguagem normal, IDs internos ocultos | UI alvo definida; integração real ainda NOT RUN |
| Core → Activepieces | Capacidade, IDs, permissões, timeout, retorno correlacionado | Callback no candidato; sem workflow real |
| Activepieces → Piece/MCP/API/CLI | Execução sem autoridade, permissões mínimas, retorno correlacionado | Desenho definido; integração real NOT RUN |
| Core → Open Notebook | Um notebook reutilizável; contexto/fontes mínimos; tiny IA sem memória autoritativa | Desenho definido; integração real NOT RUN |
| Ferramenta/IA → Core | Resultado UNTRUSTED, schema comum, evidência/fontes, limites | Funções mínimas/testes; isolamento real NOT RUN |
| Resultado → 3 comparadores | Determinístico + semântico + relacional conforme tarefa | Baseline definida; integração E2E ausente |
| Candidato → Creative | Apenas estado permitido, identidade/proveniência, eventos antes de materialização | Dicionário candidato; persistência completa ausente |
| Creative → Canonical | Portão humano específico, genealogia preservada, Creative não apagado | Promoção funcional ausente |
| Creative/Canonical → Markdown | Mesma mecânica física possível, autoridade distinta | Contrato conceptual; materialização completa ausente |
| Core → SQLite | IDs, relações, proveniência, genealogia, estados, permissões, eventos, FTS/índices; não terceiro cofre | IMP-019 bloqueado; G10 POR DEFINIR |
| Autoritativo → FTS/cache | Derivado reconstruível | Apenas estado UPDATED/DIRTY; rebuild real ausente |
| Pedido → eliminação | Autorização específica/atual, efeito restrito, auditoria | IMP-026 bloqueado; retenção/original POR DEFINIR |

[Contratos](docs/CONTRATOS-IMP.md) · [Arquitetura operacional](docs/ARQUITETURA-OPERACIONAL-ADAPTATIVA.md) · [Matriz por módulo/IMP](docs/MATRIZ-CONFORMIDADE.md).
