# Estado atual do Nexus

**Reconciliação documental de 10-10-2026:** ver [fotografia datada](docs/10-current/ESTADO-DOCUMENTAL-2026-10-10.md), [compatibilidade com código no SHA da PR #45](docs/10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) e [matriz de provas](docs/60-evidence/MATRIZ-PRS-2026-10-10.md). PR #45 permanece Draft; PR #48 não prova espelho completo do PC. Não houve teste físico nem release nesta reconciliação.

O [ponto de situação acumulado](nexus/docs/PONTO-DE-SITUACAO.md) conserva os ciclos de execução e a abertura de 08/10; **não representa, isoladamente, a posterior integração experimental da PR #45**. Para implementação concreta, conferir o HEAD de código e a matriz datada.

A **PR #32** (`cleanup/llamacpp-only-20261007`, `da86b6dd...`) é a **baseline Windows**. A **PR #45** (`integration/nexus-unified-candidate-20261009`, `66027af7...`) é a **integração candidata posterior**, isolada e ainda Draft; não está em `main`. A issue #33 fixa a convergência final sem novas funcionalidades por antecipação.

## Composição candidata

- Folha + parser determinístico (sete intenções reconhecidas; na API pública normal, apenas a proposta natural `verify` é encaminhada para execução após confirmação no SHA auditado);
- Kernel / Host / Store;
- regras, schemas e allowlists;
- runner direto sob fronteira Windows e MCP Python opcional para ferramentas autorizadas (MCP não é relay universal);
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
