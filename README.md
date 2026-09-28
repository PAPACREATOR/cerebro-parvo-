# Cérebro Independente

Sistema local-first de criação, conhecimento e execução governada para uma pessoa. A pessoa usa linguagem normal; o sistema coordena processos e memória nos bastidores; a pessoa continua autoridade final.

## Estado atual em uma frase

**Núcleo candidato: Humano + Activepieces Community + um Memory Provider local SQLite/MCP.**

A arquitetura conceptual está estável, mas a implementação física **não está fechada** até o Memory Provider passar testes reais.

## O que é nosso

- 3 memórias lógicas: Working, Behavioral/Procedural e Persistent Knowledge;
- 2 domínios de autoridade: Creative e Canonical;
- 3 comparadores: determinístico/exato, semântico e relacional;
- Human Gate;
- M1–M14 como responsabilidades;
- proveniência, genealogia, contradições e recuperação;
- regras versionadas e explicáveis;
- IA/provider sem autoridade;
- provider substituível;
- desmontar deve ser tão fácil como montar.

## Núcleo candidato

```
                         HUMANO
                      autoridade final
                            |
                            v
                     ACTIVEPIECES
                processos / regras / gates
                            |
                            | MCP
                            v
                  MEMORY PROVIDER LOCAL
                    SQLite + FTS5
                 + semântico opcional
                 + relações/proveniência
```

### Bloco 1 — Activepieces Community

Função: execução determinística, flows/subflows, estado de processo, Human Gate, integração MCP/HTTP e receitas.

Licença: **core MIT**. Funcionalidades Enterprise ficam fora do núcleo salvo licença própria.

### Bloco 2 — Memory Provider SQLite/MCP

Função: conhecimento persistente, pesquisa, relações, temporalidade, proveniência e histórico.

Candidatos a testar, sem decisão antecipada:

1. **RMANOV/sqlite-memory-mcp** — candidato A: SQLite/WAL, FTS5, semântica opcional, knowledge graph, proveniência, eventos e promoção approval-aware. MIT.
2. **Beledarian/mcp-local-memory** — candidato B: SQLite, FTS5, sqlite-vec, pesquisa temporal, entidades/relações e lifecycle auditável. MIT.

SQLite é parte interna desta camada; não precisa de ser um terceiro serviço.

### PiecesOS

PiecesOS deixa de ser dependência nuclear. Mantém-se como:
- benchmark funcional;
- opção experimental para protótipo;
- referência para LTM/FTS/vector/temporal/MCP.

É proprietário e não temos prova de direito de redistribuição perpétua. A geração 12.3.8/12.3.9 continua útil para comparação, mas o projeto deve funcionar sem ela.

## Regra permanente

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

E ainda:

- **NENHUM COMPONENTE ENTRA SEM UM FAIL QUE O JUSTIFIQUE.**
- **SE NÃO PODE SER DESLIGADO SEM DESTRUIR O RESTO, ESTÁ MAL INTEGRADO.**
- **ACTIVEPIECES É MOTOR, NÃO PROPRIETÁRIO DO CONHECIMENTO.**
- **MEMÓRIA NÃO É AUTORIDADE.**
- **PROMOTE_TO_CANONICAL só acontece após decisão humana.**

## Providers periféricos

LibreOffice, Zotero, ComfyUI, LanguageTool, IA local, web, email e publicação não pertencem ao núcleo. Entram por receita apenas quando necessários.

Open Notebook e K-DLC deixam de ser dependências runtime. Permanecem como referências históricas/fontes de requisitos e só regressam se um teste demonstrar uma lacuna concreta.

## Próxima prova

Testar os dois Memory Providers contra o mesmo contrato:

```
Activepieces
 -> MCP
 -> criar memória
 -> FTS
 -> semântico
 -> temporal
 -> relações/proveniência
 -> contradição sem auto-delete
 -> Creative
 -> Human Gate
 -> Canonical
 -> restart
 -> backup/restore
 -> desligar provider
 -> núcleo continua íntegro
```

Só depois deste teste se escolhe o provider.

## Licença do projeto

O código/documentação próprios do repositório usam PolyForm Noncommercial 1.0.0. Dependências mantêm as suas licenças: Activepieces core MIT; os dois candidatos atuais de memória MIT; SQLite public domain; PiecesOS proprietário.

[Constituição](CEREBRO_CONSTITUTION.md) · [Arquitetura](CEREBRO_ARCHITECTURE.md) · [Decisões](DECISIONS.md) · [Estado](STATUS.md) · [Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md)
