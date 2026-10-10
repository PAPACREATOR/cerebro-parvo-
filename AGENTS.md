# Instruções correntes — Cérebro

> **Nota de vigência (2026-10-10):** As menções abaixo a Activepieces como executor ou componente por defeito documentam uma proposta anterior. A decisão posterior de 30-09-2026 em [DECISIONS.md](DECISIONS.md) e [STATUS.md](STATUS.md) retira Activepieces do núcleo obrigatório; o Conductor é candidato sujeito a testes. Preservamos o texto histórico para auditoria. Nenhuma ferramenta passa a ter autoridade sobre o Kernel ou o Human Gate.


Ler, por esta ordem, [Projeto final auditado](docs/PROJETO-FINAL-AUDITADO-2026-09-28.md), CEREBRO_CONSTITUTION.md, CEREBRO_ARCHITECTURE.md, DECISIONS.md, STATUS.md e o contrato da tarefa.

## Regra principal

Não defender uma tecnologia porque já foi escolhida. Comparar primeiro. Manter uma decisão apenas se continuar a ser a forma mais simples de preservar o comportamento exigido.

Aplicar sempre:

USE > ADAPT > CREATE.

## Autoridade

- A pessoa é autoridade final.
- Activepieces executa; não decide conhecimento.
- Open Notebook/tiny produz proposta/evidência; não decide autoridade.
- Ferramentas externas devolvem UNTRUSTED.
- Instrução humana atual prevalece sobre comportamento aprendido.
- Creative e Canonical têm autoridade distinta.
- Similaridade semântica nunca autoriza eliminação.
- Nenhuma ferramenta publica, apaga ou promove diretamente sem o portão aplicável.

## Implementação

- M1–M14 são responsabilidades/invariantes, não exigem 14 serviços.
- IMP-001–026 são contratos/testes da família de importação, não exigem 26 módulos.
- Preferir flows/Subflows/Pieces/MCP/API/CLI existentes a código próprio.
- Não duplicar no Activepieces regras que pertencem ao Core.
- Não criar custom Piece quando um conector existente resolve.
- Um flow deve ter explicação equivalente em linguagem natural.
- Open Notebook usa um único espaço cognitivo por defeito; contexto e sessão são delimitados por tarefa.
- A tiny recebe contexto temático, fontes permitidas, budget e schema de saída.
- SQLite não é um terceiro cofre; coordena eventos/IDs/relações/estado/índices.
- Markdown/formatos abertos materializam Creative/Canonical.
- Obsidian/Joplin/Logseq não são dependências obrigatórias.

## Método de trabalho

Implementar vertical slices curtas:

contrato -> implementação mínima -> testes positivos/negativos/adversariais -> regressão -> evidência -> PASS/FAIL/NOT RUN.

Separar sempre:

- desenhado;
- implementado;
- testado;
- integrado;
- aprovado.

Não transformar um PASS unitário em release.

Para G10 usar o desenho PREPARED -> materialização Markdown -> verificação de hash -> COMMITTED -> reconcile, mas não declarar fechado antes dos testes de crash/replay.

Não aceitar segredos em prompts, publicar automaticamente, dar auto-approve global ou aumentar permissões silenciosamente.
