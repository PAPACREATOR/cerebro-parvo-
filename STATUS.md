# Estado atual do Nexus

O estado operacional corrente está em [nexus/docs/PONTO-DE-SITUACAO.md](nexus/docs/PONTO-DE-SITUACAO.md).

A implementação candidata ativa está na **PR #32**, branch `cleanup/llamacpp-only-20261007`. A issue #33 fixa a convergência final sem novas funcionalidades por antecipação.

## Composição candidata

- Folha + parser determinístico;
- Kernel / Host / Store;
- regras, schemas e allowlists;
- MCP Python e adaptadores autorizados;
- ferramentas externas delimitadas;
- Creative → Human Gate → Canonical.

Activepieces e Conductor não são dependências do produto candidato.

SpiffWorkflow permanece apenas candidato de laboratório para fluxos determinísticos realmente complexos. Não é requisito atual.

## Regras vigentes

- Humano é a autoridade máxima.
- Kernel/Host/Store mantêm estado, política, Creative, Human Gate, Canonical e recovery.
- MCP é transporte, não autoridade.
- Ferramentas externas não recebem autoridade Nexus.
- Tiny/IA é opcional, delimitada e sem autoridade.
- Arquitetura conceptual M1–M14 permanece congelada.
- Conhecimento Canonical não é eliminado automaticamente salvo duplicação absolutamente exata.
- FAIL, BLOCKED e NOT RUN não contam como PASS.
- Side effects externos de outcome ambíguo não são repetidos silenciosamente após crash.

## Fonte de verdade

Não criar ficheiros de estado/handoff por sessão.

Atualizar apenas:

1. `nexus/docs/PONTO-DE-SITUACAO.md` para estado operacional;
2. PR #32 para commits, testes, FAIL → correção → PASS e próximos gates;
3. relatórios específicos quando houver evidência técnica nova;
4. `docs/00-start-here/` e os índices de navegação apenas quando mudar a organização documental.

O histórico anterior permanece no Git, em `historico/`, em relatórios datados e nos PRs fechados.
