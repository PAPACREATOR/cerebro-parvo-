# Decisões e hipóteses substituídas — com motivo

## Activepieces como orquestrador obrigatório
**Antes:** centro de fluxos e estado temporário. **Agora:** estudo/referência. **Porquê:** no candidato Host/Kernel + regras + transportes delimitados evitam duplicação de execução, estado e autoridade. Não foi apagado do histórico. Ver [ADR motores](../40-decisions/ADR-2026-10-09-MOTORES-E-MCP.md).

## Conductor como condutor principal
**Antes:** routing, scripts, waits e MCP por motor externo. **Agora:** não dependência candidata. **Porquê:** repetia tarefas do Kernel/Host e levantava questões de retries de side effects ambíguos. A exclusão não afirma que a ferramenta é insegura universalmente.

## SpiffWorkflow como requisito
**Antes:** hipótese de engine para processos. **Agora:** laboratório opcional. **Porquê:** sem caso real de joins/gateways que vença uma solução mínima direta, o custo/estado extra não está justificado.

## OpenNotebook obrigatório ou descartável por classificação automática
**Antes:** bancada cognitiva descartável; investigação previa KEEP/OPTIONAL/REMOVE do produto base. **Agora:** ferramenta **especializada e valorizada**, selecionada por tarefa, nunca eixo obrigatório. **Porquê:** não perder capacidade editorial, mas também não perder autonomia do Kernel. Ver [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42).

## MCP como relay para todas as capacidades
**Antes:** usar um relay interno até entre operações nativas. **Agora:** PR #32 candidata compara transporte com via direta sob a mesma fronteira. **Porquê:** reduzir fronteiras e duplicação; MCP externo continua útil sem conferir autoridade.

## PASS de vários ramos como produto pronto
**Antes:** relatórios locais podiam ser lidos como progresso global. **Agora:** a convergência só fecha com um HEAD, suites aplicáveis e aceitação física. **Porquê:** versões e ambientes não são intercambiáveis.

## Sandy como integração imediata
**Antes:** investigação de sandbox Windows com contacto técnico. **Agora:** integração suspensa por decisão humana em 10/10. **Porquê:** reduzir trabalho paralelo e manter prioridades; atribuição ao autor Hrvoje Abraham preservada. Suspender não elimina estudo nem constitui juízo técnico sobre a ferramenta.

A reversão de escolha técnica nunca permite apagar FAILs, citações, créditos, documentos de época ou evidência incompatível.