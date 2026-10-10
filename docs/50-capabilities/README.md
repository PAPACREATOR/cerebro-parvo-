# Capacidades externas — papel e prova necessária

As ferramentas devolvem trabalho especializado; nenhuma governa o Kernel. A presença de um adaptador, um teste simulado ou uma instalação planeada não prova função utilizável no PC.

| Ferramenta | Papel permitido | Limite atual documentado |
| --- | --- | --- |
| OpenNotebook | Pesquisa/revisão editorial, comparação, planeamento de podcast | Contratos parciais; E2E real Windows+SurrealDB+modelo ainda pendente |
| LibreOffice/Writer | Edição/render/export de documentos | **PASS PDF real na bancada Windows LPAC** [PR #3](https://github.com/PAPACREATOR/nexus-writer-lab/pull/3), SHA `73be29f0`: A sem pipe `LOCAL` FAIL; B PASS em 7,218 s, 13.902 bytes, DACL original recuperada. **NOT RUN nas rotas Host reais do Nexus e no PC pessoal** |
| LanguageTool | Revisão linguística local | Prova anterior por CLI não basta para aceitar toda a integração atual |
| Zotero | Referências e fontes | Capacidade delimitada; aceitação física não demonstrada aqui |
| ffmpeg/avatar | Media a partir de áudio e imagem | Não confundir plano/CLI/fixture com vídeo final no PC |
| ACE-Step/Forge | Geração de som/imagem sob controlo externo | Health check não equivale a geração física aprovada |
| Sir Thaddeus | Ferramenta externa potencial, sob autorização Host | Clone Git completo **PASS de integridade** na PR #48 (1.446/1.446 ficheiros em Linux); instalação, execução e integração Windows **NOT RUN** |
| Sandy | Instrumento experimental de isolamento Windows | Bancada A/B Windows LPAC [PR #3](https://github.com/PAPACREATOR/nexus-writer-lab/pull/3) obteve PASS do PDF e das DACLs recuperadas; **integração de Sandy no Nexus continua suspensa** e não é dependência aprovada |

Princípios: execução por necessidade real, allowlist, inputs confinados, validação/proveniência do output, estado Creative e Human Gate antes de Canonical; sem Ollama obrigatório e sem fallback cloud implícito. A [matriz código-documentação da PR #45](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) distingue dez processos internos de operações naturais públicas e de capacidades físicas. O instalador completo pode exigir `llama.cpp`; isso não reintroduz Ollama como dependência.

Relatório de hoje: [clonagem Sir Thaddeus e Writer/Sandy por SHA](../60-evidence/CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md), com limites do CI e do PC físico.

Fontes: [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42), [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), [PR #48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48), [contratos técnicos Nexus](../../nexus/docs/).