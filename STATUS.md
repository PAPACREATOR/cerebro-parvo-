# Estado operacional — 28-09-2026

## Arquitetura

**FECHADA — composição mínima governada.**

A arquitetura só reabre por decisão humana explícita ou falha estrutural demonstrada em teste real.

Direção vigente:

- Activepieces WebUI/Chat UI como experiência principal;
- Flows/Subflows/Tables/Storage/MCP/Pieces como orquestração e estado inicial;
- “Core” como função constitucional — regras, permissões, estados e autoridade — não como aplicação Python obrigatória;
- 3 memórias, Creative/Canonical, 3 comparadores, M1–M14 e Human Gate preservados;
- Open Notebook + uma tiny/modelo parametrizado para cognição/semântica;
- K-DLC apenas como provider opcional/substituível de knowledge governance;
- Zotero, LibreOffice, Pinokio/ComfyUI e outros providers como capacidades nos bastidores;
- SQLite/Python/código próprio apenas se um teste real provar que a composição não cumpre uma regra;
- regra permanente: **LIGAR > CONFIGURAR > ADAPTAR > CRIAR**.

## Compatibilidade documental verificada

- Activepieces: Chat UI/Human Input, Tables, Storage, Subflows, MCP e catálogo amplo de Pieces;
- Open Notebook: REST API completa, pesquisa full-text/vector, fontes, chat e controlo de contexto;
- Zotero: API local offline; leitura e escrita autorizada no desktop;
- LibreOffice: headless/CLI e API/UNO;
- Pinokio: instalação e lançamento local de aplicações/servidores;
- ComfyUI: API/backend para workflows locais;
- K-DLC: alinhamento forte com governação, mas especificação 0.2.0 ainda “Draft for implementation”.

Ver [Matriz de compatibilidade](COMPATIBILITY-MATRIX.md).

## Evidência preservada

O código histórico, a implementação ativa e o writer recuperável continuam preservados como evidência técnica/fallback.

No commit `f48382f396e3b4af18e62a15c3ecb6104dfd52c9`:

- GitHub Actions: SUCCESS;
- suite histórica: 34 PASS;
- writer recuperável: 11 PASS;
- total: 45 testes sem falha;
- integridade documental: PASS.

Isto não prova a nova composição E2E.

## O que deixou de ser pressuposto

- Core Python separado;
- SQLite obrigatório;
- writer próprio como primeiro caminho;
- workflow engine próprio;
- motor de pesquisa próprio;
- frontend próprio;
- multiagente;
- adaptadores onde Piece/MCP/API/CLI resolve.

Nada é apagado: permanece disponível como fallback.

## Próximo e único portão estrutural

Provar uma vertical slice preferencialmente sem código próprio:

```
Activepieces WebUI
-> regras/tabelas
-> uma capacidade
-> resultado
-> Creative
-> Human Gate
-> Canonical
```

Depois acrescentar Open Notebook. Os restantes providers entram um a um sem alterar a arquitetura.

## Critério de sucesso

A pessoa usa linguagem natural numa única experiência; não vê processos internos nem precisa de conhecer aplicações auxiliares. As ferramentas trabalham nos bastidores, os resultados regressam à mesma interface e nenhuma IA/provider ganha autoridade.

[Arquitetura](CEREBRO_ARCHITECTURE.md) · [Constituição](CEREBRO_CONSTITUTION.md) · [Decisões](DECISIONS.md) · [Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md)
