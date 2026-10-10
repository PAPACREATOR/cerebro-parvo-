# Start here — Nexus / Cérebro Local

Este é o ponto de entrada recomendado para quem chega ao repositório pela primeira vez. [Mapa completo](../README.md) · [Decisões e razões](../40-decisions/README.md) · [História](../99-history/README.md).

## Em uma frase

Nexus é um sistema Windows local-first em que a pessoa continua autoridade final. A Folha recebe linguagem natural; o Kernel valida regras, estado e limites; MCP/adaptadores chamam ferramentas; resultados ficam em Creative; só uma decisão humana explícita pode promover conteúdo para Canonical.

## Ler nesta ordem

1. [Núcleo mínimo atual](../20-architecture/MINIMUM-CORE.md)
2. [Estado operacional](../../nexus/docs/PONTO-DE-SITUACAO.md)
3. [Onde ajudar](../30-help/README.md)
4. [Constituição](../../CEREBRO_CONSTITUTION.md)
5. [Arquitetura](../../CEREBRO_ARCHITECTURE.md)
6. [Decisões](../../DECISIONS.md)

## Código ativo

O candidato Windows atual está em [nexus/](../../nexus/). A baseline candidata está na PR #32; a PR #45 é posterior, isolada e Draft. A direção é a issue #33. Ver [matriz de PRs](../60-evidence/MATRIZ-PRS-2026-10-10.md).

As pastas `implementacao/` e `historico/` preservam genealogia, experiências e versões anteriores. Não devem ser usadas como fonte de verdade do runtime atual.

## Regra de leitura

Quando documentação antiga contradiz código/testes atuais:

1. Constituição e invariantes continuam vigentes.
2. O código do candidato atual e a evidência por SHA decidem a implementação física.
3. `nexus/docs/PONTO-DE-SITUACAO.md` decide o estado operacional.
4. Documentos históricos explicam como se chegou aqui; não mandam reinstalar componentes removidos.

## English quick summary

Nexus is a Windows local-first, human-authority system. The user writes in a simple sheet; the Kernel owns policy, state, provenance, approval and recovery; MCP/adapters are bounded tool transports; external tools have zero authority over Canonical knowledge.

Current contributors should start with PR #32 and issues #35–#39. Do not redesign the architecture or weaken Windows isolation to make a test pass.
