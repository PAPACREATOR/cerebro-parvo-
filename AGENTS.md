# Instruções obrigatórias para agentes

Projeto: Cérebro Independente
Autor e Gatekeeper: Pedro Alexandre Caldas Coelho

## Antes de qualquer alteração

1. Ler `CEREBRO_CONSTITUTION.md`.
2. Ler `CEREBRO_ARCHITECTURE.md`, `DECISIONS.md` e `STATUS.md`.
3. Abrir apenas a SPEC indicada em `STATUS.md`.
4. Se não existir uma SPEC ativa e fechada, não programar.

## Regras de execução

- Executar uma única SPEC por vez.
- Fluxo: SPEC → implementação mínima → testes → resultados → atualização de estado → parar.
- Não iniciar a tarefa seguinte, não fazer commit e não mudar arquitetura sem autorização.
- Nunca esconder, apagar, enfraquecer ou ignorar testes falhados.
- Registar em `STATUS.md` os comandos, códigos de saída e contagens reais.
- Aplicar `USE > ADAPT > CREATE`; código próprio é a menor categoria.
- Quando houver conflito estrutural, parar e apresentar evidência, impacto e alteração mínima.

## Limites arquitetónicos

- Nome atual: Cérebro Independente. Nexus e LocalNest são nomes históricos.
- Logseq não é substituído por Obsidian.
- Activepieces não é substituído por n8n.
- Cofre criativo nativo do Logseq e cofre final permanecem separados. O final contém Markdown gerido pelo sistema e **SQLite interno vivo**; existe **um segundo SQLite espelhado**. Não fundir as duas bases nem tratar o interno como cache descartável. A v0.1 `vault.db` como cofre único é histórica.
- O utilizador escreve normalmente no Logseq: não exigir input Markdown/YAML/SQL nem reconstruir nativamente blocos, páginas, links, tarefas ou queries do Logseq.
- Nenhuma entrada no cofre final sem aprovação expressa de Pedro ligada ao item e à sua versão; não apagar automaticamente do criativo após promoção.
- IA é opcional, efémera e sem capacidades permanentes.
- Fontes externas e IA nunca escrevem diretamente no Final Vault.
- Replay, auditoria, proveniência, human gate e idempotência não podem ser removidos.

## Segurança e confidencialidade

- Nunca ler ou enviar `fontes/`, `juridico/`, `documentacao/` ou `MEMORIA-DE-TRABALHO.md` durante programação normal.
- Nunca mostrar, guardar ou commitar chaves, tokens, passwords ou dados de pagamento.
- Não ativar faturação adicional, on-demand usage, MCP, serviços cloud ou publicação.
- Não executar comandos destrutivos.
- Pedir aprovação antes de instalar dependências ou usar rede.

## Paragem obrigatória

No fim da SPEC, apresentar ficheiros alterados, testes executados, resultados PASS/FAIL, riscos e trabalho restante. Depois parar e aguardar revisão do Codex e decisão de Pedro.
