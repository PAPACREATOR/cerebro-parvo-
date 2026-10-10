# ADR — confirmação humana em dois momentos

Data: 09–10/10/2026. Estado: **contrato normativo**; integração completa pendente.

**Risco:** interpretar uma frase como comando executável sem confirmação, confundir negação ou citação com intenção positiva, ou tomar uma confirmação de operação por autorização para Canonical.

**Decisão:** Folha/parser faz proposta, nunca executa. Para a rota natural limitada de verificar um ficheiro, é exigida confirmação pré-execução ligada à operação e ao anexo/bytes específicos. Edição/rejeição/replay/restart exigem nova confirmação. O Host revalida independentemente. Após executar e validar, resultados vão para Creative; promoção para Canonical exige **outro** Human Gate explícito.

**Porquê:** proteção contra execução inesperada e contra promoção não autorizada são riscos distintos. Uma única aprovação genérica criaria bypass. Side effects ambíguos não são repetidos para “completar” uma tarefa.

**Evidência:** PR #43 propõe a rota natural verify; PR #45 registou FAIL-first com interpretações perigosas de negações e uma correção com testes parciais. Isso não significa sete intenções totalmente ligadas nem E2E físico universal.

Fontes: [PR #43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), [fronteiras](../20-architecture/FRONTEIRAS-DE-AUTORIDADE.md).