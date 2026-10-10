# Plano de execução histórico — Activepieces + Memory Provider

> **Vigência:** a composição deste documento foi superada pela decisão Nexus Minimal de 30-09-2026 em `DECISIONS.md`. É preservada como hipótese histórica e fonte de contratos de teste; não prescreve instalação de Activepieces. Ver `auditoria/CONSOLIDACAO-2026-10-10.md` para o processo de reconciliação e validação.


## Objetivo

Construir o menor Cérebro funcional possível com dois blocos nucleares:
- Activepieces Community;
- Memory Provider local SQLite/MCP.

O humano é a autoridade.

## Fase 0 — comparação do Memory Provider

Testar em igualdade:
- RMANOV/sqlite-memory-mcp;
- Beledarian/mcp-local-memory.

Contrato mínimo:
- Windows;
- MCP acessível pelo Activepieces;
- SQLite local e portátil;
- FTS;
- semântico local ou desligável;
- temporal;
- relações;
- proveniência;
- histórico/contradições;
- sem auto-delete por similaridade;
- restart;
- backup/restore;
- funcionamento sem Internet;
- possibilidade de desligar/substituir.

Critério de escolha: **menos adaptação + menos dependências + mais invariantes PASS**. Não escolher por marketing ou quantidade de tools.

## Fase 1 — vertical slice

```
pedido humano
 -> Activepieces
 -> retrieve Memory Provider
 -> comparadores
 -> recipe
 -> resultado
 -> Creative
 -> Human Gate
 -> Canonical
 -> persistir com proveniência
```

A operação técnica de promoção no Memory Provider só pode ser chamada após aprovação humana.

## Fase 2 — três memórias

- Working: estado Activepieces + contexto temporário;
- Behavioral/Procedural: regras/preferências/correções versionadas;
- Persistent: Memory Provider SQLite com Creative/Canonical.

Não criar três bases.

## Fase 3 — três comparadores

- determinístico/exato;
- semântico;
- relacional.

Temporal/proveniência complementam a decisão mas não concedem autoridade.

## Fase 4 — robustez

- matar Memory Provider durante flow;
- reiniciar sem duplicar ação irreversível;
- matar Activepieces;
- restaurar SQLite;
- exportar Canonical;
- comparar hashes/estado;
- Internet OFF;
- trocar provider mantendo contrato.

## Fase 5 — providers periféricos

Só após FAIL/necessidade real:
- LibreOffice;
- Zotero;
- LanguageTool;
- ComfyUI;
- IA local OpenAI-compatible;
- web explícita;
- email;
- publicação.

Open Notebook/K-DLC só regressam se um teste provar uma função não coberta.

## PiecesOS

Pode ser usado como benchmark para comparar qualidade de memória. Não é requisito do MVP nem do produto.

## Código histórico

Python/writer recuperável permanecem como fallback. Não apagar. Não reativar sem lacuna demonstrada.

## Regra

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

**Nenhum componente entra sem FAIL.**
