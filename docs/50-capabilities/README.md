# Capacidades externas — papel e prova necessária

As ferramentas devolvem trabalho especializado; nenhuma governa o Kernel. A presença de um adaptador, um teste simulado ou uma instalação planeada não prova função utilizável no PC.

| Ferramenta | Papel permitido | Limite atual documentado |
| --- | --- | --- |
| OpenNotebook | Pesquisa/revisão editorial, comparação, planeamento de podcast | Contratos parciais; E2E real Windows+SurrealDB+modelo ainda pendente |
| LibreOffice/Writer | Edição/render/export de documentos | Conversão histórica com evidência; Writer editorial sob LPAC ainda com gate independente/FAIL |
| LanguageTool | Revisão linguística local | Prova anterior por CLI não basta para aceitar toda a integração atual |
| Zotero | Referências e fontes | Capacidade delimitada; aceitação física não demonstrada aqui |
| ffmpeg/avatar | Media a partir de áudio e imagem | Não confundir plano/CLI/fixture com vídeo final no PC |
| ACE-Step/Forge | Geração de som/imagem sob controlo externo | Health check não equivale a geração física aprovada |
| Sir Thaddeus | Ferramenta externa potencial, sob autorização Host | Clone Git Linux registado; instalação/execução real Windows não provadas |
| Sandy | Investigação de sandbox Windows | Integração suspensa; guardar estudo e crédito, não ativar |

Princípios: execução por necessidade real, allowlist, inputs confinados, validação/proveniência do output, estado Creative e Human Gate antes de Canonical; sem Ollama obrigatório e sem fallback cloud implícito. A [matriz código-documentação da PR #45](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) distingue dez processos internos de operações naturais públicas e de capacidades físicas. O instalador completo pode exigir `llama.cpp`; isso não reintroduz Ollama como dependência.

Fontes: [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42), [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), [PR #48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48), [contratos técnicos Nexus](../../nexus/docs/).