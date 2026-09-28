# Cérebro Independente

Sistema local-first de criação, conhecimento e execução governada. A pessoa escreve em linguagem normal numa única interface; regras e flows escolhem capacidades maduras; as ferramentas trabalham nos bastidores; a pessoa continua autoridade final.

## Arquitetura em uma frase

**Uma interface, poucas regras e tabelas, flows simples e providers substituíveis.**

O projeto não pretende reconstruir editores, motores de workflow, sistemas de pesquisa, geradores multimédia ou gestores bibliográficos. Liga ferramentas maduras e obriga-as a respeitar as mesmas leis humanas.

## O que fica nosso

- 3 memórias: trabalho, comportamental/procedimental e conhecimento persistente;
- 2 domínios de autoridade: Creative e Canonical;
- 3 comparadores: determinístico, semântico e relacional;
- Human Gate;
- M1–M14 como responsabilidades;
- proveniência, genealogia, contradições e recuperação;
- regras pessoais versionadas;
- IA sempre sem autoridade.

## Implementação preferencial

```
Pessoa
  -> Activepieces WebUI / Chat UI
  -> regras + Tables/Storage + flows
  -> capacidade necessária
       -> Open Notebook
       -> K-DLC ou outro knowledge-governance provider
       -> Zotero
       -> LibreOffice
       -> Pinokio / ComfyUI / outros providers locais
       -> outras Pieces / MCP / API / CLI
  -> resultado
  -> Creative
  -> Human Gate
  -> Canonical / ação autorizada
```

O utilizador não deve precisar de abrir as aplicações internas nem conhecer Markdown, IDs, SQL, MCP ou APIs.

## Regra permanente

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Python, SQLite, bases vetoriais, serviços próprios e adaptadores próprios deixam de ser pressupostos do MVP. Só entram se um teste real provar que um provider existente não consegue cumprir uma regra essencial.

## Compatibilidade verificada

- Activepieces: Chat UI/Human Input, Flows, Subflows, Tables, Storage, MCP e centenas de integrações;
- Open Notebook: REST API para notebooks, fontes, pesquisa, chat e operações cognitivas;
- Zotero: API local no desktop, incluindo leitura e escritas autorizadas;
- LibreOffice: execução headless/CLI e controlo por API;
- Pinokio: instalação e execução local de aplicações/servidores AI;
- ComfyUI: backend/API local para workflows de imagem e multimédia;
- K-DLC: forte compatibilidade conceptual para governação de conhecimento, mas ainda tratado como provider opcional porque a especificação atual continua draft.

Ver [Matriz de compatibilidade](COMPATIBILITY-MATRIX.md).

## Estado real

A arquitetura está fechada. O produto completo ainda não está provado ponta-a-ponta.

O repositório preserva a implementação Python e o writer recuperável já testados como evidência técnica/fallback, mas eles deixaram de ser caminho obrigatório.

O próximo teste é uma única vertical slice, preferencialmente sem código próprio:

`WebUI -> regras/tabelas -> provider -> Creative -> Human Gate -> Canonical`.

## Documentação vigente

1. [Constituição](CEREBRO_CONSTITUTION.md)
2. [Arquitetura vigente](CEREBRO_ARCHITECTURE.md)
3. [Decisões](DECISIONS.md)
4. [Estado](STATUS.md)
5. [Plano de implementação](IMPLEMENTATION_PLAN.md)
6. [Matriz de compatibilidade](COMPATIBILITY-MATRIX.md)
7. [Pendências](docs/PENDENCIAS.md)

Documentos anteriores permanecem no histórico para genealogia, não como orientação operacional atual.

## Licença

O repositório usa [PolyForm Noncommercial 1.0.0](LICENSE). Uso comercial do código/documentação próprios exige licença ou permissão separada do titular. Licenças dos providers e componentes de terceiros continuam independentes.

[CONTRIBUTING](CONTRIBUTING.md) · [CLA](CONTRIBUTOR_LICENSE_AGREEMENT.md) · [Licenciamento comercial](COMMERCIAL-LICENSING.md) · [Segurança](SECURITY.md) · [Terceiros](THIRD_PARTY_NOTICES.md)
