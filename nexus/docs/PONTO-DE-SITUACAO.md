# Nexus — ponto de situação atual

Última revisão documental: 07-10-2026.

Este é o único documento de estado operacional corrente em `nexus/docs`. Relatórios antigos, FAIL→correção→PASS, comparações e decisões históricas permanecem no Git, em `historico/`, `DECISIONS.md` e nos relatórios datados; não são apagados nem tratados como estado atual.

## Linha de produto

**PR #32 — `cleanup/llamacpp-only-20261007`**

HEAD auditado de referência: `b5cb20c308099c3e153358bcc28e7571119db081`.

É a linha mais completa do produto Nexus/Windows neste momento. Deriva da PR #29 e mantém o runtime executável:

`nexus.app → nexus.host → nexus.store → adapters/MCP → ferramentas externas → Creative → Human Gate → Canonical`.

Nesse HEAD terminaram em SUCCESS:
- Auditoria e suites;
- Nexus Windows;
- Nexus Windows Confinement Gate;
- Nexus Integration Stress;
- OpenNotebook llama.cpp compatibility.

Isto prova CI/contratos/integração cobertos por esses gates. Não prova instalação física completa, modelos/GPU reais nem transforma testes determinísticos em inferências reais de modelo.

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
- MCP é transporte determinístico;
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

## O que falta antes de chamar produto integrado

- convergir as garantias transacionais relevantes da #31 para testes do runtime `nexus/`;
- obter um único HEAD com todos os gates relevantes verdes;
- resolver qualquer FAIL dessa convergência com alteração mínima;
- manter documentação alinhada com esse SHA;
- realizar aceitação física no PC para instalação, modelos/GPU e capacidades externas que dependam do hardware.

## Regra de trabalho

Não criar mais documentos de estado por sessão. Atualizar este ficheiro quando o estado operacional mudar. Guardar detalhes técnicos novos apenas em contratos/relatórios específicos quando acrescentarem evidência que não esteja já registada.
