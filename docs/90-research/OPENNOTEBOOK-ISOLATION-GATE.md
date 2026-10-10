# Gate OpenNotebook — isolamento, funcionalidade e valor

> **Vigência 10/10:** a classificação KEEP/OPTIONAL/REMOVE no final deste estudo ficou histórica quanto à decisão de produto. A [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42) regista decisão humana posterior: OpenNotebook é ferramenta especializada valorizada, escolhida por tarefa, nunca motor obrigatório nem autoridade. Os gates técnicos deste estudo continuam hipóteses úteis a validar. [ADR](../40-decisions/ADR-2026-10-09-OPENNOTEBOOK.md).

Data: 2026-10-09  
Estado: investigação. Não altera o runtime.

## Papel permitido

OpenNotebook é uma bancada externa e opcional. Não é Kernel, Store, Creative, Canonical, autoridade nem memória soberana.

## Estado já demonstrado

No candidato da PR #32:

- OpenNotebook está fixado em `lfnovo/open-notebook@315d5255af2a5132aada41c94d5c3c5dc8e837aa`;
- SurrealDB está fixado em 2.7.0;
- o runtime local usa endpoints llama.cpp OpenAI-compatible;
- o workflow `OpenNotebook llama.cpp compatibility` passou no HEAD `da86b6dd181d00fd7a87addaa01a12ec3a14e57b`;
- Ollama não é requisito Nexus.

## Fronteira atual

No Windows, o Host Nexus faz a chamada loopback autorizada e reduz a resposta a um ficheiro temporário entregue ao processo confinado.

O processo confinado:
- não recebe configuração administrativa OpenNotebook;
- não precisa de acesso de rede à bancada;
- não recebe acesso ao Store Nexus;
- só pode devolver um candidato UNKNOWN;
- não pode promover para Canonical.

Antes da chamada externa o Host persiste `execution_phase=EXECUTING`. Recovery não deve reconstruir um resultado repetindo silenciosamente a cognição.

## Persistência da transformação simples

O endpoint usado pelo Nexus é `POST /api/transformations/execute` com `input_text`.

No código upstream analisado, um insight só é persistido quando a transformation graph recebe um objeto Source. O caminho usado pelo Nexus fornece texto simples. Portanto a hipótese a provar é: uma transformação Nexus simples não cria Source, Note ou Insight no OpenNotebook.

## O que ainda não está provado

Os testes atuais provam contratos e compatibilidade, mas ainda não provam um E2E Windows completo com:

`Nexus → OpenNotebook real → modelo llama.cpp real → resposta estruturada → Creative → Human Gate → Canonical`.

Também falta provar que a bancada pode ser removida e reconstruída sem afetar conhecimento Nexus aprovado.

## Gates O0–O8

### O0 — instalação fixada
Versões e commits esperados ficam verificáveis.

### O1 — isolamento de serviço
OpenNotebook, base de dados e modelos permanecem locais e não são autoridade Nexus.

### O2 — separação de dados
Dados OpenNotebook e dados Nexus usam raízes independentes. A bancada não recebe paths de Creative, Canonical, aprovação ou EventLog.

### O3 — transformação real
Executar uma transformação com modelo local real. Exigir schema cognitivo válido, citações literais verificáveis e resultado `UNKNOWN/candidate`.

Antes/depois, verificar que a transformação simples não criou conhecimento persistente inesperado no OpenNotebook.

### O4 — negativos
Resposta inválida, citação inventada, indisponibilidade, timeout ou configuração incompatível devem falhar fechados sem escrita em Canonical.

### O5 — crash
Interrupção depois de `EXECUTING` mas antes de resultado durável não pode provocar repetição automática do efeito externo.

### O6 — independência
Depois de aprovação humana e commit Canonical, Nexus deve reiniciar e verificar o resultado sem precisar de OpenNotebook, base de dados da bancada ou modelo.

### O7 — reconstrução
Uma instalação nova e vazia da bancada, com a configuração autorizada recriada, deve conseguir executar novos pedidos sem importar memória anterior OpenNotebook.

### O8 — prova de valor
Testar separadamente capacidades que poderiam justificar a bancada:
- ingestão documental;
- pesquisa textual/vetorial;
- contexto multi-source;
- revisão de livros por partes;
- títulos, sinopses e notas editoriais;
- podcast.

Medir código Nexus evitado, recursos, complexidade e qualidade.

## Decisão

**KEEP opcional:** O0–O7 passam e O8 evita quantidade material de código próprio.

**OPTIONAL avançado:** útil para livros, pesquisa ou podcasts, mas desnecessário para o núcleo.

**REMOVE do produto base:** se só for usado para transformar texto curto; nesse caso uma capability local mais simples pode ser suficiente.

A hipótese preferida atual é: **OpenNotebook como bancada opcional avançada, nunca como cérebro do Nexus.**
