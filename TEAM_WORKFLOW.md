# Trabalho e ferramentas do GitHub

Pedro define finalidade, arquitetura e decisões normativas. Codex cruza documentação, audita e testa. Copilot/Cline/Cursor podem escrever uma microtarefa fechada; não assumir acesso ao repositório nem delegar desenho por falta de contexto.

## GitHub usado neste processo

- Commits e histórico: versões reversíveis e proveniência das alterações.
- Pull requests: revisão do conjunto alterado, âmbito, testes e limitações; modelo em .github/pull_request_template.md.
- Actions: verificar links/hashes e reproduzir os testes fornecidos num runner Linux, sem segredos. Não declara PASS dos IMP nem aprovação humana do produto.
- Issues: registar lacunas e falhas específicas, com requisito, evidência e critério de fecho. Modelo de microprocesso incluído.

A passagem de um IMP exige contrato + testes necessários + evidência + revisão, não apenas um check verde. A reconciliação documental não permite avançar a programação de IMP posteriores.

Branch protection, regras de revisão obrigatória, Projects, Wiki, Copilot e funcionalidades dependentes de plano/permissões não foram ativadas nem presumidas. Não criar notificações ou integrações externas sem necessidade. Actions fica limitado a uma tarefa Linux por execução, timeout de cinco minutos, permissões de leitura e sem cron. O runtime do produto continua local-first; o CI só testa código com dados artificiais.
