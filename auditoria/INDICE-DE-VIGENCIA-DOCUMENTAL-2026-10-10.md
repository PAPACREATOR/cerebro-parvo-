# Índice de vigência documental — Nexus (revisão parcial de 2026-10-10)

> Este índice organiza **apenas os documentos efetivamente lidos** nesta revisão. Não é inventário integral do PC, do GitHub nem aprovação de código. Os documentos históricos continuam intactos; a classificação descreve a sua validade para novas decisões.

## Hierarquia usada

1. Instrução humana explícita mais recente, sem alterar retroativamente o histórico.
2. Invariantes de autoridade humana, Kernel/Host, proveniência, Creative/Canonical, integridade, recuperação e segurança.
3. Decisões arquiteturais datadas que ainda não foram substituídas.
4. Contratos/testes que comprovam comportamento; só PASS comprovado permite declarar integração.
5. Documentos antigos como genealogia e contexto, não como instruções de instalação.

## Documentos conferidos

| Caminho | Estatuto para novas decisões | Justificação / cautela |
| --- | --- | --- |
| `README.md` | ENTRADA CONCEPTUAL | Apresenta Nexus Minimal, Folha, Conductor candidato e memória soberana; não prova E2E. |
| `AGENTS.md` | INSTRUÇÕES COM RESSALVA | Invariantes e metodologia válidos; frases sobre Activepieces como executor são anteriores à decisão de 30/09, identificadas apenas na auditoria da PR #46; a redação da raiz foi restaurada e deve ser reconciliada na PR #41. |
| `DECISIONS.md` | REFERÊNCIA DE PRECEDÊNCIA | Regista Nexus Minimal de 30/09, Activepieces superado como requisito nuclear, Conductor ainda candidato. |
| `STATUS.md` | RETRATO HISTÓRICO/MISTO | Estado cronológico, com provas e pendências datadas; não confundir PASS localizado com release. |
| `CEREBRO_CONSTITUTION.md` | INVARIANTES VÁLIDAS; STACK HISTÓRICA | Autoridade humana e demais leis mantidas; secção de implementação Activepieces precisa ser interpretada à luz de 30/09. |
| `CEREBRO_ARCHITECTURE.md` | IMPLEMENTAÇÃO HISTÓRICA | Diagrama Activepieces+Memory Provider está superado; invariantes e critérios de desacoplamento mantêm valor. |
| `IMPLEMENTATION_PLAN.md` | PLANO HISTÓRICO | Dois blocos Activepieces+Memory Provider já não são a composição escolhida; mantido intacto na PR #46, com estatuto histórico declarado neste índice, sem reescrever a origem. |
| `SECURITY.md` | POLÍTICA DE SEGURANÇA | Proibições e reporte permanecem; ameaça «via Activepieces/MCP» representa cenário histórico/possível, não obrigação de instalar Activepieces. |
| `docs/PROJETO-FINAL-AUDITADO-2026-09-28.md` | ARQUITETURA HISTÓRICA | O título «final» diz respeito à proposta de 28/09, substituída pela simplificação de 30/09; preservar, não executar como receita vigente. |
| `docs/PENDENCIAS.md` | MATRIZ HISTÓRICA DE 28/09 | P01–P04 e P11 pressupõem Activepieces/Memory Provider; portas comportamentais podem continuar úteis, mas requerem reexpressão no Nexus atual. |
| `docs/RECONCILIACAO.md` | RECONCILIAÇÃO HISTÓRICA DE 27/09 | Não prevalece sobre `DECISIONS.md` de 30/09; genealogia e justificações preservadas. |
| `docs/GENEALOGIA.md` | HISTÓRICO | Compara decisões até 27/09; não contém por si só arquitetura completa atual. |
| `docs/INVENTARIO-HISTORICO.md` | INVENTÁRIO HISTÓRICO | Declara 35 blobs preservados de 24/09; não certifica cópia integral do PC. |
| `nexus/docs/ORGANIZACAO-E-FASES.md` | RETRATO DE INSTALAÇÃO 01/10 | Inventário de instalações e ensaios daquela data; não valida o Windows em 10/10 sem nova execução. |
| `auditoria/CONSOLIDACAO-2026-10-10.md` | DOCUMENTO DE AUDITORIA | Regista divergências e crédito a Hrvoje Abraham. Integração Sandy explicitamente suspensa por decisão humana de 10/10. |
| `auditoria/FASE-1-INVENTARIO-DOCUMENTAL-2026-10-10.md` | CHECKLIST ATIVA FASE 1 | O âmbito desta PR é exclusivamente documental; fecho condicionado a evidência verificável. |

