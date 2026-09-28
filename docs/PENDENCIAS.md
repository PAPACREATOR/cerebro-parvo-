# Pendências e portões — 28-09-2026

A arquitetura está fechada em composição mínima. As pendências são agora provas de ligação e comportamento, não módulos a programar.

| ID | Lacuna | Fecho mínimo |
| --- | --- | --- |
| P01 | Vertical slice Activepieces | WebUI -> regras/tabelas -> capacidade -> Creative -> Human Gate -> Canonical |
| P02 | 3 memórias | Provar Working, Behavioral/Procedural e Persistent Knowledge sem criar três sistemas |
| P03 | 3 comparadores | Provar determinístico, relacional e semântico com providers separados e cruzamento no flow |
| P04 | Open Notebook + tiny | Um espaço reutilizável, agente único parametrizado, duas áreas temáticas, saída UNTRUSTED |
| P05 | Knowledge governance | Testar K-DLC como provider sem lhe conceder autoridade sobre as leis do Cérebro |
| P06 | Pesquisa/indexação | Usar primeiro capacidades existentes; SQLite/FTS próprio só se houver lacuna demonstrada |
| P07 | Documentos/fontes | Ligar Zotero e LibreOffice por Piece/MCP/API/CLI, sem obrigar o utilizador a trocar de interface |
| P08 | Multimédia local | Ligar Pinokio/provider local para imagem e, depois, áudio/música |
| P09 | Recovery/backup | Provar restart, divergência, backup e restore com a composição real |
| P10 | Windows/UX | Uso no PC alvo através de uma experiência principal Activepieces, sem Markdown/SQL/IDs visíveis |
| P11 | Terceiros | Fixar versão/licença/origem apenas dos providers realmente usados |
| P12 | Visibilidade pública | Alterar manualmente a visibilidade do repositório quando pretendido |
| P13 | Eliminação | Continua fora do MVP até existir política humana específica |

## Fallback preservado

O writer recuperável e a implementação Python já existentes ficam preservados. Não são apagados nem obrigatórios. Servem como fallback apenas se a composição provar que uma capacidade madura não fecha uma regra essencial.

## Critério de decisão

Antes de qualquer código novo perguntar, por ordem:

1. já existe Piece?
2. já existe MCP/API/CLI?
3. Activepieces Tables/Storage/flow já resolve?
4. um provider maduro já resolve?
5. apenas se todas falharem: adaptar ou criar o mínimo indispensável.

## Regra

**LIGAR > CONFIGURAR > ADAPTAR > CRIAR.**

A simplificação nunca pode retirar:

- autoridade humana;
- 3 memórias;
- Creative/Canonical;
- 3 comparadores;
- proveniência/genealogia/contradições;
- IA sem autoridade;
- recuperação verificável.

[Arquitetura vigente](../CEREBRO_ARCHITECTURE.md) · [Plano](../IMPLEMENTATION_PLAN.md)
