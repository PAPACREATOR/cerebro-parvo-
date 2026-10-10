# Núcleo mínimo atual

Data: 2026-10-09  
Estado: decisão de implementação candidata; arquitetura conceptual M1–M14 não reaberta. [Fronteiras](FRONTEIRAS-DE-AUTORIDADE.md) · [Decisões](../40-decisions/README.md) · [Evidências](../60-evidence/README.md).

## Hipótese mínima

O produto mínimo pode ser composto por:

1. **Folha + parser determinístico** — recebe o pedido e classifica apenas o necessário.
2. **Kernel / Host / Store** — autoridade, estado, integridade, recovery, proveniência, Creative/Canonical e Human Gate.
3. **Regras + schemas** — contratos explícitos, allowlists, limites e validação.
4. **MCP Python** — transporte delimitado para ferramentas quando MCP for a interface adequada.
5. **Adaptadores diretos mínimos** — apenas quando uma ferramenta não precisa de MCP ou quando a fronteira direta é mais simples e mais segura.
6. **Ferramentas externas** — LibreOffice, LanguageTool, Zotero, OpenNotebook, ffmpeg e outras, sempre subordinadas ao Kernel.

## O que não é obrigatório

- Activepieces: estudo/referência apenas.
- Conductor: não é dependência candidata.
- SpiffWorkflow: candidato opcional de laboratório apenas para processos determinísticos realmente complexos.
- LLM/agente: nunca é o motor de autoridade nem requisito para os fluxos determinísticos.

## Porque isto pode chegar

MCP resolve o contrato uniforme de chamada de ferramentas; o Kernel já resolve autoridade, persistência, hashes, recovery e bloqueio conservador. Para fluxos simples, acrescentar um motor de workflows apenas duplica responsabilidades.

Exemplo:

```text
Folha → Kernel → MCP Python → LanguageTool → Kernel → Creative → humano
```

Não é necessário BPMN para uma sequência simples.

## Quando um motor de processos seria justificado

Só perante um fluxo real com complexidade suficiente, por exemplo:

```text
A → [B e C em paralelo] → juntar → D
                  ↓
             esperar humano
                  ↓
                  E
```

e apenas se implementar joins, loops, multi-instance, waits e serialização diretamente no Kernel criar mais código/risco do que integrar uma máquina de estados externa.

## Regra de entrada de dependências

**Nenhum componente entra porque parece útil. Entra apenas quando um FAIL ou um fluxo real demonstra uma lacuna concreta.**

A dependência tem ainda de provar:

- pode ser desligada sem destruir o Nexus;
- não ganha autoridade sobre Store/Canonical;
- não contorna a sandbox Windows;
- não repete side effects ambíguos após crash;
- não enfraquece Human Gate;
- não altera as invariantes.
