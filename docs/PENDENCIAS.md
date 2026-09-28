# Pendências e portões — 28-09-2026

As pendências são testes de comportamento, não uma lista de programas a instalar.

| ID | Portão | Fecho |
| --- | --- | --- |
| P01 | Memory Provider A | Testar RMANOV/sqlite-memory-mcp no Windows + MCP + SQLite |
| P02 | Memory Provider B | Testar Beledarian/mcp-local-memory nas mesmas condições |
| P03 | Escolha | Comparar PASS/FAIL; escolher o que exigir menos adaptação |
| P04 | Activepieces -> MCP | Chamar create/search/relations/provenance sem bridge próprio |
| P05 | 3 memórias | Working, Behavioral e Persistent como papéis lógicos |
| P06 | 3 comparadores | Exato, semântico e relacional separados e cruzados |
| P07 | Creative/Canonical | Contradição preservada; só humano promove |
| P08 | Human Gate | Provider/IA não consegue contornar aprovação |
| P09 | Offline | Internet OFF sem destruir núcleo |
| P10 | Recovery | restart + backup + destroy + restore verificado |
| P11 | Desmontagem | remover provider sem destruir Activepieces/leis; remover Activepieces sem perder SQLite/Canonical |
| P12 | Windows/UX | utilizador não vê SQL/Markdown/IDs/MCP |
| P13 | Licenças | fixar versões MIT/public-domain e notices antes de distribuição |
| P14 | Providers periféricos | só entram por receita/FAIL real |
| P15 | PiecesOS benchmark | opcional; comparar memória, nunca tornar requisito |
| P16 | Eliminação | fora do MVP até existir política humana explícita |

## Candidatos atuais

### A — sqlite-memory-mcp
Pontos a verificar:
- promoção approval-aware nunca pode substituir Human Gate;
- funcionalidades premium/avançadas não podem tornar-se dependência;
- confirmar funcionamento simples/unified MCP no Windows;
- confirmar backup/restore do SQLite.

### B — mcp-local-memory
Pontos a verificar:
- qualidade FTS + vector + temporal + graph;
- lifecycle outdated/incorrect/restore respeita regra de não apagar;
- dependências Node/build tools no Windows;
- backup/restore do SQLite.

## Fora do núcleo até prova contrária

- PiecesOS;
- Open Notebook;
- K-DLC;
- Qdrant;
- Neo4j;
- vector DB separado;
- Python Core novo;
- frontend próprio.

## Critério de decisão

1. cumpre as leis?
2. liga diretamente por MCP?
3. funciona offline?
4. dados ficam num SQLite recuperável?
5. pode ser desligado/substituído?
6. licença permite o nosso uso?
7. exige menos adaptação?

Se empatar, escolher o mais simples.

## Regra permanente

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

**NENHUM COMPONENTE ENTRA SEM UM FAIL QUE O JUSTIFIQUE.**
