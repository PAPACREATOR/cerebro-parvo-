# Cérebro Independente / Nexus

Sistema local-first de criação, conhecimento e execução governada para uma pessoa. A pessoa usa linguagem natural; o sistema compõe processos e ferramentas nos bastidores; a pessoa continua autoridade final.

## Estado atual

O protótipo Windows está em [nexus/](nexus/README.md). O estado operacional corrente está apenas em [nexus/docs/PONTO-DE-SITUACAO.md](nexus/docs/PONTO-DE-SITUACAO.md).

A composição candidata continua a ser:

**Folha em linguagem natural → Kernel/Host/Store Python → MCP determinístico → ferramentas externas → Creative → Human Gate → Canonical.**

Em 07-10-2026 existem duas frentes técnicas que ainda não formam um único HEAD:

- [PR #31](https://github.com/PAPACREATOR/cerebro-parvo-/pull/31): núcleo transacional auditado — ingestão, preservação de bytes, hash, PREPARED/COMMITTED, atomicidade, recovery/reconcile, idempotência, permissões e concorrência.
- [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32): continuação Windows da PR #29 — percurso `llama.cpp` local, compatibilidade OpenNotebook e remoção de referências ativas ao runtime legado.

Os ramos #31 e #32 estão divergentes. Não se somam os PASS como se fossem uma única versão. A convergência só é aceite quando o código necessário estiver num mesmo SHA e os gates aplicáveis voltarem a passar.

## Princípios que não mudam

- humano = autoridade máxima;
- Kernel/Host/Store governam estado e política;
- MCP transporta, não decide;
- Creative e Canonical permanecem separados;
- Canonical exige Human Gate;
- IA/modelos/ferramentas externas têm autoridade zero;
- M1–M14 permanecem invariantes da arquitetura;
- similaridade semântica nunca autoriza eliminação;
- eliminação automática só por duplicação absolutamente exata;
- PASS parcial nunca equivale a release;
- validação em CI não substitui aceitação física no PC.

## Runtime local de modelos

O percurso Windows ativo usa `llama.cpp` por endpoints OpenAI-compatible locais. Ollama não é dependência obrigatória nem requisito do instalador/runtime candidato.

Os testes de fronteira `llama.cpp` incluem contratos determinísticos e testes de compatibilidade. Isso não deve ser descrito como milhares de inferências físicas de modelo; a aceitação real de modelo/GPU continua separada.

## Ferramentas externas

OpenNotebook, LibreOffice, LanguageTool, Zotero, ACE-Step, Forge, FFmpeg e outras capabilities entram como ferramentas delimitadas. Nenhuma recebe autoridade para promover, publicar, apagar ou alterar Canonical diretamente.

OpenNotebook é bancada cognitiva, não memória soberana nem autoridade.

## Regra de engenharia

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

Não reabrir a arquitetura sem FAIL concreto e reproduzível. Não alterar o Kernel para acomodar uma ferramenta quando a fronteira/adaptador resolve.

## Estrutura documental

- [PONTO-DE-SITUACAO.md](nexus/docs/PONTO-DE-SITUACAO.md): fonte operacional;
- [CEREBRO_CONSTITUTION.md](CEREBRO_CONSTITUTION.md): invariantes;
- [CEREBRO_ARCHITECTURE.md](CEREBRO_ARCHITECTURE.md): responsabilidades;
- [DECISIONS.md](DECISIONS.md): decisões e genealogia;
- `historico/`: estados e caminhos substituídos, preservados para auditoria.

Relatórios PASS/FAIL e comparações técnicas não devem ser apagados só por serem antigos; deixam de ser “estado atual” e permanecem como evidência.

## Licença

Código e documentação próprios: PolyForm Noncommercial 1.0.0. Dependências mantêm as respetivas licenças.
