# Matriz de fronteiras — estado real

| Fronteira | Contrato exigido | Evidência atual |
| --- | --- | --- |
| Folha → Core | Intenção/referência, linguagem normal, IDs internos | UI ausente; IMP-001 recebe Path local |
| Core → Activepieces | Capacidade, IDs, permissões, timeout, retorno correlacionado | Callback no candidato; sem workflow real |
| Ferramenta/IA → Core | Resultado não confiável, schema, limites, sem autoaprovação | Funções mínimas/testes; isolamento real NOT RUN |
| Candidato → Creative | Apenas READY, identidade/proveniência, eventos antes de materialização | Dicionário candidato; não persistência completa |
| Creative → Canonical | Portão humano específico e genealogia | Promoção funcional ausente |
| Core → EventLog/SQLite/Markdown | Protocolo autoritativo, recibos, replay e crash recovery | IMP-019 bloqueado; G10 POR DEFINIR |
| Autoritativo → FTS/cache | Derivado reconstruível | Apenas estado UPDATED/DIRTY; rebuild real ausente |
| Pedido → eliminação | Autorização específica/atual, efeito restrito, auditoria | IMP-026 bloqueado; retenção/original POR DEFINIR |

[Contratos](docs/CONTRATOS-IMP.md) · [Matriz por módulo/IMP](docs/MATRIZ-CONFORMIDADE.md).
