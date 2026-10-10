# Estado atual do Nexus

O estado operacional corrente está em [nexus/docs/PONTO-DE-SITUACAO.md](nexus/docs/PONTO-DE-SITUACAO.md). Em 10-10-2026, `main` observado é `bfae55239d3803f3580f4ae29b7dfe99fec747a9`: convergência da [PR #51](https://github.com/PAPACREATOR/cerebro-parvo-/pull/51) e roteamento das dez capacidades da [PR #53](https://github.com/PAPACREATOR/cerebro-parvo-/pull/53), ambas integradas. A PR #23 conserva a genealogia anterior. Integração em Git não certifica instalação nem serviços completos no PC.

## Regras que continuam vigentes

- Humano é a autoridade máxima.
- Kernel/Host/Store mantêm estado, política, Creative, Human Gate e Canonical.
- MCP é transporte, não autoridade.
- OpenNotebook, LibreOffice, LanguageTool, Zotero, ACE-Step, Forge e outras integrações são ferramentas externas.
- Tiny/IA é opcional, delimitada e sem autoridade.
- Arquitetura conceptual M1–M14 permanece congelada; implementação e testes não autorizam redesenho implícito.
- Conhecimento Canonical não é eliminado automaticamente salvo duplicação absolutamente exata.
- FAIL, BLOCKED e NOT RUN não contam como PASS.

## Fonte de verdade

Não criar novos ficheiros de “estado”, “continuidade”, “fila” ou “handoff” por sessão.
Atualizar apenas:

1. `nexus/docs/PONTO-DE-SITUACAO.md` para o estado operacional;
2. a PR correspondente à tarefa atual para commits, testes, FAIL→correção→PASS e próximos gates;
3. relatórios específicos quando houver evidência técnica nova.

O histórico anterior permanece no Git e nos PRs fechados, sem ser duplicado na árvore ativa.
