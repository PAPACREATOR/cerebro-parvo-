# ADR — preservar histórico, isolar equipas e documentar sem tocar no código

Data: 10-10-2026. Estado: **regra de trabalho desta frente documental**.

**Decisão humana nesta frente:** nunca alterar código. Esta branch é exclusivamente documental; não edita testes, scripts, configurações executáveis, Kernel, Host, Store, UI, instalação ou workflows. Não faz merge em main.

**Porquê:** há frentes simultâneas. A PR #41 é de navegação e documentos operacionais; a #46 é auditoria e privacidade; a #48 é inventário/clones; a #43/#45 são implementação candidata; outros laboratórios conservam âmbitos próprios. Editar por cima de outra frente cria conflitos e compromete comparações por SHA.

**Histórico:** conservar versões anteriores, inclusive decisões erradas, hipóteses abandonadas, logs FAIL e créditos externos. Em vez de renomear/mover originais indiscriminadamente, usar índices por época e decisão, com links estáveis. Uma limpeza física exige manifesto, verificação de referências e backup/restauro testado.

**Exceções não presumidas:** documentação aqui não prova segurança integral, cópia total do PC nem conclusão de fases. A integração Sandy está suspensa por decisão humana; os estudos e o crédito de Hrvoje Abraham não são eliminados. Clonar Sir Thaddeus em Linux não prova execução/instalação no Windows.

Fontes: [PR #41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41), [PR #46](https://github.com/PAPACREATOR/cerebro-parvo-/pull/46), [PR #48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48), [história](../99-history/README.md).