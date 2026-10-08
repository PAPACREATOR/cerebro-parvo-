# Instruções correntes — Cérebro

## Coordenação atual — 07-10-2026

- PR #32 é a linha de produto Nexus/Windows mais completa.
- PR #31 é evidência transacional em `implementacao/ativa-2026-09-28/cerebro/`; não transfere PASS automaticamente para `nexus/`.
- Issue #33 define a convergência: levar primeiro as garantias da #31 para testes contra `nexus/`; alterar runtime apenas perante FAIL real e reproduzível.
- Os ramos só formam um candidato quando houver um único SHA com regressão conjunta verde.
- PR #34 trata apenas da documentação desta convergência.
- Preservar `historico/`, relatórios e genealogia. Limpeza documental não autoriza apagar evidência.
- O runtime local legado retirado não é requisito do percurso ativo; `llama.cpp` é a fronteira local candidata.

Ler primeiro o [ponto de situação operacional](nexus/docs/PONTO-DE-SITUACAO.md), depois `CEREBRO_CONSTITUTION.md`, `CEREBRO_ARCHITECTURE.md`, `DECISIONS.md` e o contrato da tarefa.

## Regras de autoridade

- A pessoa é autoridade final.
- Kernel/Host/Store governam estado e política.
- MCP transporta; não decide.
- Ferramentas externas devolvem apenas resultados/candidatos delimitados.
- Creative e Canonical têm autoridade distinta.
- Promoção para Canonical exige Human Gate.
- Instrução humana atual prevalece sobre comportamento aprendido.
- Similaridade semântica nunca autoriza eliminação.
- Eliminação automática só pode resultar de duplicação absolutamente exata e das regras humanas aplicáveis.
- M1–M14 são responsabilidades/invariantes; não redesenhar sem decisão humana explícita ou FAIL estrutural demonstrado.

## Regra de engenharia

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Não defender uma tecnologia por inércia. Não criar código próprio quando uma interface madura resolve sem violar as invariantes.

Para cada alteração:

`contrato → teste positivo/negativo/adversarial → FAIL real → correção mínima → regressão do bloco → regressão total → E2E`.

Separar sempre: desenhado, implementado, testado, integrado e aprovado.

PASS, FAIL, BLOCKED, NOT RUN e UNKNOWN não são equivalentes. Um PASS parcial não é release e não é transferido para outro SHA ou outro ramo.

## Implementação

- Runtime candidato: `nexus.app → nexus.host → nexus.store`.
- `implementacao/ativa-2026-09-28/cerebro/` é atualmente fonte de contratos/evidência transacional, não entrypoint do produto.
- Preferir adapters finos/API/CLI/MCP a duplicação de capacidades.
- OpenNotebook é bancada cognitiva substituível, não memória soberana.
- SQLite não é terceiro cofre; coordena estado/índices quando necessário.
- Markdown e formatos abertos materializam Creative/Canonical.
- IA/modelos não recebem autoridade.
- G10/persistência deve provar PREPARED → materialização durável → verificação → COMMITTED → reconcile/replay.

## Continuidade

- Antes de editar: ler HEAD, diffs recentes, comentários/reviews e workflows.
- Não criar novas filas, handoffs ou ficheiros de “estado” por sessão.
- Estado operacional: `nexus/docs/PONTO-DE-SITUACAO.md`.
- Decisões e genealogia: `DECISIONS.md`, `historico/` e relatórios datados.
- Coordenar trabalho paralelo por branches/PRs e nunca somar PASS de ramos divergentes.
- Não incluir credenciais, ambientes, runtime local ou cofres no Git.
- PC físico, modelos/GPU e instalações externas mantêm gates próprios; CI não substitui esses gates.
