# Nexus — ponto de situação atual

Última revisão documental: 07-10-2026.

Este é o único documento de estado operacional corrente em `nexus/docs`. Relatórios antigos, FAIL→correção→PASS, comparações e decisões históricas permanecem no Git, em `historico/`, `DECISIONS.md` e nos relatórios datados; não são apagados nem tratados como estado atual.

## Linha de produto

**PR #32 — `cleanup/llamacpp-only-20261007`**

HEAD auditado de referência: `60ece4fd9160ede68b70a3c6a34b556b9d61c1c4`.

É a linha mais completa do produto Nexus/Windows neste momento. Mantém o runtime executável:

`nexus.app → nexus.host → nexus.store → adapters/MCP → ferramentas externas → Creative → Human Gate → Canonical`.

Estado dos gates nesse HEAD:
- Auditoria e suites — **PASS**;
- Nexus transactional crash gate — **PASS**;
- OpenNotebook llama.cpp compatibility — **PASS**;
- Nexus Windows Confinement Gate — **PASS**;
- Nexus Windows — **FAIL**;
- Nexus Integration Stress — **FAIL**.

Os dois FAILs correntes estão localizados nos mesmos testes de arranque em `nexus/tests/test_startup.py`: os testes ainda interceptam `os.replace`, enquanto a escrita atómica no Windows passou a publicar através de `MoveFileExW(..., MOVEFILE_WRITE_THROUGH)`. O runtime não deve ser regredido para satisfazer uma observação de implementação antiga; os testes devem verificar a fronteira atómica vigente e continuar a provar que nunca é exposta uma referência truncada e que uma falha de publicação conserva a referência anterior.

Isto prova apenas o que os gates executam. Não prova instalação física completa, modelos/GPU reais nem transforma testes determinísticos em inferências reais de modelo.

## Núcleo transacional auditado

**PR #31 — `work-core-audit-20261007`**

HEAD de referência: `628359cb4dfc363734894e0724eba25fb164acd8`.

Auditou em `implementacao/ativa-2026-09-28/cerebro/`:
- ingestão e preservação byte-a-byte;
- SHA-256;
- PREPARED → escrita temporária → durabilidade → COMMITTED;
- crashes reais e reconcile/replay;
- idempotência;
- concorrência;
- path traversal e symlinks;
- adulteração;
- permissões POSIX/ACL Windows;
- integração core → persistence.

Os gates próprios passaram, mas este diretório não é o entrypoint do produto atual. Portanto os PASS da #31 são evidência útil, não validação automática do runtime `nexus/`.

## Convergência obrigatória

Issue **#33** define a regra:

1. usar a linha #32 como base do produto;
2. traduzir cada garantia útil da #31 em teste contra `nexus/`;
3. não copiar o núcleo antigo por atacado;
4. alterar `nexus/` apenas perante FAIL real e reproduzível;
5. fazer a correção mínima;
6. repetir os gates aplicáveis no mesmo SHA;
7. só esse SHA pode ser chamado candidato convergido.

A PR #34 é exclusivamente documental e não altera runtime, Kernel, Host, Store, testes, workflows ou instalação.

## Arquitetura e autoridade

Continuam vigentes:
- pessoa = autoridade final;
- M1–M14 permanecem invariantes;
- Kernel/Host/Store governam estado e política;
- MCP é transporte quando acrescenta uma fronteira útil; não é autoridade nem segundo orquestrador;
- ferramentas/modelos externos têm autoridade zero;
- Creative precede Canonical;
- promoção para Canonical exige Human Gate;
- similaridade nunca autoriza eliminação;
- eliminação automática só por duplicação absolutamente exata;
- falha, timeout, ausência de evidência e UNKNOWN nunca contam como PASS.

## Runtime local de modelos

Ollama não é dependência obrigatória nem requisito do percurso ativo.

O candidato Windows usa `llama.cpp` por endpoints OpenAI-compatible locais para linguagem/embeddings. OpenNotebook e outras ferramentas devem permanecer subordinados ao Kernel e substituíveis.

A limpeza do runtime antigo aplica-se às superfícies ativas. `historico/` e a genealogia não devem ser reescritos apenas para satisfazer um teste textual.

## Simplificação ainda por provar

A auditoria de 07-10 identificou pontos para teste antes de refactor:

- a Folha executável ainda recebe um `process` escolhido pela UI, enquanto `frontdoor.py`, `natural_bridge.py` e `tiny_classifier.py` existem e são extensamente testados mas não pertencem ao percurso executável atual nem ao manifesto de integridade; o produto final deve ter um único estado claro: integrar essa Front Door no percurso oficial ou mantê-la explicitamente fora do runtime até à integração;
- processos/capabilities são descritos em vários limites (policy, schema, Store, runner e UI); manter defesas independentes é aceitável, mas deve existir teste automático de consistência para impedir drift;
- `adapters/runner.py` contém também `execute_confined()`, além do caminho Host → `launch_confined`; confirmar callers reais e manter apenas um proprietário ativo da execução externa;
- os scripts Windows ainda apresentam várias superfícies de arranque/instalação e alguns defaults históricos de branch; para o protótipo deve existir um único entrypoint humano, com helpers internos claramente não oficiais;
- a publicação Canonical tem testes de atomicidade/recovery no processo, mas a garantia de morte real/power-loss no rename final deve ser provada antes de se declarar T4 completo nesse ponto.

Nenhum destes itens autoriza remover Human Gate, hashes, proveniência, confinement, recovery ou verificações independentes.

## O que falta antes de chamar produto integrado

- corrigir os dois FAILs de arranque sem enfraquecer a atomicidade Windows;
- convergir as garantias transacionais relevantes da #31 para testes do runtime `nexus/`;
- obter um único HEAD com todos os gates relevantes verdes;
- provar um único percurso ativo por responsabilidade;
- definir um único entrypoint de instalação/arranque para o protótipo Windows;
- manter documentação alinhada com esse SHA;
- realizar aceitação física no PC para instalação, modelos/GPU e capacidades externas que dependam do hardware.

## Regra de trabalho

Não criar mais documentos de estado por sessão. Atualizar este ficheiro quando o estado operacional mudar. Guardar detalhes técnicos novos apenas em contratos/relatórios específicos quando acrescentarem evidência que não esteja já registada.
