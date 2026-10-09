# Comparação — orquestração local de ferramentas e processos

Data: 2026-10-09  
Objetivo: estudar código real de motores de processos, não frameworks de agentes.

## Referências fixadas

- NodePilot — `b17eda8dc546202b2b62f9452ef31edec00983c4` — Apache-2.0
- Open Flow — `ff722d8fe8ea20c0a8124e284484937ca4fadcbd` — Apache-2.0
- Sledge — `fd87d3c4ad495a0f8072476cb025db531085cdd3` — MIT
- Dagu — `45f19c0b1f1c0119ade65474e688cff637d8576a` — GPL-3.0
- Electron Workflow Engine — `f6c912dd34a98b230689bd9de2ca7092387b599b` — MIT

Tentativas de `git clone` no ambiente de estudo falharam porque o runtime não resolve `github.com` por DNS. A leitura foi feita pelos objetos/ficheiros públicos do GitHub nos commits acima. Nenhum código foi copiado para o Nexus.

## Padrão 1 — intenção durável antes da execução

### NodePilot

A ADR `0014-durable-execution-dispatch.md` regista a execução `Pending` e o `ExecutionDispatchOutboxItem` **na mesma transação**.

Depois:
1. worker reclama a intenção com lease;
2. gates de política/concurrency são avaliados;
3. só então o engine recebe ownership;
4. falhas antes da execução podem ser repetidas;
5. falhas depois do início da execução não são automaticamente repetidas, porque side effects podem ser ambíguos.

O código em `ExecutionDispatchService.cs` contém explicitamente a regra: depois de engine invocation, retry automático pode duplicar efeitos externos e é suprimido.

Isto confirma a direção Nexus: `PREPARED → EXECUTING → RESULT_ACCEPTED`, com recuperação conservadora.

## Padrão 2 — estado "indeterminate" é uma feature

### Open Flow

Open Flow distingue estados terminais normais de `indeterminate`.

O teste real `process-recovery.test.ts`:
1. inicia um flow;
2. espera até o node estar running;
3. mata o processo;
4. reinicia o servidor;
5. exige que o run fique `indeterminate`, não completed/retried por suposição.

Também usa idempotency keys na admissão de flows, revisions e runs.

Isto é diretamente compatível com a regra Nexus de não repetir side effects cujo outcome não pode ser provado.

## Padrão 3 — evento + materialização + trabalho numa única transação

### Sledge

Sledge é um núcleo pequeno de event/work com SQLite.

Características relevantes:
- append de eventos com `dedupeKey`;
- materialização e criação de trabalho no mesmo limite transacional;
- leases;
- retries;
- dead-letter;
- recovery após restart;
- WAL com verificação explícita de checkpoint.

É um bom benchmark para EventLog/filas/idempotência, mas não justifica outra dependência enquanto Store/EventLog Nexus cobrir os mesmos contratos.

## Padrão 4 — processo declarativo e humano como passo persistente

### Dagu

Dagu é um single binary para DAGs, comandos, PowerShell/shell, retries, paralelismo e human tasks.

A especificação de human task exige que o estado de conclusão sobreviva à saída do processo. O run tem identidade durável própria e o estado da DAG é persistido separadamente da definição fonte.

Também tem MCP como interface de controlo/executar DAGs, mas MCP não é o motor de persistência.

É útil como referência de:
- separar definição de processo e run;
- IDs estáveis de passos;
- waits humanos persistentes;
- retry de passos/downstream;
- snapshot da definição usada por um run.

Por ser GPL-3.0, código não deve ser transportado para Nexus sem análise de compatibilidade. Estudo conceptual/testes apenas.

## Padrão 5 — embed local e recuperação de processo de desktop

### Electron Workflow Engine

É uma biblioteca local para um único Electron app, com SQLite pertencente a utility process.

A recuperação:
- reanexa clientes ao mesmo run;
- não repete activities já checkpointadas;
- permite `resume` ou `pause` após crash;
- testa encerramento abrupto do utility process/app.

É especialmente útil como prova de que um desktop local não precisa de um servidor pesado para ter runs duráveis.

## O que todos ensinam ao Nexus

Os mecanismos recorrentes são pequenos e concretos:

```text
pedido
  ↓
intenção persistida + idempotency key
  ↓
claim/ownership explícito
  ↓
EXECUTING
  ↓
efeito externo
  ↓
resultado durável
  ↓
estado terminal
```

Se houver crash:

```text
antes de EXECUTING → pode tentar novamente
depois de EXECUTING sem resultado provado → BLOCKED/INDETERMINATE
resultado já durável → retomar sem repetir ferramenta
```

Isso é mais importante que escolher um "workflow engine".

## Implicação para o núcleo mínimo

A investigação reforça que o Nexus pode permanecer:

```text
Folha/parser
   ↓
Kernel/Host/Store
   ↓
regras + processo
   ↓
MCP Python/adaptador autorizado
   ↓
ferramenta
```

O que o Kernel precisa garantir, independentemente da ferramenta:

1. identidade estável de run;
2. identidade estável de cada efeito/step;
3. intenção durável antes da execução;
4. ownership/phase explícita;
5. idempotência onde a ferramenta a suporta;
6. nunca confundir retry seguro com side effect ambíguo;
7. persistir resultado antes de avançar;
8. waits humanos duráveis;
9. process/version hash preso ao run;
10. proveniência de input → process → tool → result.

Se estes contratos estiverem cobertos, **não é necessário adicionar Spiff/Conductor/Activepieces**.

Spiff só volta a ser avaliado quando a representação de branches/joins/loops/waits se tornar ela própria uma quantidade relevante de código próprio.

## Regra de reutilização

Aprender padrões e testes é permitido. Copiar implementação só após:
- FAIL concreto no Nexus;
- análise de licença;
- redução comprovada de risco/código;
- preservação de autoridade Kernel-owned;
- teste bidirecional e de crash.
