# Constituição — orientação vigente

> **Nota de vigência (2026-10-10):** As menções abaixo a Activepieces como executor ou componente por defeito documentam uma proposta anterior. A decisão posterior de 30-09-2026 em [DECISIONS.md](DECISIONS.md) e [STATUS.md](STATUS.md) retira Activepieces do núcleo obrigatório; o Conductor é candidato sujeito a testes. Preservamos o texto histórico para auditoria. Nenhuma ferramenta passa a ter autoridade sobre o Kernel ou o Human Gate.


Baseline conceptual preservada; implementação operacional fechada em 28-09-2026 por composição mínima.

## Precedência

1. decisão humana explícita posterior, com data e âmbito;
2. esta Constituição e as invariantes M1–M14;
3. contratos de comportamento/teste aplicáveis;
4. flows, tabelas, providers e integrações concretas;
5. documentos históricos, que explicam o percurso mas não substituem decisões posteriores.

Nenhum agente, workflow, plugin, modelo ou provider resolve por si só uma divergência normativa.

## Invariantes

- pessoa como autoridade final;
- uma interface simples em linguagem natural;
- três memórias: trabalho, comportamental/procedimental e conhecimento persistente;
- dois domínios de autoridade: Creative e Canonical;
- três comparadores: determinístico, semântico e relacional;
- M1–M14 como responsabilidades, não como obrigação de criar serviços ou módulos;
- proveniência, genealogia e contradições preservadas;
- regras versionadas e explicáveis;
- instrução humana atual prevalece sobre comportamento aprendido;
- IA e providers externos nunca aprovam conhecimento nem aumentam permissões;
- promoção para Canonical exige o Human Gate aplicável;
- similaridade, paráfrase ou concordância semântica nunca autorizam eliminação;
- replay/recuperação não volta a chamar IA/Web/provider para inventar evidência histórica;
- backup só é considerado válido após restauro demonstrado.

## Implementação operacional

O Cérebro é definido pelas leis acima, não por uma tecnologia específica.

Por defeito:

- Activepieces fornece WebUI/Chat UI, flows, Subflows, Tables, Storage, MCP, triggers, routing, waits e integrações;
- as regras e o estado constitucional são expressos por configuração, tabelas e flows sempre que isso for suficiente;
- capacidades externas são providers substituíveis chamados por Piece/MCP/API/CLI;
- Open Notebook é uma bancada cognitiva/semântica, não memória autoritativa;
- uma única tiny/modelo pode mudar de papel por parâmetros, contexto e permissões;
- K-DLC pode ser usado como provider de governação de conhecimento quando compatível, mas não substitui esta Constituição;
- Zotero, LibreOffice, Pinokio/ComfyUI e outros programas fazem trabalho especializado nos bastidores;
- Python, SQLite, bases vetoriais, serviços próprios ou adaptadores próprios só entram perante lacuna real demonstrada por teste.

## Regra de engenharia

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Não se adiciona serviço, base de dados, agente, biblioteca, frontend ou aplicação enquanto uma combinação de flow + tabela + provider maduro produzir o comportamento exigido.

A simplificação pode trocar mecanismos; não pode retirar capacidades ou autoridade humana.

## Experiência do utilizador

O utilizador vê apenas a experiência principal e linguagem normal.

Fluxos, tabelas, Markdown, IDs, APIs, MCP, índices, providers e aplicações especializadas ficam ocultos por defeito.

Modelo:

```
Pessoa
-> Activepieces WebUI
-> regras + estado + flow
-> provider necessário
-> resultado
-> Creative
-> Human Gate
-> Canonical / ação autorizada
```

[Arquitetura vigente](CEREBRO_ARCHITECTURE.md) · [Decisões](DECISIONS.md) · [Estado](STATUS.md).
