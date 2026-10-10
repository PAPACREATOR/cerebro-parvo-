# Fronteiras de autoridade — contrato documental

Estado: invariantes do Nexus; descrição, não implementação nova.

A Folha/parser interpreta e propõe. **Não executa.** O Kernel/Host valida operação, bytes/anexos, regras, permissões, limites e confirmação vinculada ao pedido. Store/EventLog e proveniência pertencem ao núcleo. Um MCP externo ou adaptador direto não decide políticas nem escreve em Canonical.

**Dois portões diferentes:**
1. **Confirmação pré-execução:** o humano confirma a ação e o objeto exato antes do possível efeito. Edição, recusa, replay ou restart invalidam confirmação anterior; a operação tem de ser revalidada pelo Host.
2. **Human Gate de conhecimento:** o humano decide explicitamente promover um resultado de Creative para Canonical. A primeira confirmação não substitui a segunda.

Ferramentas como OpenNotebook, Writer/LibreOffice, LanguageTool, Zotero e ffmpeg recebem somente entradas autorizadas e devolvem resultados não confiáveis até validação. Se a ferramenta falhar, só a sua capacidade dependente é bloqueada; a identidade e memória Nexus não desaparecem. Repetição silenciosa de efeitos externos ambíguos após crash é proibida.

Windows: o Host pode limitar **os processos que lança**, conforme fronteiras nativas e testes aplicáveis; isso não equivale a governar todo o sistema operativo, nem demonstra instalação/segurança do PC físico.

Fontes: [Constituição](../../CEREBRO_CONSTITUTION.md), [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33), [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42), [PR #43](https://github.com/PAPACREATOR/cerebro-parvo-/pull/43), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45).