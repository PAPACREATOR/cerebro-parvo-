# Estado atual — navegação

Este diretório não duplica o estado operacional. Serve apenas como mapa.

## Fonte de verdade

- Estado detalhado: [nexus/docs/PONTO-DE-SITUACAO.md](../../nexus/docs/PONTO-DE-SITUACAO.md)
- Candidato ativo: PR #32 — `cleanup/llamacpp-only-20261007`
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
