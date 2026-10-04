# Estado de execução e continuidade

Atualização: 04-10-2026. Responsável nesta sessão: Codex.
Branch: nexus-startup-lock-20261003. PR: #7.

| Trabalho | Estado | Evidência / próximo passo |
|---|---|---|
| F011/F012/F013 | Testado no runner Windows | 1194 PASS, run 37162599479, commit 2870e336 |
| Script PowerShell único com relatório | Implementado; teste Windows em curso | nexus/windows/check-nexus.ps1; workflow Nexus Windows |
| Instalação pessoal | A cargo de Pedro | Não bloqueia tarefas do repositório |
| Spiff local / conciliação | Código local indisponível neste repositório | Não substituir nem declarar testado |
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
