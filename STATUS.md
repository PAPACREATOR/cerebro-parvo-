# Estado atual do Nexus

**Base ativa:** `main` `0e9c89e712b2284af5754831f7ced561b0e92d7d` — merge da PR #72, de 13-10-2026.

A fonte operacional detalhada continua a ser [`nexus/docs/PONTO-DE-SITUACAO.md`](nexus/docs/PONTO-DE-SITUACAO.md).

## Regras que continuam vigentes

- Humano é a autoridade máxima.
- Kernel/Host/Store mantêm estado, política, Creative, Human Gate e Canonical.
- MCP é transporte, não autoridade.
- OpenNotebook, LibreOffice, LanguageTool, Zotero, ACE-Step, Forge e outras integrações são ferramentas externas.
- Tiny/IA é opcional, delimitada e sem autoridade.
- Arquitetura conceptual M1–M14 permanece congelada; implementação e testes não autorizam redesenho implícito.
- Conhecimento Canonical não é eliminado automaticamente salvo duplicação absolutamente exata.
- FAIL, BLOCKED e NOT RUN não contam como PASS.
- Integrado na `main` não equivale a fisicamente validado no PC.

## Já integrado na main

- Grafo verificável ligado à pesquisa FTS5 e à Folha.
- Interpretação natural de documento com confirmação humana.
- Comandos registados sem prefixo até ao gate da Folha.
- Recusas de respostas MCP do OpenNotebook.
- Molde derivado e validação de identidade OpenNotebook, compostos na PR #72.
- Correção da limpeza Windows relativamente a negações temporárias.
- Correção da exclusividade da porta do peer em Windows.

## Ainda não resolvido

- E2E físico completo no PC do utilizador.
- Fecho da validação de identidade nas rotas de produto OpenNotebook: ver PR #73.
- Documento, podcast, música e vídeo como produtos finais provados.
- Pesquisa automática com fontes verificáveis e produção final a partir dessa pesquisa.
- Instalação completa e aceitação física em Windows: PRs #28 e #29.
- Reconciliação documental de PRs históricas, rascunhos e referências desatualizadas.

## Fonte de verdade

Não criar novos ficheiros de “estado”, “continuidade”, “fila” ou “handoff” por sessão.
Atualizar apenas:

1. `nexus/docs/PONTO-DE-SITUACAO.md` para o estado operacional;
2. `STATUS.md` para o resumo da base ativa;
3. relatórios específicos quando houver evidência técnica nova.

O histórico anterior permanece no Git, nas PRs e nas pastas `historico/` e `implementacao/`, sem ser duplicado na árvore ativa.
