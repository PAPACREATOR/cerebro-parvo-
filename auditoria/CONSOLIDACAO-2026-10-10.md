# Consolidação Nexus — 2026-10-10 (inventário e decisões pendentes)

## Âmbito e estado
Documento de auditoria numa branch isolada. Não altera Kernel, Host, Folha, executáveis, configurações, dependências, políticas, artefactos ou testes. Nenhuma remoção está autorizada por este documento. O GitHub público não prova que contenha tudo o que existe num computador local; é necessária comparação de ficheiros e hashes antes de declarar espelho completo.

## Prioridade
1. Criar inventário dos repositórios, branches, módulos, documentação, testes, artefactos e versões em disco; registar origem, HEAD, licença, estado e proveniência.
2. Rever a precedência documental (AGENTS.md, CEREBRO_CONSTITUTION.md, CEREBRO_ARCHITECTURE.md, DECISIONS.md, STATUS.md, contratos, prompts, PRs e issues recentes). Identificar e reconciliar contradições por decisão humana explícita, sem apagar a história.
3. Classificar cada dependência: núcleo, adaptador opcional, ferramenta especializada, laboratório, histórico ou candidata a remoção. Não confundir ausência de dependência obrigatória com proibição de uso como ferramenta.
4. Só depois propor diff mínimo; testar positivos, negativos, recusa de autorização, crash/replay, IPC/ACL, regressão e E2E Windows real. Uma prova laboratorial externa não substitui teste integrado Nexus.
5. Documentar PASS/FAIL/NOT RUN com SHA, ambiente, comando e evidência. Não declarar produto concluído com testes isolados.

## Contradição documental a corrigir, não por edição destrutiva
- DECISIONS.md (30-09) declara Activepieces como opção histórica superada e Nexus Minimal / Conductor candidato como direção vigente.
- STATUS.md reitera Activepieces fora do Core como requisito.
- AGENTS.md ainda diz «Activepieces executa» e recomenda flows/Pieces como implementação.
- CEREBRO_CONSTITUTION.md e CEREBRO_ARCHITECTURE.md continuam a apresentar Activepieces como padrão operacional.
Interpretação provisória pela regra explícita de precedência: decisões humanas posteriores prevalecem, mas alterações normativas carecem de reconciliação rastreável. **Não remover bibliotecas, flows ou documentos existentes por simples pesquisa textual.** Preservar histórico e assinalar partes substituídas.

## Contributo externo: Hrvoje Abraham — Sandy CLI
Hrvoje Abraham, autor do projeto open-source Sandy CLI (https://github.com/ahrvoje/sandy_cli), respondeu à investigação Nexus sobre LibreOffice Writer em LPAC/AppContainer. Em 2026-10-10 comunicou um teste próprio com intercetação e renomeação de named pipe para namespace LOCAL, edição de documento dentro de LPAC com permissões mínimas, e disponibilizou a versão v0.9994 e demonstração pública:
- https://ahrvoje.github.io/sandy_cli/libreoffice.html
- https://github.com/ahrvoje/sandy_cli/blob/main/docs/libreoffice-demo.py
- Issue original: https://github.com/PAPACREATOR/cerebro-parvo-/issues/36
Crédito pela investigação e pelo código Sandy cabe ao respetivo autor. Isto **não** significa que seja membro, parceiro ou coautor do Nexus. O seu trabalho deve ser atribuído onde for efetivamente reutilizado, cumprindo licença e avisos de terceiros.

### Gate de eventual integração Sandy
- Inspecionar licença e cadeia de dependências da versão exata; comparar Sandy vs launcher LPAC atual, sem alteração da lógica do Kernel.
- Clonar/experimentar em laboratório independente; registar commit, hashes, configuração, permissões e execução.
- Provar Writer + criação/ligação de pipe, limites de leitura/escrita, processos filhos, falhas/negações, e zero aumento silencioso de privilégios.
- Integrar apenas o adaptador mínimo justificado por evidência, mantendo reversão possível.

## Invariantes não negociáveis
Autoridade humana; Kernel governa permissões; Host não contorna autorização; Creative/Canonical distintos; proveniência, bytes originais, hashes, atomicidade e recuperação; IA sem autoridade; eliminação automática apenas duplicado exato quando contratualmente permitida; Ollama não obrigatório; sem publicação automática nem auto-approve global.

## Estado desta anotação
DOCUMENTADO: evidência de correspondência técnica externa e contradições entre documentos.
NÃO EXECUTADO: cópia integral do computador, integração de Sandy no Nexus, remoção de Activepieces, instalação e ensaios E2E do Windows.
