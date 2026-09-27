# Cérebro Independente

Arquitetura conceptual fechada: **Folha Única + M1–M14**. Documentação reconciliada em 27-09-2026 com as decisões e fontes de 26-09-2026. Autor da conceção e autoridade final: Pedro Alexandre Caldas Coelho.

A pessoa escreve normalmente numa Folha. O Cérebro preserva, relaciona, pesquisa, compara e executa trabalho autorizado. Markdown, IDs, SQLite, eventos e ferramentas ficam internos. Creative conserva exploração e genealogia; Canonical contém conhecimento atualmente aprovado pela pessoa, sem ser verdade absoluta.

## Começar aqui

1. [Constituição e precedência](CEREBRO_CONSTITUTION.md).
2. [Arquitetura, diagrama e algoritmo](CEREBRO_ARCHITECTURE.md).
3. [Prompt mestre integral](docs/baseline/CEREBRO_PROMPT_MESTRE_CURSOR_2026-09-26.md).
4. [Estado real e evidência](STATUS.md).
5. [Matriz M1–M14 e IMP-001–026](docs/MATRIZ-CONFORMIDADE.md).
6. [Tarefa IMP-001](tasks/IMP-001.md).

## Estado observado

Existe código candidato de 27-09-2026, recuperado do pacote revisto. Os 34 testes fornecidos foram reproduzidos localmente com sucesso. Isto não fecha os 26 IMP nem demonstra M1–M14 ponta-a-ponta. IMP-001 está PARCIAL; IMP-019/G10 e IMP-026 têm bloqueios explícitos POR DEFINIR.

O código foi importado sem alterar os bytes originais. Consulte [âmbito da implementação](implementacao/README.md) e [pendências](docs/PENDENCIAS.md). O estado aprovado do produto não avança por se arquivar ou testar um protótipo posterior.

## Organização

| Local | Conteúdo e autoridade |
| --- | --- |
| Raiz | Orientação corrente, estado e processo |
| docs/baseline | Três fontes de 26/09 preservadas integralmente |
| docs | Genealogia, decisões de reconciliação, matrizes e inventário |
| tasks | Contrato ativo de trabalho |
| implementacao/candidata-2026-09-27 | Código e testes recebidos; candidato parcial |
| auditoria | Hashes, comandos, resultados e cobertura |
| historico/repositorio-2026-09-24 | Todos os 35 ficheiros anteriores, intactos |
| .github | Actions, modelo de pull request e modelo de issue |

[Genealogia e razões das mudanças](docs/GENEALOGIA.md) · [Fontes localizadas](docs/FONTES.md) · [Índice histórico](docs/INVENTARIO-HISTORICO.md) · [Uso do GitHub](TEAM_WORKFLOW.md).

A aprovação dos testes existentes não substitui revisão do contrato. FAIL, SKIP, NOT RUN e resultado ambíguo nunca equivalem a PASS. Nenhuma publicação/licença de distribuição é criada por esta reorganização.

[Abrir no VS Code](docs/VS-CODE.md) · [Licenciamento pendente](docs/LICENCIAMENTO-PENDENTE.md).
