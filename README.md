# Cérebro Independente / Nexus

Sistema local-first de criação, conhecimento e execução governada para uma pessoa. A pessoa usa linguagem natural; o sistema compõe processos e ferramentas nos bastidores; a pessoa continua autoridade final.

## Código desta versão

O protótipo Windows está em [nexus/](nexus/README.md). Consultar o [estado testado e pendências](nexus/docs/PUBLICACAO-2026-10-01.md). As pastas `implementacao/` e `historico/` conservam versões anteriores; não são necessárias para executar Nexus.

## Estado atual em uma frase

**Nexus Minimal = Folha em linguagem natural + Conductor como condutor candidato + memória soberana Nexus/Windows + Open Notebook apenas como bancada cognitiva descartável.**

A arquitetura conceptual está estável. A implementação física continua sujeita a testes: nenhuma integração é declarada resolvida antes de PASS real.

## Modelo mental

Nexus é um **launcher metódico, com memória, leis e templates executáveis**, que usa as ferramentas disponíveis para atingir um fim. Não tenta reprogramar capacidades maduras.

```text
Humano
  ↕
Folha Nexus (linguagem natural)
  ↓
Conductor / runtime de workflows
  ├─ processo/template conhecido → capability/ferramenta
  └─ problema novo/ambíguo → Open Notebook + tiny local (bancada)
                               ↓
                            resultado
  ↓
verificar / PASS | FAIL | UNKNOWN
  ↓
Creative → Human Gate → Canonical
  ↓
experiência validada → processo/template candidato
```

## Separação de responsabilidades

As responsabilidades M1–M14 continuam aplicáveis. Os contratos, testes e a evidência datada da implementação estão em `nexus/docs/`.

### Folha Nexus
Interface inicial mínima. Texto natural, anexos, resultados e decisões humanas. YAML, JSON, Markdown, IDs e infraestrutura ficam escondidos na utilização normal.

### Conductor
Condutor/runtime candidato para routing, workflows, scripts, MCP, paralelismo e gates. Não é proprietário do conhecimento. Só entra definitivamente depois de provar o percurso local exigido pelo Nexus.

### Open Notebook
**Bancada de trabalho, ponto.** Não é memória soberana, Canonical, Creative, arquivo, Wiki, autoridade nem interface principal. Recebe um pacote de trabalho limitado, permite trabalho cognitivo com tiny local e devolve resultado estruturado. Deve poder ser destruído/substituído sem perda de conhecimento Nexus.

### Nexus / Windows
É dono da memória e da continuidade: Raw/entrada, Creative, Canonical, arquivo, proveniência, eventos, regras, processos/templates, schemas e histórico. Formatos preferidos: Markdown + JSON + YAML + fontes originais/hashes; SQLite/FTS5 pode ser usado como índice/estado quando justificar, sem tornar a memória dependente de uma aplicação externa.

### Capabilities
LibreOffice, Zotero, LanguageTool, web, imagem, áudio, Whisper/TTS e outras ferramentas entram apenas quando um processo precisa delas. `LIGAR > CONFIGURAR > ADAPTAR > CRIAR` continua a regra.

## O que é nosso

- autoridade humana invariável;
- Creative e Canonical separados;
- promoção para Canonical apenas por Human Gate;
- IA/provider com autoridade zero;
- PASS / FAIL / UNKNOWN;
- proveniência direta e inversa;
- contradições preservadas;
- eliminação automática apenas para duplicação absolutamente exata;
- agentes como microprocessos reconstruíveis: tiny + prompt + contexto + regras + ferramentas permitidas + schema + objetivo;
- experiência validada pode tornar-se processo/template reutilizável;
- ferramentas e bancadas substituíveis;
- desmontar deve ser tão fácil como montar.

## Templates executáveis

Uma tarefa conhecida deve poder ser representada por um pequeno contrato reutilizável:

```text
process.yaml
input.schema.json
output.schema.json
prompts/
rules.yaml
tests/
```

Se o processo é conhecido, executa-se com o mínimo de IA. Se não é conhecido, a bancada ajuda a descobrir/decompor; o resultado só se torna template reutilizável depois de testes e aprovação humana.

## Prova mínima

1. linguagem natural na Folha;
2. routing pelo condutor;
3. tarefa cognitiva enviada à bancada Open Notebook/tiny;
4. resultado JSON válido;
5. gravação em Creative;
6. tentativa de escrita direta em Canonical bloqueada;
7. Human Gate permite promoção explícita;
8. destruir/reconstruir bancada sem perder memória Nexus;
9. recuperar proveniência do resultado até ao pedido/fontes;
10. repetir tarefa semelhante e medir reutilização do processo.

Só depois destes PASS entram capabilities adicionais.

## Benchmark externo único

Para evitar dispersão, o projeto externo de comparação escolhido em 30-09-2026 é **Negentropy-Laby/OpenDoge**. Não é dependência do Nexus nem modelo a copiar. Serve apenas para aprender e falsificar decisões: local-first/single-operator, workflow templates, contracts, approvals, evidence/replay e slots/capabilities substituíveis. O Nexus mantém a sua redução própria: Folha única, memória soberana exterior à IA, Open Notebook apenas como bancada descartável e aprendizagem processual sem crescimento de autoridade.

## Regra permanente

- **LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**
- **NENHUM COMPONENTE ENTRA SEM UM FAIL QUE O JUSTIFIQUE.**
- **SE NÃO PODE SER DESLIGADO SEM DESTRUIR O RESTO, ESTÁ MAL INTEGRADO.**
- **MEMÓRIA NÃO É AUTORIDADE.**
- **IA NÃO É AUTORIDADE.**
- **PROMOTE_TO_CANONICAL só acontece após decisão humana.**
- **Similaridade nunca autoriza eliminação; apenas duplicação exata.**

## Licença do projeto

Código/documentação próprios: PolyForm Noncommercial 1.0.0. Dependências mantêm as suas próprias licenças; antes de redistribuição devem ser fixadas versões e `THIRD_PARTY_NOTICES`.

[Constituição](CEREBRO_CONSTITUTION.md) · [Arquitetura](CEREBRO_ARCHITECTURE.md) · [Decisões](DECISIONS.md) · [Estado](STATUS.md) · [Plano](IMPLEMENTATION_PLAN.md) · [Pendências](docs/PENDENCIAS.md)
