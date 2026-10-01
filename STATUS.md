## Inventário e organização — 01-10-2026

[Mapa de pastas, instalações confirmadas e plano por fases](nexus/docs/ORGANIZACAO-E-FASES.md). Publisher presente; Gmail/Facebook, imagens e música ainda sem integração. Conta Windows e restauro continuam pendentes.

## LanguageTool integrado — 01-10-2026

Revisão local por CLI ligada ao Conductor e Creative: ensaio real PASS; original intacto, IA zero, bypass BLOCK. Regressão: **94 testes passaram**. [Contrato e limites](nexus/docs/F006-LANGUAGETOOL.md).

# Atualização — 01-10-2026

Código Nexus publicado em [nexus/](nexus/README.md). [Revisão desta versão](nexus/docs/PUBLICACAO-2026-10-01.md): 83 testes passaram em Windows; integração completa e isolamento por conta continuam pendentes. As responsabilidades M1–M14 não são declaradas concluídas.

O retrato abaixo conserva o estado anterior.

---

# Estado operacional — 30-09-2026

## Estado

**ARQUITETURA CONCEPTUAL REDUZIDA AO NEXUS MINIMAL; IMPLEMENTAÇÃO E2E AINDA NÃO PROVADA.**

Não declarar o sistema funcional até o circuito mínimo passar em máquina real.

## Núcleo atual

```text
Humano
  ↕
Folha Nexus — linguagem natural
  ↓
Conductor — condutor/runtime candidato
  ├─ Windows / capabilities / web
  └─ Open Notebook — bancada cognitiva descartável
                       └─ tiny local
  ↓
resultado estruturado
  ↓
Nexus/Windows — memória soberana
Raw / Creative / Canonical / arquivo / proveniência / eventos / templates
```

## Princípio de redução

Nexus não tenta ser um superagente. É um launcher organizado e metódico que:
- recebe intenção humana;
- procura processo/template conhecido;
- compõe as ferramentas disponíveis;
- usa cognição apenas quando regras/processos não chegam;
- verifica o resultado;
- preserva experiência e proveniência;
- mantém a autoridade no humano.

## O que está preservado

- Folha Única em linguagem natural;
- Creative/Canonical;
- Human Gate;
- IA sem autoridade;
- PASS/FAIL/UNKNOWN;
- proveniência direta ↔ inversa;
- contradições preservadas;
- eliminação automática só de duplicação absolutamente exata;
- agentes em microprocessos reconstruíveis;
- templates/processos reutilizáveis;
- capabilities substituíveis;
- memória independente da bancada/modelo;
- possibilidade de reduzir uso de IA à medida que processos estabilizam.

## O que saiu do Core

- Activepieces como requisito nuclear;
- Memory Provider externo obrigatório;
- PiecesOS obrigatório;
- K-DLC runtime;
- vector DB separado;
- framework multi-agent permanente;
- RAG próprio;
- ELIZA obrigatória;
- LibreOffice/Zotero/LanguageTool/imagem/áudio como dependências de boot.

Estas ferramentas podem regressar apenas como capabilities ou alternativas perante necessidade/teste.

## Open Notebook

Regra atual: **bancada de trabalho, ponto.** Pode receber contexto/fontes/prompts/schemas para uma tarefa e devolver resultado. Não possui a memória soberana. Deve ser possível apagar/substituir a bancada e continuar a partir da memória Nexus.

## Benchmark externo

Nesta fase comparar com **um único projeto: Negentropy-Laby/OpenDoge**. Razão: oferece material concreto sobre local-first single-operator, workflow templates, contracts, approvals, evidence/replay e slots/capabilities. Não copiar a sua dimensão/complexidade; extrair apenas padrões que reduzam engenharia e respeitem as leis Nexus.

## Próximo portão — Nexus Minimal E2E

1. abrir Folha;
2. escrever pedido em linguagem natural;
3. routing pelo condutor;
4. enviar tarefa cognitiva limitada à bancada;
5. tiny local devolve JSON conforme schema;
6. guardar resultado em Creative;
7. mostrar resultado na Folha;
8. bloquear escrita direta em Canonical;
9. Human Gate explícito promove quando autorizado;
10. reconstruir bancada sem perda de memória;
11. demonstrar proveniência inversa;
12. repetir tarefa semelhante e medir reutilização do processo.

Resultado permitido: PASS, FAIL ou UNKNOWN. Sem PASS real não avançar para o catálogo grande de capabilities.

## Evidência histórica preservada

No commit `f48382f396e3b4af18e62a15c3ecb6104dfd52c9`:
- GitHub Actions SUCCESS;
- 34 testes históricos PASS;
- 11 writer tests PASS;
- total 45 PASS.

Isto continua a ser evidência histórica e não prova o Nexus Minimal E2E.

## Regra operacional

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**
