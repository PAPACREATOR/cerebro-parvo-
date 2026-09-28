# Matriz de compatibilidade — arquitetura final de composição

Data: 28-09-2026.

Esta matriz separa **capacidade disponível no componente** de **integração já provada neste projeto**. “Compatível” não significa “E2E testado”.

| Necessidade do Cérebro | Provider preferencial | Integração | Compatibilidade | Estado no projeto |
| --- | --- | --- | --- | --- |
| Interface única em linguagem natural | Activepieces Human Input / Chat UI | nativo | Alta | NOT RUN |
| Flows, routing e execução | Activepieces | nativo | Alta | NOT RUN |
| Reutilização de processos | Activepieces Subflows | nativo | Alta | NOT RUN |
| Estado estruturado / tabelas | Activepieces Tables | nativo/MCP | Alta | NOT RUN |
| Estado simples chave/valor | Activepieces Storage | nativo/MCP | Alta | NOT RUN |
| Human Gate | Activepieces wait/approval + estado do flow | nativo | Alta, exige teste do contrato Creative→Canonical | NOT RUN |
| Registo de capacidades | Table/configuração Activepieces | nativo | Alta | NOT RUN |
| Working Memory | estado do flow + Tables/Storage | nativo | Alta | NOT RUN |
| Behavioral/Procedural Memory | Tables versionadas + regras | nativo/configuração | Alta | NOT RUN |
| Persistent Knowledge | Creative/Canonical + provider de knowledge governance | formatos abertos/API/MCP | Alta conceptual | NOT RUN |
| Pesquisa determinística | filtros/condições/hash/text search disponível | flow/provider | Alta | NOT RUN |
| Pesquisa relacional | K-DLC ou relações/tabelas/índice compatível | MCP/API | Parcial: provider a validar | NOT RUN |
| Pesquisa semântica / cognição | Open Notebook | REST API | Alta | NOT RUN |
| Agente único adaptável | mesmo modelo + perfil/contexto por tarefa no Open Notebook | REST API | Alta conceptual; isolamento a provar | NOT RUN |
| Fontes e referências | Zotero Desktop | Local API HTTP | Alta | NOT RUN |
| Documentos, folhas e conversões | LibreOffice | headless CLI / UNO API | Alta | NOT RUN |
| Instalar/lançar apps AI locais | Pinokio | launcher/scripts locais | Alta para hosting/arranque; não é autoridade | NOT RUN |
| Geração de imagem local | ComfyUI alojado localmente, opcionalmente via Pinokio | HTTP API | Alta | NOT RUN |
| Áudio/música local | provider local compatível alojado via Pinokio/servidor | API/CLI | Provider ainda por escolher | NOT RUN |
| Publishing/distribuição | Pieces Activepieces aplicáveis | Piece/API | Alta por capacidade; selecionar apenas quando necessário | NOT RUN |
| MCP genérico | Activepieces MCP / MCP Piece | MCP | Alta | NOT RUN |
| Knowledge governance avançada | K-DLC | MCP/CLI quando implementação compatível existir | **Promissor, mas especificação 0.2.0 está Draft for implementation** | NÃO tornar dependência obrigatória |
| SQLite próprio | nenhum por defeito | — | Só fallback | writer existente preservado |
| Core Python próprio | nenhum por defeito | — | Só fallback | implementação existente preservada |

## Fronteiras obrigatórias

Independentemente do provider:

1. a pessoa é a autoridade final;
2. ferramenta/IA não promove Canonical;
3. resultado externo é tratado segundo o nível de confiança aplicável;
4. Creative preserva propostas, alternativas e contradições;
5. Human Gate controla promoção/ações protegidas;
6. instrução humana atual vence memória comportamental;
7. replay/recovery não reinvoca IA/Web para fabricar a história;
8. trocar provider não altera estas leis.

## Compatibilidade prática

### Activepieces

É a peça central porque já fornece WebUI/Chat UI, Flows, Subflows, Tables, Storage, MCP e catálogo de integrações. Portanto evita frontend, workflow engine, registry e base simples próprios.

### Open Notebook

Tem REST API completa e pesquisa full-text/vector, controlo de contexto, fontes e chat. Para esta arquitetura deve ser chamado como capacidade cognitiva; não é cofre autoritativo nem decide permissões.

### Zotero

A API local do desktop funciona em `localhost:23119/api/`, offline e sem rate limits para leitura. Escritas no Zotero 10+ requerem autorização local do utilizador. Isto encaixa naturalmente no Human Gate.

### LibreOffice

Suporta `--headless`, `--convert-to` e controlo programático por API/UNO. Pode operar nos bastidores sem se tornar a interface principal.

### Pinokio + ComfyUI

Pinokio instala/arranca aplicações e servidores locais; ComfyUI expõe API para submeter workflows e recuperar resultados. Pinokio é infraestrutura de conveniência, ComfyUI é um possível provider de geração.

### K-DLC

Tem alinhamento forte com proveniência, drafts/overlay, relações, conflitos, revisão humana, índices derivados e MCP. Contudo a especificação atual declara-se draft. Deve permanecer substituível e só ser adotado por funções que passem os nossos testes.

## Regra

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Se uma linha desta matriz puder ser satisfeita por capacidade madura existente, não criar equivalente próprio.

[Constituição](CEREBRO_CONSTITUTION.md) · [Arquitetura](CEREBRO_ARCHITECTURE.md) · [Plano](IMPLEMENTATION_PLAN.md)
