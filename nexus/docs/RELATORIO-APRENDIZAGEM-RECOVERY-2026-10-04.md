# Relatório de aprendizagem — recovery, proveniência e testes

Data: 2026-10-04
Branch: `work/audit-bidirectional-20261004`
Escopo: revisão do trabalho Work/Codex na PR #8. Este documento não altera leis nem arquitetura.

## Baseline verificada

HEAD revisto antes deste relatório: `dcc3b98d375e0dc2dd4430669af9623d9f46e3f2`.

GitHub Actions Windows:
- run `37200783954`: SUCCESS;
- **1215 passed in 32.93s**;
- `NEXUS PASS | COMPLETE`;
- `POWERSHELL_WRAPPER=PASS`.

A execução Windows do GitHub não substitui o futuro teste em `C:\Nexus-Lab`.

## Como o Work/Codex resolveu os problemas

### 1. T01 — crash depois de output externo durável

FAIL inicial:
- o executor já tinha produzido `execution.stdout.json`;
- o Kernel caiu antes de `Store.accept`;
- restart degradava a operação para FAIL.

Solução aplicada:
- fixar `workflow_sha256` no estado no momento de criação do pedido;
- no restart, validar o envelope durável;
- conferir que o workflow atual tem exatamente o hash fixado;
- chamar a aceitação do resultado guardado sem reexecutar Conductor;
- manter Canonical vazio;
- resultado regressa a `HUMAN_REQUIRED`.

Aprendizagem:
> Resultado externo durável não deve ser descartado nem refeito. Primeiro verificar identidade, versão e integridade; só depois reconciliar.

### 2. T03 — crash depois de Creative, antes da atualização do estado

FAIL inicial:
- Creative podia já estar totalmente escrito;
- state continuava RUNNING;
- restart não reconhecia corretamente o pacote completo.

Solução aplicada:
- tornar `Store.accept` idempotente perante Creative já existente;
- validar conteúdo, result, provenance e hashes;
- se tudo corresponde ao resultado esperado, completar a transição;
- se Creative estiver incompleto/adulterado, conservar bytes e bloquear;
- nunca reparar silenciosamente evidência danificada.

Aprendizagem:
> Idempotência não significa sobrescrever. Significa reconhecer o mesmo estado comprovado e recusar divergência.

### 3. Binding resultado ↔ workflow

FAIL reproduzido:
- `Store.accept` aceitava trace não ligado ao workflow fixado.

Solução:
- `workflow_sha256` faz parte do estado;
- trace tem de apresentar o mesmo hash;
- divergência é BLOCKED.

Aprendizagem:
> Proveniência deve ligar output não só ao input, mas também à versão exata do processo que o produziu.

### 4. Human Gate

Testes acrescentados:
- sessão errada não consome ticket válido;
- ticket de um run não aprova outro;
- ticket pendente não sobrevive ao restart;
- conteúdo alterado depois de review continua bloqueado.

Aprendizagem:
> Aprovação é uma capacidade curta e ligada simultaneamente a sessão, run, conteúdo e momento. Nunca é uma autorização genérica.

### 5. Matriz determinística de 100 000 casos

Distribuição:
- 50 000 comparação A↔B;
- 30 000 binding de decisão humana;
- 20 000 JSON estrito/roundtrip;
- seed fixa e casos reproduzíveis.

Aprendizagem:
> Escala massiva deve testar contratos baratos e determinísticos. E2E pesado fica numa amostra menor.

## Padrão reutilizável aprovado

Para qualquer novo microprocesso:

1. persistir intenção/versão antes da ação externa;
2. conservar input original;
3. executar capability como componente descartável;
4. persistir output bruto antes da interpretação/promoção;
5. ligar output a workflow/configuração por hash;
6. tornar a ingestão/reconciliação idempotente;
7. em divergência, preservar e bloquear;
8. nunca fabricar Human Gate;
9. nunca repetir ferramenta apenas para reconstruir o passado;
10. testar ida, volta, crash, adulteração e restart.

## Próximo buraco identificado — execução em curso sem resultado durável

Estado atual:
- pedido nasce `RUNNING`;
- workflow já é fixado por hash;
- Host lança o subprocesso;
- se o processo Kernel morrer enquanto a capability está em curso e ainda não existir `execution.stdout.json`, o restart não distingue:
  - crash antes de iniciar capacidade externa;
  - crash depois de capacidade externa ter começado.

Para capacidades futuras de Windows/homelab com efeitos externos, essa ambiguidade é relevante.

Contrato a testar, antes de corrigir:
- `PREPARED`: pedido persistido, capability ainda não iniciada;
- `EXECUTING`: Kernel persistiu que vai entrar na capacidade externa antes do spawn;
- restart de `EXECUTING` sem resultado durável -> `BLOCKED / RECOVERY_REQUIRED`, sem retry automático e sem Canonical;
- restart de `PREPARED` pode ser tratado separadamente conforme idempotência/política.

Isto é extensão do contrato já decidido de checkpoints Kernel-owned; não dá persistência ao Conductor e não altera a arquitetura.

## Estado de aprendizagem

Os padrões acima passam a ser referência para os próximos microprocessos. Não repetir soluções já provadas; reutilizar o contrato e variar apenas a capability específica.


## T03B — crash durante capability externa sem resultado durável

### FAIL reproduzido
Windows run `37201693913`:
- `1 failed, 1215 passed`;
- teste: `test_restart_after_kernel_dies_during_executor_is_recovery_required`;
- observado: `execution_phase == None` no momento de entrada no executor.

Causa:
- o Kernel fixava input e workflow, mas não persistia uma fronteira entre pedido apenas preparado e capability externa já iniciada.

### Correção mínima
- `Store.create` grava `execution_phase=PREPARED`;
- imediatamente antes de `subprocess.Popen`, o Host grava atomicamente `execution_phase=EXECUTING`;
- restart de `RUNNING + EXECUTING` sem `execution.stdout.json` passa para:
  - `BLOCKED`;
  - `commit_status=RECOVERY_REQUIRED`;
  - sem retry automático;
  - sem Canonical;
  - input conservado;
- `PREPARED` sem resultado mantém o comportamento anterior de interrupção antes de execução externa.

### PASS após correção
Windows run `37202001479`:
- **1216 passed in 64.51s**;
- `NEXUS PASS | COMPLETE`;
- `POWERSHELL_WRAPPER=PASS`;
- auditoria GitHub também SUCCESS.

### Aprendizagem
> Antes de qualquer ação externa, o Kernel deve persistir uma fronteira de execução. Em resultado incerto, segurança significa conservar a incerteza e bloquear, não repetir automaticamente nem declarar um FAIL simplificado.

Isto prepara o Nexus para capacidades futuras Windows/homelab com efeitos externos sem dar memória ou autoridade ao Conductor.
