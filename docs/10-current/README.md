# Estado atual — navegação

Este diretório não duplica o estado operacional. Serve apenas como mapa. A [fotografia de 10/10](ESTADO-DOCUMENTAL-2026-10-10.md) documenta refs e lacunas, sem substituir a fonte operacional.

## Fonte de verdade

- Estado detalhado: [nexus/docs/PONTO-DE-SITUACAO.md](../../nexus/docs/PONTO-DE-SITUACAO.md)
- Baseline candidata: PR #32 — cleanup/llamacpp-only-20261007; PR #45 é integração posterior Draft, sem merge
- Direção de convergência: issue #33
- Pedidos públicos de ajuda: issues #35–#39

## Composição candidata

```text
Folha / parser
      ↓
Kernel / Host / Store
      ↓
regras + schemas + allowlists
      ↓
MCP Python ou adaptador direto autorizado
      ↓
ferramenta externa delimitada
      ↓
resultado + trace + proveniência
      ↓
Creative
      ↓
Human Gate
      ↓
Canonical
```

Activepieces, Conductor e Spiff não são dependências do runtime candidato atual.

## Importante

PASS histórico não transforma automaticamente o HEAD atual em release. FAIL/BLOCKED/NOT RUN continuam explícitos até prova reproduzível.