**Isolamento editorial:** a PR #46 restaurou os quatro documentos da raiz (`AGENTS.md`, `CEREBRO_CONSTITUTION.md`, `CEREBRO_ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`) à versão exata de `main`. As alterações propostas pela PR #41 continuam exclusivamente na respetiva branch. Esta PR acrescenta apenas ficheiros em `auditoria/`.

## História integral até 10-10-2026

- [História comentada e cronologia com fontes](HISTORIA-COMENTADA-NEXUS-2026-10-10.md): explica decisões de 22/09–10/10, motivos da substituição de Logseq/Joplin, Activepieces/Conductor/Spiff, evolução da Folha, wiki, MCP e Windows; distingue proposta, implementação numa branch, PASS limitado e entrega.
- Complementa `docs/GENEALOGIA.md` (que termina em 27/09), **sem reescrever o arquivo original ou assumir como vigentes as escolhas antigas**.
- A referência em falta à memória histórica reservada é explicitamente assinalada, sem republicar ficheiros excluídos pelo `.gitignore`.

## Atualização: documentação em revisão noutras PRs

Esta classificação lê o `main` original e é **provisória**. A [PR #41](https://github.com/PAPACREATOR/cerebro-parvo-/pull/41), ainda aberta, contém propostas documentais datadas de 05/10–09/10 e um novo `docs/20-architecture/MINIMUM-CORE.md` que já não considera Conductor uma dependência candidata. A formulação nessa PR é **Folha/parser + Kernel/Host/Store + regras/schemas + MCP Python/adaptadores + ferramentas externas**, sem Activepieces e sem Conductor como requisitos. A issue [#33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33) exige ainda convergência do runtime e testes num único SHA. Não equiparar a proposta aberta à branch principal aprovada; confrontar ambas quando houver HEAD definitivo.

A [auditoria estática das ligações e duplicações](AUDITORIA-LINKS-DUPLICADOS-2026-10-10.md) identificou uma referência histórica para `MEMORIA-DE-TRABALHO.md` ausente da árvore atual, e dois pares de blobs idênticos preservados em versões distintas.

## Decisões de organização que podem ser tomadas agora

- Não promover títulos como «final», «auditado», «vigente» ou «PASS» para estado atual sem considerar a data e a evidência.
- Preferir `DECISIONS.md` de 30/09 para o estatuto histórico de Activepieces; o texto antigo pode ser mantido com aviso, não apagado.
- Separar documentação operacional atual, snapshots testados e material de pesquisa/histórico.
- Manter o crédito a Hrvoje Abraham e a origem do Sandy; **sem qualquer tarefa de integração Sandy ativa**.
- Codex é responsável por comparar e subir o espelho local; este índice não substitui o manifesto/hash do PC.
- Não modificar Kernel, Host ou mecanismos executáveis com base apenas nesta classificação.

## Pendências de fecho do inventário

- Árvore completa do repositório e branches com commits; distinguir código de documentação e laboratórios.
- Auditoria de links e anexos; referências a ficheiros locais que não estejam no GitHub.
- Conferência de documentos e hashes do espelho após entrega Codex.
- Revisão de segredos/ficheiros pessoais antes de qualquer publicitação.
- Ler documentação recente da integração PR #43/#45 e da organização PR #41 antes de consolidar índice definitivo.

**Estado:** ÍNDICE PARCIAL, sem validação do espelho local nem da execução Windows.
