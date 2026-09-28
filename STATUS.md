# Estado operacional — 28-09-2026

## Estado

**ARQUITETURA CONCEPTUAL ESTÁVEL; COMPOSIÇÃO FÍSICA EM TESTE.**

Não declarar o Memory Provider escolhido antes de teste comparativo.

## Núcleo candidato

```
Humano
  |
  v
Activepieces Community (MIT)
  |
  | MCP
  v
Memory Provider local (MIT)
  |
  v
SQLite (public domain)
```

Candidatos:
- A: RMANOV/sqlite-memory-mcp;
- B: Beledarian/mcp-local-memory.

PiecesOS: benchmark/opção experimental, não dependência.

## O que está preservado

- 3 memórias;
- Creative/Canonical;
- 3 comparadores;
- Human Gate;
- M1–M14;
- proveniência/genealogia/contradições;
- regras versionadas;
- IA sem autoridade;
- recuperação verificável;
- provider swap.

## Licenças verificadas

- Activepieces core: MIT; Enterprise separado/comercial;
- sqlite-memory-mcp: MIT;
- mcp-local-memory: MIT;
- SQLite: public domain;
- PiecesOS: proprietário;
- código/documentação próprios do Cérebro: PolyForm Noncommercial 1.0.0.

Antes de distribuição final, fixar versões e THIRD_PARTY_NOTICES.

## O que saiu do núcleo

- PiecesOS obrigatório;
- Open Notebook obrigatório;
- K-DLC runtime;
- vector DB separado;
- Qdrant/Neo4j;
- motor de pesquisa próprio;
- Core Python obrigatório;
- frontend técnico/Markdown para o utilizador.

## Evidência histórica preservada

No commit `f48382f396e3b4af18e62a15c3ecb6104dfd52c9`:
- GitHub Actions SUCCESS;
- 34 testes históricos PASS;
- 11 writer tests PASS;
- total 45 PASS.

Isto não prova a nova composição E2E.

## Próximo portão

Executar o mesmo teste nos dois Memory Providers:

1. instalação Windows;
2. Activepieces -> MCP;
3. create/read/update;
4. FTS/exato;
5. semântico;
6. temporal;
7. entidades/relações;
8. proveniência;
9. contradições preservadas;
10. Creative -> Human Gate -> Canonical;
11. provider não consegue promover sozinho;
12. restart;
13. backup -> destruir -> restore;
14. desligar Internet;
15. desligar Memory Provider sem destruir leis/configuração Activepieces;
16. desligar Activepieces sem perder SQLite/Canonical.

Escolher o provider apenas pelos resultados.

## Regra operacional

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**
