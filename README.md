# Nexus / Cérebro Local

Sistema Windows local-first de criação, conhecimento e execução governada. A pessoa escreve numa Folha simples; o Kernel valida regras, estado e limites; MCP/adaptadores chamam ferramentas; a pessoa continua autoridade final.

> **Novo no projeto?** Comece em [docs/00-start-here/](docs/00-start-here/README.md).

[Índice documental](docs/README.md) · [Decisões e motivos](docs/40-decisions/README.md) · [História](docs/99-history/README.md).

## Estado atual

A baseline candidata está na **PR #32 — Convergir Nexus Windows: execução direta, binding e gates nativos**; a **PR #45** é integração posterior em Draft, sem merge, release ou PASS global. A issue #33 fixa a direção de convergência: unificar o produto sem acrescentar novas funcionalidades por antecipação.

A [matriz de compatibilidade com o código de 10/10](docs/10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) descreve a PR #45 por ficheiro e SHA. O [ponto de situação técnico](nexus/docs/PONTO-DE-SITUACAO.md) reúne relatórios de vários ciclos, incluindo a abertura de 08/10; não deve ser confundido com aceitação da integração posterior.

PASS histórico não significa release. Um gate atual em FAIL continua FAIL até prova reproduzível.

## O produto em uma linha

**Folha + parser determinístico + Kernel/Host/Store + regras/schemas + execução direta protegida ou MCP delimitado + ferramentas externas + Creative/Human Gate/Canonical.**

```text
Humano
  ↓
Folha / parser
  ↓
Kernel / Host / Store
  ↓
regras + schemas + allowlists
  ↓
Runner direto protegido ou MCP Python autorizado
  ↓
ferramenta externa delimitada
  ↓
resultado + trace + proveniência
  ↓
Creative
  ↓
Human Gate
  ↓
Canonical
```

## O Nexus não é

- um orquestrador autónomo de agentes;
- uma camada onde um LLM manda no computador;
- um wrapper de Activepieces;
- um produto dependente de Conductor;
- um sistema em que memória ou modelo têm autoridade.

IA pode existir dentro de uma capability delimitada. Não decide autoridade, promoção para Canonical, política global ou recovery.

## Núcleo mínimo

A hipótese candidata é que **Kernel + parser + regras + runner direto protegido**, com **MCP Python apenas quando necessário**, chegam para o produto mínimo. Na PR #45, o despacho interno tem dez processos definidos, mas a API pública da Folha encaminha naturalmente apenas `verify` com confirmação: ver [compatibilidade](docs/10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md).

Activepieces fica como referência de estudo.

Conductor foi estudado e não é dependência candidata.

SpiffWorkflow fica apenas como hipótese de laboratório para processos determinísticos realmente complexos; só entra se um fluxo real demonstrar que branches/joins/multi-instance/waits seriam piores de manter diretamente. Ver [estudo Spiff/Conductor/MCP](docs/90-research/SPIFF-CONDUCTOR-MCP.md).

## Mapa do repositório

| Caminho | Função |
|---|---|
| [docs/00-start-here/](docs/00-start-here/README.md) | Entrada para leitores externos |
| [docs/10-current/](docs/10-current/README.md) | Navegação do estado atual |
| [docs/20-architecture/](docs/20-architecture/MINIMUM-CORE.md) | Arquitetura mínima da implementação |
| [docs/30-help/](docs/30-help/README.md) | Onde e como ajudar |
| [docs/90-research/](docs/90-research/SPIFF-CONDUCTOR-MCP.md) | Estudos comparativos, sem autoridade sobre o runtime |
| [docs/99-history/](docs/99-history/README.md) | Como ler genealogia e experiências antigas |
| [nexus/](nexus/README.md) | Código do protótipo Windows candidato |
| [nexus/docs/](nexus/docs/) | Contratos, relatórios e evidência técnica |
| [auditoria/](auditoria/) | Matrizes e evidência de auditoria |
| [historico/](historico/) | Genealogia; não é runtime atual |
| [implementacao/](implementacao/) | Implementações anteriores/candidatas históricas |

## Garantias que não se negociam

- humano é a autoridade máxima;
- Creative e Canonical permanecem separados;
- promoção para Canonical exige decisão humana;
- IA/provider/ferramenta têm autoridade zero;
- proveniência e hashes são verificados;
- crash ambíguo não autoriza repetição silenciosa de side effects;
- eliminação automática só para duplicação absolutamente exata;
- Windows confinement não é enfraquecido para obter PASS;
- nenhuma dependência entra sem lacuna real demonstrada.

## Ajudar

As contribuições externas devem começar por [docs/30-help/README.md](docs/30-help/README.md) e pelas issues #35–#39.

Preferimos reprodução independente, testes adversariais, diagnóstico e patches pequenos. Não redesenhar a arquitetura M1–M14 nem trabalhar por cima do runtime principal para experimentar uma hipótese.

## Regra de engenharia

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

**Se um componente não pode ser retirado sem destruir o resto, está mal integrado.**

## Licença

Código e documentação próprios: PolyForm Noncommercial 1.0.0. Dependências mantêm as suas licenças. Consulte [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) e [CONTRIBUTING.md](CONTRIBUTING.md).
