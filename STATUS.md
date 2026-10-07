# Estado atual do Nexus

A única fonte operacional corrente é [nexus/docs/PONTO-DE-SITUACAO.md](nexus/docs/PONTO-DE-SITUACAO.md).

## Estado em 07-10-2026

Há duas frentes técnicas válidas, mas ainda **não convergidas num único HEAD**:

- **PR #31 — Core transacional**: branch `work-core-audit-20261007`, HEAD `628359cb4dfc363734894e0724eba25fb164acd8`. Auditoria do núcleo de ingestão/persistência/atomicidade/recovery concluída com gates Ubuntu, Windows e CodeQL verdes. Este ramo parte de `main`.
- **PR #32 — llama.cpp-only / Windows**: branch `cleanup/llamacpp-only-20261007`, HEAD de referência `b5cb20c308099c3e153358bcc28e7571119db081`. Continuação da instalação Windows da PR #29; remove dependência do runtime local legado e valida compatibilidade OpenNotebook + llama.cpp. Este ramo parte de `lab/windows-full-install-20261006`.

Os ramos estão divergentes. Um PASS da #31 não é automaticamente PASS da #32, e vice-versa. Só existe candidato integrado depois de convergência explícita e repetição dos gates aplicáveis no mesmo SHA.

## Regras vigentes

- A pessoa é a autoridade máxima.
- Kernel/Host/Store mantêm estado e política; MCP é transporte.
- Creative precede Canonical; promoção exige Human Gate.
- M1–M14 permanecem congelados.
- IA/modelos/ferramentas externas têm autoridade zero.
- Ollama não é dependência obrigatória do percurso ativo; o candidato Windows usa `llama.cpp` por fronteira OpenAI-compatible local.
- Similaridade nunca autoriza eliminação automática; apenas duplicação absolutamente exata.
- FAIL, BLOCKED e NOT RUN nunca contam como PASS.
- PASS de CI não equivale a instalação física no PC.

## Regra documental

Não criar novos ficheiros de estado, continuidade, fila ou handoff por sessão. Atualizar apenas o ponto de situação operacional e relatórios técnicos quando existir evidência nova. Histórico, comparações e FAIL→correção→PASS permanecem preservados no Git e nas PRs.
