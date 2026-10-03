# Nexus — ponto de situação revisto

## Revisão do repositório — 04-10-2026

As provas abaixo da instalação Windows são históricas, não uma nova inspeção do PC.
No [PR #7](https://github.com/PAPACREATOR/cerebro-parvo-/pull/7), o arranque único e
o hash no ambiente reduzido passaram numa suite completa de **1154 testes em
Windows do GitHub**. [Arranque](F011-ARRANQUE-UNICO.md) · [Hash](F012-HASH-WINDOWS-ISOLADO.md).

Pedido atual: **resultados ligados, sentido inverso e wikis coerentes**.
[F013](F013-PROVENIENCIA-INVERSA.md) documenta falhas observadas na ligação
Canonical → Creative → evidência/processo → fonte/pedido e a correção.
Regressão aplicável Linux: 1148 PASS; suite Windows da última correção ainda NOT RUN.
Não confundir a prova mínima de proveniência com uma wiki relacional concluída.

Prioridades da instalação mantidas: ligar a conta Nexus ao executor, configurar
Open Notebook/tiny na entrada Nexos, provar restauro e integrar ferramentas por
circuito real. Essas operações exigem acesso à cópia/configuração do PC; este
trabalho atua no repositório e não substitui alterações Spiff/Conductor locais.

## Conclusão
Existe um protótipo parcial funcional. A arquitetura já tem vários circuitos
com prova real; a integração completa e o isolamento de produção continuam
por demonstrar. Não existe uma percentagem de conclusão fundamentada.

## Resultados verificados
| Área | Evidência | Limite |
|---|---|---|
| Regressão | 1136 testes passaram em 32.31 s | Inclui 1000 variantes parametrizadas de contratos; não são 1136 tarefas E2E |
| Instalação | 16 controlos passaram em C:\Nexos | Dependências ainda em várias pastas |
| Folha e Conductor | Arranque, sessão, execução e resultados testados | O Host ainda executa com a identidade humana |
| LanguageTool | Revisão real de português por CLI, sem IA | Não deteta todos os erros linguísticos |
| LibreOffice | ODT→PDF real, descarga e bloqueios testados | DOCX ainda sem prova real nesta revisão |
| Open Notebook/Tiny | 6/6 ensaios sintéticos passaram após corrigir o prompt | Funciona no laboratório anterior, ainda não configurado em C:\Nexos |
| Multimédia | Contratos Som/Imagem e leitura pelo Conductor testados | Sem geração de áudio/imagem nem seleção desta família na Folha |
| Canonical | Zero itens na instalação; bypasses bloqueados | Proteção pelo Host; isolamento do executor ainda pendente |
| Windows/NTFS | Conta Nexus e teste de duas pastas passaram | Novo teste com Conductor não chegou a executar |

## Última tentativa Windows
O Windows recusou a autenticação no novo ensaio. A conta está ativa e sem
bloqueio. O utilizador esclareceu que se enganou na introdução da palavra-passe.
Não há resultado PASS do ensaio Conductor + conta Nexus. Os scripts estão
preparados localmente e ainda não publicados como funcionalidade concluída.
Não foi redefinida a palavra-passe nem desativada segurança para ultrapassar o erro.

## Wiki e repositório
A wiki é documentação Markdown manual e versionada. Contém a organização,
contratos, provas e pendências. Ainda não existe espelhamento automático com o
equipamento nem verificação automática de todos os links e instalações.
Os relatórios históricos mantêm estados antigos; este documento resume o estado
mais recente e deve ser lido primeiro.

Na revisão anterior, código publicado até caf6858, com família Multimédia e prompt literal v2.
Licença: PolyForm Noncommercial 1.0.0. Credenciais fora do GitHub.
Há dois scripts Windows novos locais e diferenças locais que não devem ser
confundidas com código já publicado. Nenhum trabalho anterior foi apagado.

## Organização real
C:\Nexos e o atalho Nexos existem. O Canonical da instalação está vazio.
A aplicação está em aplicacao/nexus e os dados em dados. Python/Conductor,
modelos e Notebook continuam no laboratório anterior. LibreOffice/Java usam
as instalações Windows existentes. Não apagar as pastas anteriores.

## Próximos microprocessos, por ordem
1. Repetir a autenticação e provar Conductor sob a conta Nexus.
2. Ligar essa fronteira ao Host, preservando o Human Gate; testar falhas e regressão.
3. Concluir a configuração cognitiva da instalação sem expor credenciais.
4. Provar backup/restauro e manter a wiki coerente com os resultados.
5. Instalar e testar uma ferramenta de imagem ou som de cada vez; só depois ligar o fluxo.

Zotero, pesquisa web, Publisher, Gmail e Facebook continuam sem circuito
Nexus integrado comprovado. Nenhum PASS estrutural substitui esse teste real.
