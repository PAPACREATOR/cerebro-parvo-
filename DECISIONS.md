# Decisões vigentes e respetiva origem

## 28-09-2026 — arquitetura mínima por composição (vigente)

Pedro fechou a direção operacional: preservar integralmente as leis do Cérebro, mas não programar mecanismos que ferramentas maduras já fornecem.

Decisões vigentes:

- a arquitetura conceptual mantém 3 memórias, Creative/Canonical, 3 comparadores, M1–M14, proveniência, genealogia, contradições, recuperação e autoridade humana;
- o “Core” é uma função lógica/constitucional, não uma obrigação de existir como aplicação Python separada;
- no MVP, tentar expressar Core/autoridade com **Activepieces WebUI + Flows/Subflows + Tables/Storage + regras/configuração**;
- Activepieces é simultaneamente porta de entrada e orquestrador técnico;
- as capacidades reais são providers substituíveis chamados por Piece/MCP/API/CLI;
- Open Notebook é a bancada cognitiva/semântica; usa uma única tiny adaptável por parâmetros/contexto e nunca é autoridade;
- K-DLC pode servir como provider de KNOWLEDGE_GOVERNANCE quando cumprir as nossas regras; não substitui a Constituição;
- Zotero fornece referências; LibreOffice fornece documentos; Pinokio pode alojar providers locais de imagem/áudio; outras capacidades entram apenas quando necessárias;
- Working Memory pode usar estado do flow/Tables/Storage; Behavioral/Procedural Memory pode usar Tables versionadas; Persistent Knowledge mantém Creative/Canonical em formatos abertos;
- comparação determinística, relacional e semântica pode ser feita por providers diferentes e cruzada no flow; não requer três motores próprios;
- SQLite deixa de ser obrigatório no MVP: entra apenas se Tables/Storage/providers não cobrirem pesquisa, relações, eventos ou recuperação necessários;
- Python deixa de ser obrigatório no MVP: só entra perante lacuna comportamental demonstrada por teste;
- nenhum provider externo recebe autoridade para promover Canonical;
- pessoa continua autoridade final; IA nunca aprova conhecimento;
- critério permanente passa a ser **LIGAR > CONFIGURAR > ADAPTAR > CRIAR**;
- não adicionar serviço, base de dados, agente ou aplicação enquanto um flow + provider existente cumprir o comportamento requerido.

Modelo operacional:

```
Pessoa
  -> Activepieces WebUI
  -> regras + estado + flows
  -> capability/provider
  -> resultado UNTRUSTED quando aplicável
  -> Creative
  -> Human Gate
  -> Canonical / ação autorizada
```

O valor próprio do projeto fica concentrado nas leis, nos estados, nas tabelas e nos flows que fazem ferramentas maduras cooperarem sob autoridade humana.

## 28-09-2026 — consolidação por comparação (histórica)

A decisão anterior introduziu Activepieces como oficina operacional, um Core pequeno, Open Notebook único, Creative/Canonical, SQLite e o princípio usar > adaptar > criar. Continua válida como genealogia, mas a decisão vigente acima simplifica-a: Core e SQLite deixam de ser componentes físicos obrigatórios no MVP.

## Evidência

As suites existentes continuam a demonstrar apenas o código já implementado. Não provam ainda a nova composição sem-código/low-code. Esta arquitetura deve ser validada por uma vertical slice real em Activepieces.
