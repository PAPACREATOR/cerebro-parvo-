# Reconciliação das 11 referências históricas da auditoria PR #46

**Data:** 10/10/2026. **Resultado:** 10 links técnicos reparados para caminhos existentes; 1 referência a documento reservado transformada em **nota de proveniência**, não em cópia fictícia. **Só Markdown alterado.** O código do Nexus, scripts, workflows, configurações, Kernel/Host/Store e testes não foram tocados.

## Escopo de verdade

- [Auditoria de origem (PR #46)](https://github.com/PAPACREATOR/cerebro-parvo-/blob/6ebf4912ee0ce58eece0aa9f4f26842aca177010/auditoria/PR41-AUDITORIA-LIGACOES-2026-10-10.md): leitura da PR #41 no commit `46c6b6722028017b5c174986128be4a151588ae7`, 149 Markdown e 168 referências relativas; 11 destinos em falta naquele snapshot.
- [Árvore documental anterior à reparação](https://github.com/PAPACREATOR/cerebro-parvo-/tree/adbbd5408f7646578400ec71b915bb53dd8eae27): histórico e hashes originais conservados pelo Git.
- [PR #45 candidata técnica](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), `66027af7f2ea084bc62d85b840d1fc3113e60a97`: a referência atual de comportamento do código que esta frente leu; **não** é release e não foi modificada.
- [Matriz de compatibilidade com o código](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md): explica a diferença entre sete intenções no parser, dez processos internos e apenas `verify` como proposta natural pública na API, no SHA referido.

## Mapa explícito das dez referências reparadas

Os caminhos na coluna «destino agora» são **relativos a cada um dos três documentos** situados em `historico/evolucao-2026-10-04/`. São hiperligações para o repositório publicado; o texto de época, os números dos testes e as conclusões históricas não foram atualizados para simular novos PASS.

| Documento de época | Link antigo sem destino | Destino agora existente | Natureza |
| --- | --- | --- | --- |
| `CONTINUIDADE-2026-10-04.md` | `PONTO-DE-SITUACAO.md` | [`../../nexus/docs/PONTO-DE-SITUACAO.md`](../../nexus/docs/PONTO-DE-SITUACAO.md) | ponto de situação acumulado, não release |
| `CONTINUIDADE-2026-10-04.md` | `F011-ARRANQUE-UNICO.md` | [`../../nexus/docs/F011-ARRANQUE-UNICO.md`](../../nexus/docs/F011-ARRANQUE-UNICO.md) | relatório F011 |
| `CONTINUIDADE-2026-10-04.md` | `F012-HASH-WINDOWS-ISOLADO.md` | [`../../nexus/docs/F012-HASH-WINDOWS-ISOLADO.md`](../../nexus/docs/F012-HASH-WINDOWS-ISOLADO.md) | relatório F012 |
| `CONTINUIDADE-2026-10-04.md` | `F013-PROVENIENCIA-INVERSA.md` | [`../../nexus/docs/F013-PROVENIENCIA-INVERSA.md`](../../nexus/docs/F013-PROVENIENCIA-INVERSA.md) | relatório F013 |
| `ORGANIZACAO-E-FASES.md` | `PONTO-DE-SITUACAO.md` | [`../../nexus/docs/PONTO-DE-SITUACAO.md`](../../nexus/docs/PONTO-DE-SITUACAO.md) | ponto de situação, evolução posterior |
| `RECUPERACAO-E-MATRIZ.md` | `F008-ISOLAMENTO-WINDOWS.md` | [`../../nexus/docs/F008-ISOLAMENTO-WINDOWS.md`](../../nexus/docs/F008-ISOLAMENTO-WINDOWS.md) | contrato/relatório F008 |
| `RECUPERACAO-E-MATRIZ.md` | `F007-LIBREOFFICE.md` | [`../../nexus/docs/F007-LIBREOFFICE.md`](../../nexus/docs/F007-LIBREOFFICE.md) | contrato/relatório F007 |
| `RECUPERACAO-E-MATRIZ.md` | `F005-COGNICAO.md` | [`../../nexus/docs/F005-COGNICAO.md`](../../nexus/docs/F005-COGNICAO.md) | contrato/relatório F005 |
| `RECUPERACAO-E-MATRIZ.md` | `PONTO-DE-SITUACAO.md` | [`../../nexus/docs/PONTO-DE-SITUACAO.md`](../../nexus/docs/PONTO-DE-SITUACAO.md) | ponto de situação acumulado |
| `RECUPERACAO-E-MATRIZ.md` | `F013-PROVENIENCIA-INVERSA.md` | [`../../nexus/docs/F013-PROVENIENCIA-INVERSA.md`](../../nexus/docs/F013-PROVENIENCIA-INVERSA.md) | relatório F013 |

Os quatro documentos de época agora mantêm um aviso editorial que aponta à [matriz da implementação atual](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md) e à sua versão original antes desta alteração.

## Décima primeira referência: original reservado em falta

Fonte: `historico/repositorio-2026-09-24/README.md`. Link antigo `[MEMORIA-DE-TRABALHO.md](MEMORIA-DE-TRABALHO.md)` (destino inexistente). A redação agora preserva **o nome literal** da memória referida e aponta para a [nota de documento não publicado](REFERENCIA-RESERVADA-MEMORIA-DE-TRABALHO-2026-10-10.md). Isso **não significa que a memória foi encontrada, recuperada ou publicada**. O `.gitignore` vigente exclui expressamente `MEMORIA-DE-TRABALHO.md`.

## Fonte original imutável em Git

| Documento retocado na navegação | Blob Git **antes** da reparação |
| --- | --- |
| [Continuidade — original](https://github.com/PAPACREATOR/cerebro-parvo-/blob/adbbd5408f7646578400ec71b915bb53dd8eae27/historico/evolucao-2026-10-04/CONTINUIDADE-2026-10-04.md) | `c14004c3bbd3eb9c8192966e29a52aae0c6c1b48` |
| [Organização — original](https://github.com/PAPACREATOR/cerebro-parvo-/blob/adbbd5408f7646578400ec71b915bb53dd8eae27/historico/evolucao-2026-10-04/ORGANIZACAO-E-FASES.md) | `1dd53def411eb1f86d3ae97be97d8cc6f7ef4f9c` |
| [Recuperação — original](https://github.com/PAPACREATOR/cerebro-parvo-/blob/adbbd5408f7646578400ec71b915bb53dd8eae27/historico/evolucao-2026-10-04/RECUPERACAO-E-MATRIZ.md) | `4ba9420ee841c7994d960394de580a508718b5ba` |
| [README 24/09 — original](https://github.com/PAPACREATOR/cerebro-parvo-/blob/adbbd5408f7646578400ec71b915bb53dd8eae27/historico/repositorio-2026-09-24/README.md) | `fbdf3a66d4950c079f87d41afbbad5e065fc9aba` |

**Método de preservação:** as quatro páginas de época foram alteradas **somente na navegação e em avisos editoriais**; conteúdo técnico, tabelas, comandos e provas existentes foram mantidos. Os originais continuam acessíveis pelo commit e blob antigos. Não houve movimentação/eliminação de ficheiros ou cópia para outro repositório.

## Verificação e limites

- Alvos técnicos conferidos como ficheiros existentes na árvore da PR #49 antes das alterações.
- Confirmar após commit que as 11 referências já não aparecem como destinos inexistentes, incluindo esta nota de proveniência.
- Isto **fecha o defeito de navegação** daquela lista, mas **não prova equivalência semântica completa** entre versões dos relatórios, todos os links externos ou âncoras, aceitação Windows física, Writer/LPAC, OpenNotebook real, nem integração do candidato na `main`.
- A auditoria original da PR #46 permanece imutável, descrevendo corretamente a situação **anterior**.

## Regra para revisões futuras

Se um documento de época e um relatório atual contradisserem-se, não modificar retroativamente o PASS ou a implementação: etiquetar o estado de época e indicar SHA e fonte atual. Só a equipa de implementação autorizada pode alterar código; esta frente corrige documentação exclusivamente.
