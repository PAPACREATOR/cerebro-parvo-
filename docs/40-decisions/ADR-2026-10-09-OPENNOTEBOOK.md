# ADR — OpenNotebook como ferramenta especializada, não eixo obrigatório

Data da decisão humana: 09-10-2026. Estado: **orientação vigente**; execução real integrada **não validada**.

**Problema:** um notebook cognitivo pode reduzir trabalho editorial e multimédia, mas transformá-lo em orquestrador obrigatório ameaça a independência do Kernel e da memória.

**Decisão:** o Kernel/Host escolhe microprocessos e decide se a operação pede OpenNotebook, LibreOffice, LanguageTool, Zotero, ffmpeg ou execução determinística direta. OpenNotebook é útil para pesquisa multi-fonte, interpretação, grelhas de revisão, capítulos de livros, títulos, sinopses, preparação de podcasts. Não recebe autoridade, Store, Canonical, políticas, publicação nem execução arbitrária.

**Porquê:** evitar um segundo cérebro, garantir funcionamento sem a bancada e obter ganho de capacidades com menos código próprio. O Nexus não deve depender de uma ferramenta para ações que não a exigem.

**Limites comprovados:** PR #45 possui integração/contratos parciais e testes com peer HTTP de teste. PR #44 acrescenta negativos, mas não prova OpenNotebook + SurrealDB + modelo reais em Windows. Guião de podcast não é ficheiro áudio. Ollama não é requisito nem fallback automático.

**Gates pendentes:** O0–O8 e M1–M6 da [issue #42](https://github.com/PAPACREATOR/cerebro-parvo-/issues/42); caso E2E real com fontes/citações; caso integral sem OpenNotebook; isolamento, crash e reconstrução da bancada. Não declarar capability pronta antes disso.

**Histórico:** a classificação prévia KEEP/OPTIONAL/REMOVE da [investigação de 09/10](../90-research/OPENNOTEBOOK-ISOLATION-GATE.md) foi ultrapassada quanto ao papel da ferramenta, mas conserva as perguntas de prova e critérios de segurança.