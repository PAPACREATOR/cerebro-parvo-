# Alterações

## 10-10-2026 — proposta documental isolada (sem merge)

- Novos índices de decisões fundamentadas, capacidades, provas por PR/SHA e história cronológica em docs/.
- Caminhos históricos preservados; nenhum ficheiro original movido, apagado ou reclassificado como runtime atual.
- Esclarecidos OpenNotebook especializado, confirmações humanas separadas, estado Draft das PRs e suspensão Sandy.
- Revisão posterior de compatibilidade com a PR #45: nova matriz `app.py`/parser/runner/Host/Store/sandbox/MCP/instalador por SHA; documentado que dez processos internos não equivalem a dez operações naturais públicas.
- Adicionados índices em `nexus/docs/README.md` e `historico/README.md`, catálogo de classificação documental, inventário navegável de 172 ficheiros Markdown no snapshot da branch e protocolo de prova.
- Reconciliação das 11 referências históricas identificadas na PR #46: dez links para `nexus/docs/` existentes, uma referência a `MEMORIA-DE-TRABALHO.md` ausente transformada em nota de proveniência sem criar/publicar a fonte reservada. Quatro páginas de época tiveram apenas reparações de navegação e avisos editoriais, com blobs anteriores por SHA.
- Consulta de evidências de 10/10: clone Git completo Sir Thaddeus no Linux da PR #48, 1.446 ficheiros verificados; não instalado/executado no PC. Writer Lab PR #1 demonstra diferença de namespace pipe legado/LOCAL sob LPAC; PR #2 testa Sandy em bancada autorizada, mantendo a integração no produto suspensa. Primeiro A/B no SHA fa8d65c4: **FAIL de execução/limpeza no caso A; caso B não executado**. Esse run no SHA 40d29078 terminou FAIL de metadados DACL; depois a PR #3 Writer Lab corrigiu o restauro fail-closed e obteve **PASS PDF real Windows/LPAC** no SHA `73be29f0` ([run 38049519797](https://github.com/PAPACREATOR/nexus-writer-lab/actions/runs/38049519797)), auditoria e CodeQL SUCCESS no mesmo SHA. A+B comparados, DACLs revalidadas, sem alterações ao runtime candidato do Nexus. [Dossier por SHA](docs/60-evidence/CONCILIACAO-WRITER-SIR-THADDEUS-2026-10-10.md).
- Somente Markdown: nenhuma alteração a código, testes, scripts, workflows ou configuração. Não implica PASS global.

[Índice](docs/README.md) · [Compatibilidade com código](docs/10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) · [Decisões](docs/40-decisions/README.md) · [História](docs/99-history/README.md) · [11 ligações reconciliadas](docs/99-history/RECONCILIACAO-11-REFERENCIAS-2026-10-10.md).

## 27-09-2026 — reconciliação autorizada

- Orientação atual alinhada com Folha Única/M1–M14 e fontes de 26/09.
- Trinta e cinco ficheiros anteriores preservados byte-a-byte e indexados como históricos.
- Três fontes Markdown integrais recuperadas e contratos corrigidos apresentados em separado.
- Nove ficheiros do pacote revisto importados como candidato, sem modificar implementação.
- Reprodução da suite fornecida; matrizes de cobertura, pendências e evidência real.
- Actions e modelos de issue/pull request para rastreabilidade futura.

[Changelog anterior](historico/repositorio-2026-09-24/CHANGELOG.md).
