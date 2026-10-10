# ADR — motores de processo e MCP

Data: 09-10-2026. Estado: **orientação de arquitetura candidata** documentada na PR #41.

**Questão:** acrescentar Activepieces, Conductor ou Spiff ao núcleo reduz trabalho ou duplica o que o Kernel/Host já faz?

**Decisão atual:** Activepieces fica como estudo histórico, não dependência final; Conductor fora da candidata; SpiffWorkflow apenas hipótese em laboratório para um fluxo real que prove necessidade de gateways/joins/esperas; MCP Python mantém-se como transporte de ferramentas quando adequado, e chamadas diretas também são válidas sob controlo do Host.

**Porquê:** a duplicação de motores aumenta estados e recuperação a reconciliar. O comportamento at-least-once de chamadas externas não permite assumir repetição segura de efeitos ambíguos. Para sequências simples, Kernel + regras + adaptador tem fronteiras mais curtas.

**O que se preserva:** os testes, estudos e versões de Activepieces/Conductor/Spiff. A exclusão do runtime candidato **não apaga** a hipótese nem converte estudos em falhas intrínsecas das ferramentas.

**Reabertura possível:** FAIL documentado ou microprocesso real cuja complexidade torne a ferramenta objetivamente mais simples, com isolamento, licenças e gates iguais ou melhores. Nunca por preferência estética.

Fontes: [PR #41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41), [estudo comparativo](../90-research/SPIFF-CONDUCTOR-MCP.md), [Constituição](../../CEREBRO_CONSTITUTION.md).