# Nexus — fluxo genérico: contrato, implementação e prova

## Estado e fontes

**Integrado em `main` pela [PR #53](https://github.com/PAPACREATOR/cerebro-parvo-/pull/53) em 10-10-2026, às 17:02 de Lisboa.** HEAD testado: `e98bc6fa7dc18cdb4b26aa4deb7c68d7992eebfd`. Merge observado: `bfae55239d3803f3580f4ae29b7dfe99fec747a9`. Ambos têm a árvore Git `6c70de51642e4ee7fc36069443646bd5022d1895`; resultados continuam associados ao commit em que os testes correram.

Esta revisão documental usa esse código e os logs dos nove workflows do HEAD. A descrição antiga «PR Draft, não integrada» está preservada no [documento anterior por SHA](https://github.com/PAPACREATOR/cerebro-parvo-/blob/e98bc6fa7dc18cdb4b26aa4deb7c68d7992eebfd/nexus/docs/FLUXO-GENERICO-FERRAMENTAS-2026-10-10.md). A [PR #52](https://github.com/PAPACREATOR/cerebro-parvo-/pull/52) contém uma implementação alternativa não integrada; não deve ser confundida com a versão de `main`.

O estado operacional único está em [PONTO-DE-SITUACAO.md](PONTO-DE-SITUACAO.md). Integração em Git e SUCCESS de workflows não certificam uma release, todas as ferramentas futuras ou a instalação física no PC.

## 1. Circuito normal da Folha

Pedido e anexo → interpretação/seleção → proposta com hash → confirmação da execução → Host/Kernel → adaptador → validação → Creative → confirmação do resultado → Canonical.

| Etapa | Código responsável e comportamento observado |
| --- | --- |
| Interpretar | [`frontdoor.py`](../frontdoor.py) interpreta o pedido; não executa nem concede autorização. `/api/interpret` devolve `execution: NOT_AUTHORIZED`. |
| Selecionar | [`app.py`](../app.py) usa as regras existentes; o fallback de [`capability_router.py`](../capability_router.py) exige interpretação resolvida e prefixo explícito. Comando desconhecido ou composto é recusado. |
| Preparar | `/api/prepare-run` valida schema, nome, base64 e input até 2 MiB; Writer também exige DOCX/ODT e extensão compatíveis. Emite ticket ligado ao hash do pedido completo, com TTL de 180 s e limite de 64 pendentes. Não chama `Host.start`. |
| Autorizar execução | `/api/confirm-run`, em `app.py`, consome o ticket uma vez, exige `confirmed is True` e revalida pedido/hash. `False` cancela. Edição, expiração, uso repetido ou ticket perdido no reinício recusam execução. Só após estes controlos a rota chama `Host.start`. |
| Receber | [`host.py`](../host.py) verifica sessão, manifesto e exclusão de concorrência; [`Store.create`](../store.py) valida processo/política e conserva original, pedido, hashes e estado. |
| Executar | `Host._run` verifica o input e persiste `EXECUTING` antes da chamada. [`prepare_task`](../adapters/runner.py) prepara a área delimitada. OpenNotebook faz a chamada HTTP local pelo Host e fornece resposta limitada ao runner; os processos confinados não recebem credenciais do Store. |
| Delegar | Writer usa [`writer_sandy.convert`](../adapters/writer_sandy.py), com Sandy LPAC/Job. Os restantes processos usam `launch_confined` → [`runner.py`](../adapters/runner.py). O relay MCP interno não é obrigatório. |
| Validar retorno | Host exige envelope `{result, trace}`. `collect_artifact` valida schema e eventual PDF/hash; Store verifica input, fingerprint fixado, restrições do processo, contagem de IA e proveniência. Candidato válido entra em Creative como `HUMAN_REQUIRED`; falha não recebe aprovação automática. |
| Rever e promover | `Host.prepare_approval` emite outro ticket, ligado ao candidato e hash, com TTL de 300 s. `Host.approve` consome-o e cria [`HumanDecision`](../approval_binding.py). `Store.promote` verifica o binding e publica em Canonical. |
| Reiniciar | A reconciliação usa o input, resultados e decisões conservados. Não volta a executar ferramentas para reconstruir evidência nem inventa aprovação humana. |

O ticket de execução é consumido no servidor da Folha; o ticket de promoção é consumido no Host. `HumanDecision` liga ator, item, versão SHA-256 e ação, mas não substitui esses dois tickets. A rota `/api/run` é recusada no servidor normal; existe apenas como opção explícita de diagnóstico/teste. A prova de pré-autorização refere-se à rota normal do produto, não a todas as invocações Python internas imagináveis.

## 2. Interface comum e extensão

- Entrada normal: `{text, filename, attachment}`, onde `attachment` contém base64; todas as dez capacidades atuais exigem anexo.
- Descrição: `Capability(process, intent, command, tool, requires_attachment)`.
- Seleção: `CapabilityRouter.propose(intent=..., text=..., attachment_present=...)` devolve uma `Capability` única ou `Blocked`. O método seleciona sem I/O ou execução. `registered_router()` verifica os mapas do runner e lê a política; não concede permissões.
- Execução delimitada: o runner expõe `execute(process, input_path)` → `{result, trace}`; a rota Writer fornece o mesmo envelope. A tarefa entra pelo Host e mantém as restrições próprias do processo.
- Resultado: schema [`result.json`](../schemas/result.json), evidência e rastreio verificados; artefacto PDF obrigatório apenas nos processos Writer atuais. Aprovação para Canonical é independente da execução.

A classe do roteador aceita N entradas e tem teste com 100 capacidades sintéticas. O runtime autorizado contém exatamente dez processos, definidos em [`contracts.py`](../contracts.py), [`policy.json`](../laws/policy.json), [`request.json`](../schemas/request.json) e nos mapas do runner. **Adicionar uma entrada ao roteador não autoriza uma ferramenta nova.** A extensão exige revisão dos contratos, política, fingerprint, isolamento, resultado e compatibilidade com Store; a generalização atual não modificou Kernel nem Store.

O manifesto usa hashes SHA-256 e recusa divergências; isso não equivale a uma assinatura digital. Na PR #53, o Host mudou apenas para exigir o novo módulo nesse manifesto. Store, `contracts.py`, `approval_binding.py` e o código `cerebro/` permaneceram iguais à base `178333bf16e5232f097b6a61c9f0d6f0650e03fa`.

### Padrão comum e parte específica do Writer

| Comum às capacidades | Específico do Writer |
| --- | --- |
| Parser, intenção, seleção e sessão Host | Validação de DOCX/ODT, extensão e conteúdo do pacote |
| Confirmação pré-execução ligada ao hash do pedido | `writer_sandy.convert`, Sandy LPAC/Job e comportamento de IPC |
| Política, Store.create, estado EXECUTING e isolamento | Configuração de `soffice.com` e `sandy.exe` |
| Envelope, validação, Creative e decisão Canonical | Presença, formato e hash do PDF exportado |
| Original conservado, proveniência e reinício sem replay | Conversão do documento recebido; não composição editorial completa |

## 3. Capacidades atuais e saídas

| Processo | Adaptador/ferramenta | Saída e condição |
| --- | --- | --- |
| `verify` | [`verify_direct.py`](../adapters/verify_direct.py) | Comparação de hashes; não prova veracidade do conteúdo. |
| `interpret` | [`notebook.py`](../adapters/notebook.py) / OpenNotebook | Interpretação candidata de texto UTF-8; exige serviço e configuração locais. |
| `proofread` | [`languagetool.py`](../adapters/languagetool.py) | Sugestões candidatas; exige Java e LanguageTool configurados. |
| `convert_pdf`, `book` | Writer/Sandy e [`office.py`](../adapters/office.py) | PDF do DOCX/ODT fornecido; não compõe nem pagina um livro completo. |
| `video`, `podcast`, `visual_podcast` | [`product_routes.py`](../adapters/product_routes.py) / OpenNotebook | Plano candidato com microtarefas e citações; não produz ficheiro áudio/vídeo final. |
| `music` | `product_routes.py` | Especificação musical; exige Tema, Letra e Estilo; não gera áudio. |
| `web` | `product_routes.py` | Consulta preparada; não executa pesquisa nem inventa fontes. |

Os adaptadores existentes foram reutilizados. Disponibilidade do serviço, formato de input, execução da ferramenta e validade do resultado são gates distintos da seleção correta.

## 4. Prova no HEAD e98bc6f

| Workflow | Run | Estado |
| --- | --- | --- |
| Auditoria e suites | [38064843166](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843166) | SUCCESS |
| CodeQL | [38064846658](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064846658) | SUCCESS |
| Roteador genérico Windows/Linux | [38064843201](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843201) | SUCCESS |
| Front Door | [38064843167](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843167) | SUCCESS |
| Writer real Windows/Linux | [38064843212](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843212) | SUCCESS |
| Windows | [38064843126](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843126) | SUCCESS |
| Confinamento Windows 2022/2025 | [38064843182](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843182) | SUCCESS |
| Integration Stress | [38064843584](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843584) | SUCCESS |
| Pacote de aceitação Windows isolado | [38064843098](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/38064843098) | SUCCESS |

Nove workflows, 19 jobs concluídos; o checkout de `e98bc6fa7dc18cdb4b26aa4deb7c68d7992eebfd` foi confirmado nos 19 logs. Nos respetivos gates: roteador 41 PASS por sistema; Writer Windows 8 PASS, incluindo o teste de duas ferramentas reais `verify` → Writer/PDF; regressão completa 1821 PASS / 17 SKIP. Os SKIP não são convertidos em PASS. Os testes de Writer explicitamente ativados têm prova separada; backend/modelo completo OpenNotebook e PC pessoal continuam NOT RUN. As contagens de suites sobrepõem-se e não representam uma soma de inputs distintos.

Testes de referência: [`test_generic_capability_router.py`](../tests/test_generic_capability_router.py), [`test_generic_folha_gate.py`](../tests/test_generic_folha_gate.py), [`test_folha_writer_preexecution.py`](../tests/test_folha_writer_preexecution.py) e [`test_native_writer_route_real.py`](../tests/test_native_writer_route_real.py).

## 5. Limites e próximas fases

A seleção de dez capacidades e a prova real Verify/Writer estão integradas. Não há prova de execução universal de ferramentas futuras nem de criação final de todos os produtos multimédia. Configuração ausente, input incompatível, indisponibilidade, timeout ou retorno inválido bloqueiam o percurso; aprovação de um passo não autoriza o seguinte.

**Fase 1 desta revisão:** corrigir documentação e referências com a implementação preservada. A evidência funcional acima pertence à PR #53; os checks documentais do novo commit serão registados na PR desta fase. **Fase 2:** rever sintaxe e contratos num contexto separado. **Fase 3:** testar os blocos justificados pelos achados antes da regressão necessária. Estado corrente e progresso ficam exclusivamente em [PONTO-DE-SITUACAO.md](PONTO-DE-SITUACAO.md), preservando o histórico.
