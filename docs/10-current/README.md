# Estado atual — navegação

Este diretório não duplica a execução. Serve de mapa para a [fotografia de 10/10](ESTADO-DOCUMENTAL-2026-10-10.md) e a [auditoria código-documentação da PR #45](COMPATIBILIDADE-CODIGO-2026-10-10.md), ambas com SHA e limites. Não afirma aprovação física.

## Fonte de verdade

- Relatório operacional acumulado (abertura de 08/10): [nexus/docs/PONTO-DE-SITUACAO.md](../../nexus/docs/PONTO-DE-SITUACAO.md). Ler cada ciclo pelo respetivo SHA.
- Baseline Windows: PR #32 — `cleanup/llamacpp-only-20261007`; integração posterior: PR #45, Draft, HEAD examinado `66027af7...`, sem merge
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
Runner direto protegido ou MCP Python autorizado
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

Activepieces, Conductor e Spiff não são dependências do runtime candidato atual. **Sete prefixos interpretados e dez processos internos não equivalem a dez operações disponíveis na Folha**; a rota natural pública comprovável pelo código examinado é `verify`, com ticket pré-execução.

## Importante

PASS histórico não transforma automaticamente o HEAD atual em release. FAIL/BLOCKED/NOT RUN continuam explícitos até prova reproduzível.
