# Estado de execução e continuidade

Atualização: 04-10-2026. Responsável nesta sessão: Codex.
Branch: nexus-startup-lock-20261003. PR: #7.

| Trabalho | Estado | Evidência / próximo passo |
|---|---|---|
| F011/F012/F013 | Testado no runner Windows | 1194 PASS, run 37162599479, commit 2870e336 |
| Script PowerShell único com relatório | PASS com Python preparado | 1194 PASS + falha por Python ausente; run 37194297587 |
| Instalação pessoal | A cargo de Pedro | Não bloqueia tarefas do repositório |
| Executor | Conductor no GitHub; equivalência com Spiff local pendente | Handoff do outro GPT no PR #7; aguardar espelho dos ficheiros e reproduzir contratos |
| Wiki relacional / navegação | Por iniciar | F013 cobre validação de pacotes, não navegação completa |

## Regra de continuidade pedida por Pedro
Antes de terminar cada etapa, registar commit, objetivo, ficheiros, resultados,
bloqueios e próximo passo. Não declarar uma tarefa concluída sem evidência.
O executor seguinte deve ler este estado e consultar o PR e Actions mais recentes.
Registar falhas como FAIL e tarefas não executadas como NOT RUN.
Não depender da memória interna de outra sessão.

## Script de verificação
Na raiz desta branch:
```powershell
powershell -NoProfile -File .\nexus\windows\check-nexus.ps1
```
Cria ambiente Python 3.12 separado numa pasta temporária, instala dependências
de teste, verifica manifesto e executa a suite com dados sintéticos.
Apresenta PASS/FAIL e caminho do relatório state.json, logs e JUnit XML.
Pode ser chamado de qualquer diretório usando o caminho completo do script.

Com Python 3.12 já preparado, usar -PythonPath com o executável desse ambiente.
Nesse caso não instala dependências. A ausência de dependências resulta em FAIL.
O relatório não é enviado automaticamente para o GitHub.

Este script verifica e prepara o ambiente de ensaio. As correções de produto
são F011–F013 no código da branch. Não aplica patches cegos a versões divergentes.
Falha de criação do diretório de relatório ou interrupção forçada pode impedir
o relatório final; estado RUNNING não significa PASS.

## Evidência desta entrega
Commit de código: 38df949ff375f99f76d0519a994291a9938838b9.
[Runner Windows / PowerShell 5](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37194297587):
1194 passed in 48.99s. Script devolveu PASS/COMPLETE e criou state.json.
Executável ausente devolveu exit != 0 e FAIL com diagnóstico; teste do wrapper PASS.
Auditoria histórica: SUCCESS, run 37194297574.
O modo de criação automática de venv não foi exercitado neste run; usa-se -PythonPath
preparado pelo runner. Esse modo mantém NOT RUN até teste específico.
A suite inclui ida/retorno F013, fontes danificadas e reinício; não prova todas
as capabilities externas. Próximo passo: validar preparação automática de ambiente
e alargar cobertura bidirecional por capability, um contrato de cada vez.

## Coordenação com o outro GPT — 04/10, 11:13 Lisboa
Lido o [handoff local](https://github.com/PAPACREATOR/cerebro-parvo-/pull/7#issuecomment-5978887095).
Relata adaptador Spiff -> Conductor e dois testes ainda não publicados.
A ausência de Spiff nos 36 ficheiros publicados não demonstra redundância local.
Retirada condicionada à comparação dos mesmos contratos; nenhuma alteração local feita.
Espelho solicitado por branch própria com caminhos relativos, hashes e testes.
O Work continua na branch deste PR; comparar antes de conciliar ficheiros comuns.

Nova ocorrência: [run 37194459860](https://github.com/PAPACREATOR/cerebro-parvo-/actions/runs/37194459860)
teve 1193 PASS e 1 FAIL: test_independent_memories_can_open_together,
ValueError por URL vazia em wait_for_app. Run paralelo 37194461942 passou.
Estado: falha intermitente por investigar; não declarada resolvida.
Próximo microprocesso: reproduzir a leitura durante publicação da URL e corrigir
conforme a causa; depois validar o modo de criação automática do ambiente.
