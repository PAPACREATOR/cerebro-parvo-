# Estudo — SpiffWorkflow, Microsoft Conductor e MCP Python

Data: 2026-10-09  
Estado: investigação; não altera o runtime ativo.

## Referências exatas

- Nexus PR #32, HEAD analisado inicialmente: `a13d316117024ffc7923bcfc49d5517e8184828e`
- Nexus laboratório Spiff+Conductor: `829764dee6144d05c29fed92bcf6e48829d70ff2`
- Microsoft Conductor 0.1.41: `11dcc41ed3df78f0806127cc901822fe8758294b`
- SpiffWorkflow 3.2.0: `902055aa5c214581c4ca01bbe7dbed79c985c65f`

## Decisão atual

1. **Activepieces:** estudo/referência; fora do produto final.
2. **MCP Python:** manter. É transporte de ferramentas autorizado pelo Kernel.
3. **Conductor:** não restaurar como dependência obrigatória.
4. **SpiffWorkflow:** não tornar obrigatório; manter como candidato opcional para máquina de estados determinística, apenas se um fluxo real o justificar.

## Conductor

O Conductor 0.1.41 é um motor completo, não um wrapper MCP. Inclui routing, checkpoints, limits, scripts, set/wait, human gates, parallel/foreach, subworkflows, providers e gestor MCP próprio.

Observações de código:

- `src/conductor/engine/workflow.py`: ~8.8k linhas.
- `src/conductor/engine/checkpoint.py`: checkpoints JSON em diretório temporário, `.tmp → rename`.
- `src/conductor/mcp/manager.py`: usa diretamente o SDK Python MCP por stdio.
- Conductor 0.1.41 declara `mcp>=1.28.1,<2`.
- Nexus candidato fixa `mcp==1.23.2` + `trio==0.34.0`.
- Uma chamada MCP interrompida com outcome externo desconhecido pode ser retomada com semântica at-least-once; isso pode repetir o passo mediante decisão de resume.

Para Nexus, o Kernel já possui o contrato de durabilidade, hashes, recovery e bloqueio conservador. Reintroduzir Conductor duplicaria grande parte dessas responsabilidades e acrescentaria um segundo runtime de execução.

Os 5.000/5.000 testes históricos continuam valiosos: provaram que Spiff e Conductor podiam trabalhar subordinados ao Kernel no laboratório. Não provaram necessidade arquitetural.

## SpiffWorkflow

Spiff é mais interessante como **máquina de estados/BPMN**:

- exclusive/parallel gateways;
- joins;
- loops;
- sequential/parallel multi-instance;
- manual/user tasks;
- subworkflows;
- serialização/deserialização de estado.

Isso pode evitar escrever um mini-engine próprio quando aparecer um processo realmente complexo.

Mas existem superfícies que o Nexus não deve permitir:

- `Execute` pode lançar subprocessos;
- `Transform` usa `exec()`;
- ScriptTask/ServiceTask podem executar através do script engine.

Se Spiff for testado no futuro, o adaptador Nexus deve aceitar apenas um subconjunto passivo de máquina de estados. Toda capability externa volta ao Kernel e daí a MCP/adaptador autorizado.

## Forma preferida

Fluxo simples:

```text
Folha → Kernel → MCP/adaptador → ferramenta → Kernel → humano
```

Fluxo complexo, apenas se necessário:

```text
Folha → Kernel → Spiff (estado)
                    ↓
             pedido de capability
                    ↓
         Kernel dispatcher → MCP → ferramenta
                    ↑                    ↓
                    └── resultado durável┘
```

## Gate antes de Spiff entrar

Spiff só deve tornar-se dependência do produto se um laboratório isolado provar:

- fluxo real materialmente mais simples/legível do que a rota direta;
- allowlist de classes/task types;
- bloqueio de Execute/Transform/script/service execution;
- `dispatch_id` determinístico Kernel-owned para cada efeito externo;
- crash depois de tool PASS não repete a tool;
- crash antes de resultado durável dá BLOCKED/RECOVERY_REQUIRED;
- alteração do hash do processo durante recovery é rejeitada;
- HumanDecision continua Nexus-owned e ligada ao hash exato;
- estado Spiff é persistido através do Store durável;
- Nexus continua funcional e verde sem Spiff instalado.

Até esse gate passar, a recomendação é: **MCP Python sim; Conductor não; Spiff laboratório opcional.**
