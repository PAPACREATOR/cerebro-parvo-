# Controlo das proteções Windows — contrato proposto

Estado em 11-10-2026: **PROPOSTA; alteração efetiva NÃO IMPLEMENTADA**.
Base: `main` `0f39fc81fc6f8109cdea66db8e15cf8bb8de0671`.
Este contrato não concede permissões nem cria uma ferramenta executável.

## Pedido e fronteira encontrada

Pedro pediu que o Host possa propor ativação perante perigo e desativação quando
ele a autorizar, com os privilégios necessários e registo da alteração. **Ativar e
desativar exigem decisão humana explícita.** A Folha apresenta a proteção, motivo,
efeito e resultado; executores, IDs, tickets e detalhes internos ficam na evidência.
Mantêm-se as regras de não alterar Kernel nem Store e de trabalhar por microfases.

A versão lida admite dez processos. `contracts.load_policy()` exige a lista exata;
o schema do pedido, registo de capacidades e runner têm de concordar com ela.
Nenhum processo administra proteções Windows. `Host._run()` usa AppContainer/LPAC
e Job, com exceção delimitada para o Writer/Sandy. Essa execução de ferramentas
não recebe autorização administrativa para alterar o sistema.

Escolher uma ferramenta pelo roteador não regista uma capacidade no Kernel,
concede elevação ou transforma a aprovação de um documento em consentimento para
alterar o Windows. Não reutilizar `verify`, `web`, Writer ou MCP para esconder uma
operação administrativa. Não elevar o Host inteiro nem retirar o confinamento
das ferramentas existentes.

## Âmbito inicial e APIs

| Proteção | Consulta e limite | Alteração proposta |
| --- | --- | --- |
| Antivírus em tempo real | `Get-MpComputerStatus`; disponibilidade, modo e `RealTimeProtectionEnabled` observados | Capacidade administrativa própria, com opções fixas do Defender e leitura posterior; primeiro alvo candidato |
| Avisos sobre aplicações e ficheiros | SmartScreen de aplicações/ficheiros; distinguir de Edge e Store | Controlos oficiais da Segurança do Windows; não inferir estado efetivo só de uma chave de registo |
| Controlo Inteligente de Aplicações | Disponibilidade, versão e modo observados; avaliação não equivale a ligado | Controlos oficiais da Segurança do Windows; disponibilidade de reativação tem de ser verificada no dispositivo |

Proteção contra alterações: observar como condicionante da operação. Este contrato
não autoriza desativá-la, contorná-la, acrescentar exclusões, parar serviços ou
alterar outras proteções. Firewall, BitLocker e gestão remota ficam fora do âmbito.

A FAQ atual da Microsoft permite reativação do Controlo Inteligente sem instalação
limpa em dispositivos/atualizações compatíveis. A página geral de controlo de
aplicações ainda contém a restrição antiga. Esta divergência impede assumir
reversibilidade universal; não reinstalar/resetar o PC, alterar modo S ou ativar
dados de diagnóstico para resolver indisponibilidade sem novo pedido humano.

`Set-MpPreference` documenta o controlo da proteção em tempo real. A existência do
cmdlet não prova que uma alteração seja permitida: a proteção contra alterações
pode bloqueá-la mesmo quando o comando parece ter tido sucesso. Voltar a ler o
estado efetivo é obrigatório.

## Interface de uma única operação

Entrada proposta: proteção da lista delimitada, ação `consultar`, `ativar` ou
`desativar`, motivo, evidência de risco quando exista e estado/versão observados.
Pedidos compostos, scripts, comandos livres, nomes de serviços/chaves arbitrários,
IDs de outras proteções e argumentos remotos são recusados.

1. Receber o pedido na Folha e identificar uma capacidade registada.
2. Consultar o estado por interface suportada, sem alterar configuração. Falha de
   consulta devolve `UNKNOWN`; ausência de serviço não equivale a proteção desligada.
3. Apresentar proposta com proteção exata, estado anterior, estado pedido, motivo,
   consequências e possibilidade de recuperação verificada. Um alerta suspende o
   trabalho relevante e fundamenta a proposta; não concede aprovação automática.
4. Obter confirmação humana ligada ao pedido, alvo, estado observado, versão,
   implementação e sessão, com ticket de utilização única e validade limitada.
   Recusa, edição, expiração, ticket antigo ou reutilizado impedem a alteração.
5. O Host valida a confirmação antes de despachar uma operação administrativa
   delimitada. A autorização administrativa nativa do Windows continua obrigatória
   quando aplicável; a Folha não a substitui nem a oculta. IA, MCP e a ferramenta
   não aprovam nem elevam permissões por si.
