# Reconciliação documental — 10 de outubro de 2026

**Natureza:** fotografia datada dos refs consultados; não é certificação física do PC, nem substitui [o ponto de situação operacional](../../nexus/docs/PONTO-DE-SITUACAO.md).

## Retrato comprovável no GitHub

- **main:** árvore Git aeeb6f662a8282b3793708aa3e6782ef20d2d0ca; 177 ficheiros segundo o inventário da PR #46. Não representa automaticamente todo o PC.
- **PR #32:** baseline do runtime Windows, HEAD da referência consultada da86b6dd181d00fd7a87addaa01a12ec3a14e57b; oito workflows SUCCESS e um FAIL Writer Windows no mesmo SHA, segundo a PR. Não há PASS global.
- **PR #43:** Work, Front Door/verify natural e confirmação humana antes da execução; branch Draft distinta. Um contrato de verify não representa as sete intenções ligadas a todas as operações.
- **PR #45:** integração candidata isolada, HEAD 66027af7f2ea084bc62d85b840d1fc3113e60a97 no exame. Integra experimentalmente a PR #43 só nessa branch; registou FAIL-first de 79 casos e correção até gates parciais PASS. Continua Draft, não release nem merge.
- **PR #44:** negativos do OpenNotebook com peer de teste, não prova da stack real.
- **PR #47:** laboratório Wiki/Flow com regressões de tipos malformados; sem promoção à candidata.
- **PR #41:** navegação/documentação; base desta revisão e não integrada em main no exame.
- **PR #46:** inventário, auditoria de links, divergências documentais e privacidade; incompleto e isolado em auditoria/.
- **PR #48:** clones e inventário Linux; não é espelho validado dos ficheiros físicos do PC, nem limpeza local Windows.

Links e estatutos pontuais: [matriz de evidência](../60-evidence/MATRIZ-PRS-2026-10-10.md).

## Política vigente a descrever

A entrada é Folha/parser; Kernel/Host/Store mantêm as decisões e os limites; MCP ou adaptador direto transportam apenas operações autorizadas. Ferramentas são substituíveis. Confirmação humana **pré-execução** não é o mesmo que Human Gate de promoção **Creative → Canonical**.

Activepieces e Conductor não integram a dependência candidata; Spiff só laboratório perante necessidade demonstrada. OpenNotebook é ferramenta especializada valorizada, **não percurso obrigatório** nem executor soberano. Ollama não é requisito. Sandy permanece suspenso por decisão humana, sem apagar o reconhecimento histórico.

## Estado de aceitação

**Não comprovado**: release integrada num único HEAD com todos os gates PASS; Writer/LPAC real completo; OpenNotebook com SurrealDB/modelo locais reais em E2E; inventário/hash SHA-256 de todo o PC; validação física de todas as capacidades; proteção integral de segredos/histórico Git; ligações externas/âncoras de toda a documentação. Não interpretar NOT RUN/BLOCKED/FAIL como PASS.

## Regras de atualização

Antes de alterar este retrato: recolher PR/commit, ambiente, data, operação e evidência. Distinguir plano, teste com fixture, CI Windows, teste físico e aceitação humana. Para operações atuais, prevalece o HEAD exato verificado, não esta fotografia datada.