# Estado operacional — 28-09-2026

## Direção vigente

Arquitetura simplificada para composição mínima:

- Activepieces WebUI como única porta de entrada;
- Activepieces Flows/Subflows/Tables/Storage/MCP/Pieces como orquestração e estado inicial;
- “Core” tratado como função constitucional (regras, permissões, estados e autoridade), não como aplicação Python obrigatória;
- 3 memórias, Creative/Canonical, 3 comparadores, M1–M14 e Human Gate preservados;
- Open Notebook + uma tiny parametrizada para cognição/semântica;
- K-DLC como provider opcional de knowledge governance quando cumprir as regras;
- Zotero, LibreOffice, Pinokio e outros providers como capacidades externas;
- SQLite e Python entram apenas se uma lacuna real, demonstrada por teste, exigir;
- princípio vigente: **LIGAR > CONFIGURAR > ADAPTAR > CRIAR**.

## O que permanece válido do trabalho anterior

O código histórico, a implementação ativa e o writer recuperável continuam preservados como evidência técnica e fallback.

No commit `f48382f396e3b4af18e62a15c3ecb6104dfd52c9`:

- GitHub Actions: SUCCESS;
- suite histórica: 34 PASS;
- writer recuperável: 11 PASS;
- total: 45 testes sem falha;
- integridade documental: PASS.

Isto não prova a nova composição em Activepieces.

## O que deixou de ser pressuposto do MVP

- Core Python separado;
- SQLite obrigatório;
- writer próprio como primeiro caminho;
- motor de pesquisa próprio;
- adaptadores próprios onde Piece/MCP/API/CLI já resolva.

Nada é apagado: estes componentes ficam disponíveis se a composição provar que são necessários.

## Próximo portão real

Construir uma única vertical slice sem código próprio sempre que possível:

```
Activepieces WebUI
-> regras/tabelas
-> uma capacidade externa
-> resultado
-> Creative
-> Human Gate
-> Canonical
```

Depois acrescentar Open Notebook e provar uma tarefa semântica com a mesma tiny parametrizada.

Só depois integrar Zotero, LibreOffice, Pinokio/imagem e restantes capacidades.

## Critério de sucesso

A pessoa escreve normalmente numa única interface; as ferramentas trabalham nos bastidores; o resultado regressa à mesma experiência; nenhuma IA ou provider externo ganha autoridade; Creative/Canonical e memórias mantêm-se coerentes.

[Arquitetura vigente](CEREBRO_ARCHITECTURE.md) · [Decisões](DECISIONS.md) · [Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md)