6. Ler novamente o estado e verificar o alvo. O estado final pedido tem de estar
   efetivamente observado para declarar sucesso. Recusa UAC/política, proteção
   contra alterações ou indisponibilidade não têm fallback para outra proteção.
7. O Host regista resultado, decisão e evidência no fluxo existente. A eventual
   promoção do relatório para Canonical mantém a decisão humana separada; não é
   autorização retroativa de uma alteração do Windows.

O estado persistido antes da chamada administrativa impede que recuperação ou
reinício repitam uma alteração. Timeout, crash ou resposta perdida após despacho
devolvem resultado desconhecido; consultar o estado/histórico e reconciliar sem
novo despacho automático. Uma nova ação exige nova decisão.

Desativação deve mostrar o aumento de exposição e o plano de reativação. Este
contrato não promete restauro automático: reativação é outra ação autorizada, e a
sua disponibilidade tem de ser demonstrada antes de apresentar a operação como
temporária ou reversível.

## Evidência e critérios observáveis

Registo mínimo: fonte/versão da observação, pedido e impressão digital, proteção,
ação, estado anterior, decisão humana, instante de despacho, resposta recebida,
estado posterior observado e ligação ao run original. Não guardar credenciais.
Resultado distingue recusa antes do despacho, falha confirmada, mudança confirmada
e resultado desconhecido. Nenhum timeout ou código de saída sozinho prova que
nada foi alterado.

| Gate | Critério de PASS | Estado nesta proposta |
| --- | --- | --- |
| Fronteira existente | Pedidos de proteções não registados são recusados por HTTP e contrato, sem runs/Creative/Canonical | A testar contra o Host original |
| Integridade | Kernel/Host/Store, políticas, schemas, adapters e os 40 hashes da base intactos | A reconferir |
| Consulta Windows | Observação por API suportada, limites de tempo, indisponibilidade e dados inválidos | NOT RUN |
| Recusa da alteração | Sem confirmação/UAC válida, estado Windows permanece igual | NOT RUN |
| Alteração permitida | Windows descartável, antes/depois reais e registo pela autoridade original | NOT RUN |
| Proteção contra alterações | Tentativa bloqueada não produz falso sucesso | NOT RUN |
| Recuperação | Perda de resposta, timeout, edição, expiração, reinício e replay não repetem alterações | NOT RUN |
| PC de Pedro | Consulta e alteração do alvo específico no PC, com consentimento aplicável | NOT RUN |

PASS de recusa prova que o controlo ainda não está disponível. Não prova consulta,
elevação, ativação ou desativação. Não aplicar mudanças de segurança a um runner
partilhado para fabricar prova positiva; usar Windows descartável delimitado para
esse gate.

## Extensão necessária para implementar

A regra de núcleo intacto não permite acrescentar silenciosamente o processo às
listas fechadas nem uma exceção administrativa ao Host. É necessária decisão
humana específica sobre esse âmbito antes de implementar a alteração efetiva.

Proposta de âmbito para essa decisão: um único processo `windows_protection`,
primeiro só proteção em tempo real; mudanças declarativas coerentes em
`contracts.py`, `schemas/request.json`, `laws/policy.json` e `capability_router.py`;
dispatch/fingerprint no runner; exceção administrativa mínima no Host com comando
fixo, consentimento nativo e verificação posterior; integridade atualizada para os
bytes revistos. Store, leis, promoção, replay e restantes ferramentas conservam a
lógica atual. Nenhuma alteração desse âmbito está aplicada por este documento.

SmartScreen e Controlo Inteligente seguem em microfases posteriores com métodos
suportados próprios; não são aliases de um interruptor genérico do Defender.

## Fontes e código verificados

- [Get-MpComputerStatus](https://learn.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=windowsserver2025-ps).
- [Set-MpPreference](https://learn.microsoft.com/en-us/powershell/module/defender/set-mppreference?view=windowsserver2025-ps).
- [Proteção contra alterações](https://learn.microsoft.com/en-us/defender-endpoint/tamper-protection-overview).
- [Controlos de aplicações/navegador](https://support.microsoft.com/en-us/windows/security/windows-security/app-browser-control-in-the-windows-security-app).
- [FAQ atual do Controlo Inteligente](https://support.microsoft.com/en-us/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).
- Código da base: `contracts.py`, `schemas/request.json`, `laws/policy.json`,
  `capability_router.py`, `app.py`, `approval_binding.py`, `host.py`,
  `windows_sandbox.py` e `adapters/runner.py`.
