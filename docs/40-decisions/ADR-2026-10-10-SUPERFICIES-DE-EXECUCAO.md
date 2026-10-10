# ADR — separar reconhecimento, execução interna e capacidade pública

**Data:** 10/10/2026. **Estado:** reconciliação documental de comportamento observado; não é aprovação de nova funcionalidade.

## Problema

A comunicação do Nexus pode confundir três superfícies diferentes: o parser reconhecer sete intenções, o runner conter dez processos e a Folha disponibilizar efetivamente operações naturais. Confundir estas camadas faria o utilizador esperar uma execução que o servidor atual recusa por segurança.

## Decisão documental

Documentar **separadamente**:

1. **Compreensão:** o parser aceita sete prefixos/intents e reconhece alguns padrões naturais, devolvendo RESOLVED/UNRESOLVED/BLOCKED conforme a entrada.
2. **Seleção autorizada:** a única `operation_rule` em `frontdoor_rules.json` no SHA auditado propõe `verify` para pedido de verificação de integridade de ficheiro com anexo.
3. **Exposição HTTP pública:** `/api/prepare-run` e `/api/confirm-run` aceitam o percurso natural limitado, com confirmação pré-execução. A rota `/api/run` está desativada no arranque normal, salvo diagnóstico explícito.
4. **Despacho interno:** dez processos aparecem no schema/runner; existência do adapter não significa exposição pública nem aceitação física.
5. **Persistência/Canonical:** promoção exige outro portão humano, após validação do resultado.

## Porque esta formulação

A interpretação linguística não confere autoridade. A recusa é comportamento de segurança deliberado, não prova de que uma capacidade futura já funciona. Esta separação também permite que os técnicos testem o core e adapters sem chamar «produto acabado» à Folha.

## Evidência de código, imutável por SHA

- [Regras e sete prefixos](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/frontdoor_rules.json).
- [Parser e seleção da operação](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/frontdoor.py).
- [API pública, prepare/confirm e rota de diagnóstico](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/app.py).
- [Schema com dez processos](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/schemas/request.json) e [dispatcher direto](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/adapters/runner.py).
- [Store e aprovação humana](https://github.com/PAPACREATOR/cerebro-parvo-/blob/66027af7f2ea084bc62d85b840d1fc3113e60a97/nexus/store.py).

## Consequências

- README e STATUS passam a dizer «dez processos internos», mas «uma rota natural pública limitada» no SHA examinado.
- Descrever sete prefixos como sete comandos E2E passa a ser **afirmação não suportada**.
- A futura ligação de outros processos à Folha é trabalho de implementação sujeito a testes e autorização, **fora do âmbito da PR documental**.
- MCP continua opcional como protocolo externo; o runner do Host é direto e protegido.
- A classificação exige nova leitura de código após alteração do HEAD.

## Não demonstra

Esta decisão não executou testes, não instalou nada no PC, não corrigiu Writer/LPAC, não provou a stack OpenNotebook real e não aprova merge nem release. Ver [matriz técnica](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md).
