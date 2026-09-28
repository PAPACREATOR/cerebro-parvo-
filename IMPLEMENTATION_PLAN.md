# Plano de execução vigente — composição antes de código

Objetivo: provar o produto ligando capacidades maduras, com o mínimo possível de código próprio.

## Princípio

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Nada é programado de raiz enquanto Activepieces, uma Piece, MCP, API, CLI, Open Notebook, K-DLC, Zotero, LibreOffice, Pinokio ou outro provider maduro conseguir produzir o comportamento exigido.

O humano continua autoridade máxima em todos os casos.

## Fase 1 — vertical slice mínima

Construir primeiro apenas:

`Activepieces WebUI -> regras/tabelas -> capacidade -> resultado -> Creative -> Human Gate -> Canonical`

Critérios:

- uma única interface para a pessoa;
- nenhuma IA ou provider externo promove Canonical;
- estado e regras sobrevivem ao flow;
- resultado externo é tratado como UNTRUSTED quando aplicável;
- decisão humana explícita fecha ações protegidas;
- sem Python/SQLite próprios salvo lacuna demonstrada.

## Fase 2 — três memórias

Implementar como funções, não como três sistemas:

- Working Memory -> estado do flow + Tables/Storage;
- Behavioral/Procedural Memory -> Tables versionadas;
- Persistent Knowledge -> Creative/Canonical em formatos abertos, com provider de governação quando útil.

## Fase 3 — três comparadores

Composição independente:

- determinístico -> condições, hashes, estados, valores, regras;
- relacional -> relações, backlinks, fontes, versões, genealogia, índices;
- semântico -> Open Notebook/tiny ou outro provider.

O flow cruza os resultados. Nenhum comparador decide autoridade.

## Fase 4 — capacidades

Adicionar apenas quando necessárias:

- SEMANTIC_WORK -> Open Notebook;
- KNOWLEDGE_GOVERNANCE -> K-DLC se compatível;
- REFERENCES -> Zotero;
- DOCUMENT_OUTPUT -> LibreOffice;
- IMAGE -> Pinokio/provider local;
- AUDIO_MUSIC -> Pinokio/provider local;
- PUBLISH -> Piece/provider aplicável.

Cada capacidade fica escondida atrás da mesma experiência Activepieces.

## Fase 5 — prova de robustez

Só depois da vertical slice funcional:

- restart/recovery;
- pesquisa/indexação;
- backup/restore;
- Windows;
- E2E;
- UX para utilizador não técnico;
- troca de provider sem alterar as leis.

## Código já existente

A implementação Python e o writer recuperável permanecem preservados como evidência/fallback. Não são caminho obrigatório do MVP.

Entram apenas se a composição real demonstrar uma lacuna que não possa ser resolvida por configuração/provider maduro.

## Regra permanente

- pessoa manda;
- IA não aprova;
- Activepieces orquestra tecnicamente;
- regras/estado impõem autoridade;
- Pieces fazem o trabalho;
- Open Notebook pensa quando necessário;
- Creative recebe propostas;
- Human Gate decide promoção;
- Canonical guarda o aprovado;
- não criar componentes por antecipação.

[Arquitetura vigente](CEREBRO_ARCHITECTURE.md) · [Pendências](docs/PENDENCIAS.md)
