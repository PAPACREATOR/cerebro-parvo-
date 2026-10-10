# PR #41 — auditoria de referências documentais (2026-10-10)

## Âmbito imutável
Auditoria **somente leitura** da branch `docs/external-navigation-20261009` no SHA `46c6b6722028017b5c174986128be4a151588ae7`. A PR #41 pertence a outra frente. Não alterar o seu código, documentação, configuração ou histórico nesta PR #46.

Comparação com `main` no SHA `aeeb6f662a8282b3793708aa3e6782ef20d2d0ca`:
- `main`: 100 ficheiros `.md`.
- PR #41: 149 ficheiros `.md`; 54 caminhos novos, 29 caminhos partilhados com conteúdo alterado, 66 partilhados sem mudança e 5 caminhos `.md` de `main` ausentes nessa branch.
- Foram **lidos os 54 ficheiros Markdown novos e os 29 alterados**, usando o conteúdo do SHA de PR #41.
- Novos: 43 referências relativas Markdown analisadas; 10 caminhos sem destino na árvore PR #41.
- Alterados: 64 referências relativas Markdown analisadas; 0 caminhos sem destino.
- Partilhados sem mudança (66): conteúdo idêntico ao `main`; resta confirmar que a remoção/movimentação de ficheiros na branch não quebra as referências anteriormente válidas. **Não declarar rastreio completo da PR #41 antes desta verificação.**
- Método: links `[texto](destino)`, `![alt](destino)` e definições Markdown, sem interpretar links absolutos, URLs externos, âncoras `#`, HTML, wiki-links, imagens dinâmicas ou código gerador.

## Dez referências relativas sem destino na PR #41

| Documento original preservado | Linha | Destino relativo que falha | Candidato presente na árvore da PR #41 |
| --- | ---: | --- | --- |
| `historico/evolucao-2026-10-04/CONTINUIDADE-2026-10-04.md` | 15 | `PONTO-DE-SITUACAO.md` | `nexus/docs/PONTO-DE-SITUACAO.md` |
| mesmo | 15 | `F011-ARRANQUE-UNICO.md` | `nexus/docs/F011-ARRANQUE-UNICO.md` |
| mesmo | 16 | `F012-HASH-WINDOWS-ISOLADO.md` | `nexus/docs/F012-HASH-WINDOWS-ISOLADO.md` |
| mesmo | 16 | `F013-PROVENIENCIA-INVERSA.md` | `nexus/docs/F013-PROVENIENCIA-INVERSA.md` |
| `historico/evolucao-2026-10-04/ORGANIZACAO-E-FASES.md` | 6 | `PONTO-DE-SITUACAO.md` | `nexus/docs/PONTO-DE-SITUACAO.md` |
| `historico/evolucao-2026-10-04/RECUPERACAO-E-MATRIZ.md` | 5 | `F008-ISOLAMENTO-WINDOWS.md` | `nexus/docs/F008-ISOLAMENTO-WINDOWS.md` |
| mesmo | 6 | `F007-LIBREOFFICE.md` | `nexus/docs/F007-LIBREOFFICE.md` |
| mesmo | 7 | `F005-COGNICAO.md` | `nexus/docs/F005-COGNICAO.md` |
| mesmo | 8 | `PONTO-DE-SITUACAO.md` | `nexus/docs/PONTO-DE-SITUACAO.md` |
| mesmo | 9 | `F013-PROVENIENCIA-INVERSA.md` | `nexus/docs/F013-PROVENIENCIA-INVERSA.md` |

Os sete caminhos candidatos existem na árvore de PR #41; **a equivalência semântica de conteúdo não foi aqui certificada**. Não preencher links com documentos inventados nem reescrever snapshots históricos sem acordar o método de preservação. Sugestão para a pessoa responsável pela PR #41: índice de redirecionamentos ou corrigir só links de navegação, mantendo hashes e proveniência dos originais.

## Coordenação e limites
- Não duplicar a estrutura `docs/00-start-here` ou quaisquer alterações de `README.md`, `STATUS.md`, `DECISIONS.md`, `CONTRIBUTING.md` da PR #41.
- A PR #45 é de integração e permanece fora desta auditoria documental; não inferir PASS das suas afirmações.
- A cópia local e o clone de Sir Thaddeus pertencem ao Codex e não são afetados.
- Integração Sandy permanece suspensa por decisão humana; crédito ao autor mantido.
- Não alterar `nexus/` executável, Kernel, Host, Store, scripts, CI, dependências, testes, ou configurar ferramentas a partir deste relatório.

**Estado:** 83 documentos novos/alterados verificados para referências relativas; os 66 documentos sem alteração ainda aguardam verificação contra caminhos removidos na PR #41.
