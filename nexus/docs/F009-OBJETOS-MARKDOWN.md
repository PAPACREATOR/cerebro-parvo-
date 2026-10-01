# F009 — primeira família Multimédia

## Contrato
INPUT: Markdown UTF-8, até 100 KB, com YAML inicial entre ---.
Campos obrigatórios: tipo=proposta, familia=multimedia, tribo=som ou imagem,
dominio=creative, lab=windows. Campos adicionais são rejeitados.
OUTPUT: JSON com nome_ficheiro, dados_yaml e notas_markdown.

O leitor é o nativo do Microsoft Conductor 0.1.41. O adaptador Nexus apenas
limita tamanho, valida o contrato e compõe o envelope. Não implementa parser YAML.
As APIs de leitura usadas são internas ao Conductor; a revisão está fixada em
11dcc41ed3df78f0806127cc901822fe8758294b e exige regressão antes de atualizar.

Conductor executa register_object.yaml e chama essa capability. Nenhuma IA é
registada no executor. Metadados e notas não concedem capacidades nem aprovação.
O manifesto do Host inclui os contratos e exemplos desta família.

## Evidência
100 casos válidos (dois ramos, notas e nomes Unicode), 900 casos inválidos
(cinco campos, quinze valores inválidos, seis variantes de formatação), mais
18 controlos de campos ausentes, autoridade extra, codificação, tamanho,
metadados malformados e execução real de ambos os ramos pelo Conductor.

Regressão antes de atualização do manifesto: 1133 testes passaram em 31.96 s.
As primeiras falhas do ensaio eram dupla descodificação de JSON já convertido
pelo Conductor e identificação excessivamente longa de um caso parametrizado.
As asserções de conteúdo foram preservadas. Diagnóstico conservado localmente.

## Limites
Esta família é uma fundação de contratos, não um gerador instalado.
Ainda não está selecionável na Folha nem materializa automaticamente o envelope
em Creative. Nenhum processo de geração de som/imagem foi autorizado no Host.
Geração permanece por instalar, integrar e testar, uma ferramenta de cada vez.
Nada foi promovido para Canonical.
