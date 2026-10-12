# Nexus / Cérebro Independente

**Nexus é um estúdio pessoal local-first para escrever, investigar, organizar conhecimento e executar tarefas no teu computador — mantendo a tua memória, fontes e autoridade.**

Escreves em linguagem natural. O sistema organiza o trabalho, usa ferramentas locais quando são necessárias e mostra o resultado para revisão. A IA pode ajudar, mas não decide sozinha nem substitui a tua aprovação.

## Para quem é

Nexus é pensado para escritores, investigadores, estudantes e criadores que querem trabalhar com documentos, notas, fontes e tarefas repetitivas sem perder privacidade nem controlo.

A ideia é simples: em vez de espalhar trabalho por chats, ficheiros, notas e ferramentas separadas, tens uma Folha em linguagem natural, memória persistente e processos reutilizáveis.

## O que já está provado

Esta é a realidade observada no repositório, não uma promessa de produto final:

- protótipo Windows com Folha, Kernel/Host/Store Python e fronteira nativa de execução;
- comandos naturais registados com ticket de uso único, aprovação humana antes da execução e aprovação do resultado;
- verificação de texto/anexo por hash;
- revisão de português opcional com LanguageTool;
- conversão de ODT para PDF com LibreOffice;
- bancada cognitiva opcional com OpenNotebook;
- memória, proveniência, recuperação e separação entre rascunho e conhecimento aprovado.

A PR [#61](https://github.com/PAPACREATOR/cerebro-parvo-/pull/61) foi integrada em `main` no commit `89e8b7e4a54ce6bb10ee97e0285d3ec21e2d8148`. O candidato `2e0f3e8a3babe89b06ca38263d94e2f4d74bf569` teve 10 workflows, 21 jobs e 22 checks verdes; após o merge, 3 workflows, 5 jobs e 5 checks passaram no SHA de merge.

## O que ainda não está provado

Nexus é um protótipo, não uma release pronta para produção:

- não há aceitação completa no PC pessoal;
- Writer editorial completo, Zotero, pesquisa web verificada, música, vídeo e avatar continuam pendentes ou exigem prova própria;
- a instalação/provisioning protegido de ferramentas externas não está concluído;
- um PASS de CI não equivale a release, backup válido ou funcionamento garantido no teu computador.

Consultar sempre o [estado operacional](nexus/docs/PONTO-DE-SITUACAO.md) antes de usar, instalar ou contribuir.

## Como funciona

```text
Pessoa
  ↓
Folha em linguagem natural
  ↓
Kernel / Host / Store Python
  ↓
MCP determinístico e adaptadores delimitados
  ↓
Ferramentas externas opcionais
  ↓
Resultado candidato
  ↓
Creative
  ↓
Aprovação humana
  ↓
Canonical
```

A pessoa escreve na Folha. O Kernel/Host/Store mantém estado, regras, proveniência e recuperação. O MCP transporta chamadas delimitadas; ferramentas externas executam capacidades específicas e devolvem resultados não confiáveis até validação.

Nada é promovido para Canonical sem decisão humana aplicável. A IA e as ferramentas não ganham autoridade por estarem integradas.

## Princípios

- A pessoa é a autoridade final.
- Privacidade e execução local primeiro.
- Memória e fontes pertencem ao utilizador, não a um chat.
- Proveniência: cada resultado pode ser seguido até ao pedido, processo e fontes.
- Rascunho e conhecimento aprovado são separados.
- Similaridade nunca autoriza eliminação; apenas duplicação exata.
- Ferramentas devem poder ser desligadas ou substituídas sem destruir a memória.
- `LIGAR > CONFIGURAR > ADAPTAR > CRIAR`.

## Começar

O protótipo Windows está em [`nexus/`](nexus/README.md). Antes de executar, consulta o [estado operacional](nexus/docs/PONTO-DE-SITUACAO.md), o guia de [arranque](nexus/README.md) e os requisitos do teu sistema.

Para contribuir, começa por [`CONTRIBUTING.md`](CONTRIBUTING.md) e pela [documentação interna](docs/README.md).

## Documentação

- [Estado operacional](nexus/docs/PONTO-DE-SITUACAO.md) — SHAs, provas, falhas e pendências.
- [Arranque e runtime](nexus/README.md) — instalação, comandos e limites.
- [Constituição](docs/architecture/CEREBRO_CONSTITUTION.md) — invariantes e autoridade.
- [Arquitetura](docs/architecture/CEREBRO_ARCHITECTURE.md) — composição e desacoplamento.
- [Decisões e genealogia](docs/architecture/DECISIONS.md) — evolução datada do projeto.
- [Documentação interna](docs/README.md) — mapa para colaboradores.

## Licença

Código e documentação próprios: [PolyForm Noncommercial 1.0.0](LICENSE). Dependências mantêm as suas licenças; consultar [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) antes de redistribuição.

O projeto pode vir a ter um percurso comercial separado, sem eliminar o caminho comunitário não comercial. Contribuições estão sujeitas ao [CLA](CONTRIBUTOR_LICENSE_AGREEMENT.md).