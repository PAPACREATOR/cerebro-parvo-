# Nexus — Fluxo multi-ferramenta (estudo e primeira implementação isolada)

**Estado:** bancada/laboratório, não exposto na Folha oficial. Nenhuma ferramenta nova é executável por esta PR. **Não fazer merge** antes dos gates reais.

## 1. Circuito existente, lido no código

```text
Folha [texto + bytes/ficheiro]
  -> frontdoor.parse + propose_operation [proposta, sem autoridade]
  -> app._natural_request [schema, limites e validação de anexo]
  -> POST /api/prepare-run [ticket de uso único ligado a hash de pedido; TTL]
  -> confirmação humana explícita: POST /api/confirm-run
  -> Host.start [sessão + verify_integrity; Store.create = Kernel de estado]
  -> Host._run [Store.check_input + EXECUTING antes da chamada]
       -> prepare_task: input.bin e configuração da capability
       -> Writer DOCX/ODT: writer_sandy.convert (LPAC/Job)
          outras: Windows launch_confined -> adapters/runner.py
       -> envelope {result,trace} + artefacto verificável
  -> Store.accept [contratos, proveniência, Creative = HUMAN_REQUIRED]
  -> Host.prepare_approval [hash e ticket com caducidade]
  -> confirmação humana separada: Host.approve
  -> Store.promote [Canonical PASS + replay não executável]
```

A classe `HumanDecision` em `approval_binding.py` liga item, versão SHA-256, ator e ação; **não** substitui nenhum dos dois tickets. `contracts.py` valida JSON/schema e política fixa; o Host confere integridade. Um runner sem Host não recebe permissão, identidade, Store ou Canonical.

## 2. Contrato proposto para N ferramentas

- Entrada: `{text, filename, attachment}` + intenção resolvida do parser existente.
- Registo declarativo e estrito: `Capability(process, intent, command, tool, requires_attachment)`, associado a `PROCESS_TO_TOOL`, `PROCESS_FILES` e `laws/policy.json`.
- `CapabilityRouter.propose` devolve **um** candidato ou `Blocked`. Não importa o Host para o executar; zero IO e zero autorização. Suporta N entradas; duplicados, conflitos, texto desconhecido ou composto → bloqueio.
- Adaptador de execução: por enquanto permanece o código real existente de `adapters/runner.py` (dez rotas) e a exceção delimitada de Writer/LPAC em `host.py`. Não criar adaptadores que escapem ao sandbox.
- Autoridade: a implementação futura tem de aceitar a seleção apenas depois de `frontdoor.parse`, validação de anexo adequada à capability e *ticket* humano consumido no Host. O processo precisa estar na política fixa e passar `verify_integrity`.
- Saída: `{result,trace}` validado no Host; Creative; promoção Canonical **só** após segunda confirmação humana vinculada ao hash.
- Cadeia com duas ferramentas: cada passo usa um **novo pedido de Host e ticket humano individual**, resultados do passo anterior conservados e validados antes da proposta seguinte. Uma ferramenta não autoriza automaticamente a seguinte. Falhas não repetem execução no restart.

## 3. Específico Writer vs comum

| Comum | Só Writer |
| --- | --- |
| Parser, intenção, seleção, sessão Host | DOCX/ODT (ZIP) e extensão/MIME |
| Pré-autorização humana com hash e ticket | `writer_sandy.convert`, Sandy LPAC e namespace de pipe |
| Store.create, política, EXECUTING, isolamento | `soffice.com` e `sandy.exe` autorizados |
| Envelope, validação, Creative, Canonical | Verificação de PDF de exportação |
| Replay bloqueado e proveniência | Documento preparado, não composição automática de livro |

## 4. Matriz atual e limites

O runner interno implementa dez processos: verify, interpret (OpenNotebook), proofread (LanguageTool), convert_pdf e book (Writer), video/podcast/visual_podcast (plano OpenNotebook), music e web. Alguns devolvem **planos**, não produtos finais; uma proposta de plano nunca deve ser anunciada como vídeo/podcast/pesquisa concluída.

Este primeiro módulo **não** ativa os sete processos atualmente inacessíveis na Folha e não demonstra um fluxo real multi-ferramenta. Pendente: separar validações por capability sem enfraquecer ZIP, unificar frontdoor sob revisão, registar e vincular novos ficheiros ao manifesto, ensaiar autorização negada/aceite via HTTP e testar dois executores confinados de ponta a ponta em Windows. Não modificar Kernel nem Store para conseguir isso.

**Critério de fecho:** todos os workflows exigidos PASS no mesmo SHA, incluindo Windows nativo, LPAC, Writer real, outros adapters reais, stress, reinício, recusa e dois passos autorizados separadamente. Caso contrário: LAB/NOT RUN; não merge.
