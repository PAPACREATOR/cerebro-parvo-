# 10/10/2026 — Sir Thaddeus × Folha Nexus: seleção de mecanismos, não clonagem de arquitetura

**Escopo:** comparação de código e contratos, não prova de instalação local. Origem Sir Thaddeus: [raydeStar/sir-thaddeus](https://github.com/raydeStar/sir-thaddeus) no commit `974b5d7d258a687f99062425ef40e54b1eefc034`, clonado integralmente em Linux e auditado byte a byte no dossier da PR [#48](https://github.com/PAPACREATOR/cerebro-parvo-/pull/48). Candidato Nexus antes da integração: [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45), `66027af7f2ea084bc62d85b840d1fc3113e60a97`. Trabalho isolado nesta [PR #50](https://github.com/PAPACREATOR/cerebro-parvo-/pull/50).

## O que foi examinado

- `sir-thaddeus/README.md`: local-first, decisões de execução configuráveis **Off / Ask / Always**, recibos, fontes, memória local.
- `src/Thaddeus.Runtime/Api/WorkspaceHostingExtensions.cs`: interface entregue no loopback, autenticação de sessão, cache de bootstrap desativada.
- `web/src/components/ChatComposer.tsx`, `PlanApprovalCard.tsx`, `ProvenanceChip.tsx`, `WorkReceipt.tsx`: fronteira visível entre escrever, confirmar e consultar provas, sem tratar a aprovação visual como autoridade do runtime.
- Folha Lab PRs [#4](https://github.com/PAPACREATOR/nexus-folha-lab/pull/4) e [#5](https://github.com/PAPACREATOR/nexus-folha-lab/pull/5): revisão de edição monotónica e guarda `Host/Origin`. A bancada é `SIMULATED_ONLY`, não um serviço produtivo.

## Matriz de decisão — USE > ADAPT > CREATE

| Mecanismo | Sir Thaddeus / Folha Lab | Nexus nesta candidata |
| --- | --- | --- |
| Interface centrada na escrita | SPA React com superfícies de chat/wiki e composição; bancada Folha HTML reduzido | **Adaptado:** substituído `nexus/ui/index.html` e `style.css` por **uma única folha simples**, sem introduzir React/Vite/.NET |
| Confirmação antes de execução | Política explícita por capacidade e decisão visível | **Preservado:** `/api/prepare-run` e `/api/confirm-run` com ticket de operação associado ao pedido; sem opções `Always` que retirem aprovação humana |
| Aprovação de conhecimento | No Thaddeus, ferramentas e wiki têm portões por operação | **Preservado:** outro ticket e decisão humana para Creative→Canonical; confirmação de execução não promove conteúdo |
| Revisões enquanto HTTP está pendente | Folha Lab PR #4 invalida mesmo se texto alterado e reposto | **Integrado:** revisão monotónica de texto/anexo no `nexus/ui/app.js`; resposta tardia não abre diálogo antigo |
| HTTP Host/Origin | Folha Lab PR #5 protege serviço loopback | **Já existia:** `nexus/app.py` exige Host e Origin esperados antes da interpretação e de ferramentas; não copiar segundo servidor |
| Várias intenções | Thaddeus tem capacidades e permissões próprias | **Read-only:** Folha reconhece sete prefixos e expressões com `/api/interpret`; devolve `execution: NOT_AUTHORIZED`, sem criar runs nem escrita |
| Ferramenta ativa | Thaddeus tem MCP e runtime com modelos | **Sem fusão:** só `verify` com anexo alcança o gate natural nesta versão; modelos/MCP/NET não são requisitos |
| Proveniência | Thaddeus apresenta recibos e atividade | **Preservado:** resultados verificados, hashes e origem no Store e no histórico; UI não constrói proveniência |
| Interrupção/limites | Runtime Thaddeus tem stop/kills | **Preservado:** limites Job/LPAC no Host, sem transferir controlo para UI ou Thaddeus |

## O que foi removido/substituído

Os ficheiros anteriores `nexus/ui/index.html` e `nexus/ui/style.css` foram substituídos **no mesmo caminho**, para que o Host continue a servir só uma Folha. Não há dois servidores de UI nem dois Kernels. O Git preserva os blobs antigos para auditoria e rollback. O `nexus/ui/app.js` conserva o contrato seguro do Host (visualização de runs, Creative, PDF e Human Gate) e acrescenta interpretação sem execução.

## Gates obrigatórios

1. Manifesto `nexus/integrity.json` com SHA-256 dos bytes efetivos, nunca desativado.
2. Parse JavaScript, cinco corridas adversariais de revisão e testes HTTP de interpretação de sete intenções sem efeitos.
3. Recusas de entrada ambígua/maliciosa e acesso `Host/Origin` inesperado.
4. Verificação real Windows de `verify` pela Folha, confirmação humana, Creative, promoção humana e recuperação; **não** inferir PASS de scripts sintéticos.
5. Writer/LPAC `book` e `convert_pdf` apenas se testes físicos sob o Host da candidata PASS no mesmo SHA; a prova da bancada [Writer Lab #3](https://github.com/PAPACREATOR/nexus-writer-lab/pull/3) não substitui estes gates.

**Estado:** código da UI proposto na PR #50 Draft; CI e integração física são observações por SHA. Sem merge, sem alteração da main, sem eliminação do histórico, sem motor de IA obrigatório e sem autonomia de ferramentas.
