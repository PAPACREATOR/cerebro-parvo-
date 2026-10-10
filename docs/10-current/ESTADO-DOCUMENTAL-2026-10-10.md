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
- **PR #48:** clones Git integrais em Linux de Nexus e Sir Thaddeus (1.446 ficheiros Sir Thaddeus verificados byte a byte; 1.461 registos por seis árvores Nexus públicas). Cópia/limpeza do PC Windows **NOT RUN**, não é espelho físico.
- **PR #49:** revisão documental, índices históricos e matriz por leitura estática do código da PR #45. Não altera código nem transfere provas de um SHA para outro.
- **Writer Lab PR #1:** diagnóstico Windows LPAC real identificou falha no pipe legado (WinError 5) e PASS no namespace `LOCAL`; protótipo de fonte passou testes estáticos, **sem compilar nem produzir PDF**.
- **Writer Lab PR #2 (10/10):** ensaio A/B isolado com Sandy v0.9994 de Hrvoje Abraham. O primeiro [run 38047795468](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38047795468), SHA `fa8d65c4`, terminou **FAIL** após timeout e limpeza/terminação não demonstrada de A; **B nem chegou a correr**. A nova tentativa [run 38048136938](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38048136938), SHA `40d29078`, estava em curso na consulta. Auditoria/CodeQL do primeiro SHA SUCCESS, mas não substituem PDF real.

Links e estatutos pontuais: [matriz de evidência](../60-evidence/MATRIZ-PRS-2026-10-10.md), [verificação estática do código da PR #45](COMPATIBILIDADE-CODIGO-2026-10-10.md) e [reparação documental dos 11 links históricos](../99-history/RECONCILIACAO-11-REFERENCIAS-2026-10-10.md). Esta última fecha a navegação na árvore documental, **não recupera a memória privada de 24/09**.

## Política vigente a descrever

A entrada é Folha/parser; Kernel/Host/Store mantêm as decisões e os limites. O runner interno é direto e protegido; MCP é transporte opcional para ferramentas quando necessário. O parser reconhece sete intenções, mas a API natural normal só prepara `verify` com um anexo no SHA auditado. Ferramentas são substituíveis. Confirmação humana **pré-execução** não é o mesmo que Human Gate de promoção **Creative → Canonical**.

Activepieces e Conductor não integram a dependência candidata; Spiff só laboratório perante necessidade demonstrada. OpenNotebook é ferramenta especializada valorizada, **não percurso obrigatório** nem executor soberano. Ollama não é requisito. **A integração Sandy no produto permanece suspensa.** Distintamente, foi autorizado um ensaio isolado Writer/Sandy no laboratório PR #2; isso não altera a arquitetura candidata nem autoriza instalar/mesclar Sandy. Ver [prova por SHA](../60-evidence/CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md).

## Estado de aceitação

**Observação do código da PR #45:** o dispatcher define dez processos, mas a Folha pública só constrói a rota natural `verify` com anexo e ticket de confirmação; `/api/run` é diagnóstico desativado no arranque normal. Ver [matriz técnica](COMPATIBILIDADE-CODIGO-2026-10-10.md).

**Não comprovado**: release integrada num único HEAD com todos os gates PASS; Writer/LPAC real completo (mesmo com diagnóstico da causa e ensaio A/B em curso); OpenNotebook com SurrealDB/modelo locais reais em E2E; inventário/hash SHA-256 de todo o PC; validação física de todas as capacidades; proteção integral de segredos/histórico Git; ligações externas/âncoras de toda a documentação. Não interpretar NOT RUN/BLOCKED/FAIL como PASS.

## Regras de atualização

Antes de alterar este retrato: recolher PR/commit, ambiente, data, operação e evidência. Distinguir plano, teste com fixture, CI Windows, teste físico e aceitação humana. Para operações atuais, prevalece o HEAD exato verificado, não esta fotografia datada.