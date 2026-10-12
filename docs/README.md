# Documentação interna do Nexus

Esta pasta contém a documentação para desenvolvimento, planeamento e manutenção. A porta de entrada pública do projeto é o [README principal](../README.md).

## Começar aqui

1. Leia o [estado operacional](../nexus/docs/PONTO-DE-SITUACAO.md) para SHA, provas, falhas e pendências.
2. Leia as [instruções de trabalho](internal/AGENTS.md).
3. Consulte a [Constituição](architecture/CEREBRO_CONSTITUTION.md), a [arquitetura](architecture/CEREBRO_ARCHITECTURE.md) e as [decisões](architecture/DECISIONS.md).
4. Consulte o contrato específico da tarefa antes de editar.

## Navegação

- [Arquitetura, constituição e decisões](architecture/) — princípios vigentes e genealogia.
- [Planeamento, instalação, compatibilidade e estado](planning/) — planos e matrizes de trabalho.
- [Fluxo de trabalho, agentes e regras internas](internal/) — como trabalhar sem duplicar responsabilidades.
- [Estado operacional do Nexus](../nexus/docs/PONTO-DE-SITUACAO.md) — fonte operacional única para evidência por SHA.
- [Documentação do runtime Nexus](../nexus/README.md) — arranque, capacidades, limites e testes.
- [Auditoria e inventários](../auditoria/) — verificações, preservação e evidência documental.
- [Tarefas](../tasks/) — trabalho e critérios de aceitação.
- [Genealogia](GENEALOGIA.md) — evolução, decisões substituídas e contexto histórico.
- [Inventário histórico](INVENTARIO-HISTORICO.md) — mapas de documentos e fontes antigas.
- [Reconciliação datada de 27/09](RECONCILIACAO.md) — registo histórico; não substitui instruções vigentes.
- [Pendências](PENDENCIAS.md) — trabalho por fechar.
- [Histórico](../historico/) — materiais anteriores preservados.

## Regras

- A raiz do repositório é a montra pública; esta pasta é para quem desenvolve, mantém ou contribui.
- O estado operacional é `nexus/docs/PONTO-DE-SITUACAO.md`; não criar novos ficheiros de estado por sessão.
- PASS só conta com evidência no mesmo SHA; FAIL, BLOCKED, UNKNOWN e NOT RUN não se transformam em PASS.
- Histórico, decisões antigas e evidência de falhas são preservados; não apagar por parecer redundante.
- Antes de editar, conferir `main`, branch, PRs abertas e comentários recentes.

## PRs documentais abertas

As PRs #41, #49, #54 e #56 contêm propostas documentais ainda não integradas. Comparar o respetivo diff e base antes de reutilizar, substituir ou fundir trabalho. Não as tratar como estado atual.