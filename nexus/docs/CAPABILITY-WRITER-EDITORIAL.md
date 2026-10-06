# Capability — LibreOffice Writer editorial

Estado: **contrato de capacidade a implementar/testar**. Não altera M1–M14 nem a autoridade do Kernel.

A integração LibreOffice existente em [F007](F007-LIBREOFFICE.md) prova apenas **DOCX/ODT → PDF**. Este contrato define a extensão necessária para Writer editorial/livros.

## Objetivo

Permitir que o Nexus produza e reveja documentos Writer profissionais sem transformar LibreOffice em memória, UI principal ou autoridade.

Fluxo:

```text
pedido / estrutura / conteúdo aprovado
        ↓
Kernel valida intenção e assets
        ↓
Writer adapter prepara ODT candidate
        ↓
LibreOffice Writer renderiza/exporta
        ↓
validação estrutural + hashes + preview/PDF
        ↓
Creative
        ↓
revisão humana
        ↓
Canonical apenas após Human Gate
```

## Princípios

- formato editável preferencial: ODT;
- DOCX é formato de interoperabilidade, não fonte autoritativa por defeito;
- PDF é derivado de publicação, nunca substitui o editável;
- original fornecido pela pessoa nunca é alterado;
- macros, scripts, ligações externas e embeddings ativos são bloqueados;
- LibreOffice não escreve diretamente em Creative/Canonical;
- toda a saída é candidate/UNTRUSTED até validação do Kernel;
- estilos e layout são dados explícitos, não efeitos invisíveis de UI;
- reabrir/editar deve preservar estrutura e proveniência;
- nenhum documento é publicado automaticamente.

## Perfis editoriais

O primeiro perfil deve ser `book.standard.v1`.

Campos explícitos e versionados:

- formato de página;
- orientação;
- margens superior/inferior;
- margem interior/exterior;
- gutter;
- cabeçalho/rodapé;
- posição e formato da numeração;
- página inicial de capítulo;
- estilos de título/subtítulo/corpo/citação/legenda/notas;
- fonte/fallback;
- tamanho/entrelinha;
- recuo de primeira linha;
- espaço antes/depois;
- alinhamento;
- controlo de viúvas/órfãos;
- keep-with-next;
- page-break-before;
- hifenização;
- língua;
- estilos de imagem/legenda;
- sumário/índice;
- metadados do documento.

Nenhum valor é inferido silenciosamente como “regra universal”. O perfil deve dizer o que escolheu.

## Microprocessos

### W001 — receber pedido editorial
Entrada: texto/Markdown estruturado, documento existente ou pacote de capítulos.

Saída: operação editorial sem mutação.

Testes:
- vazio;
- excesso de tamanho;
- Unicode;
- capítulos repetidos;
- asset ausente;
- paths externos;
- instruções que tentem promover/publicar.

### W002 — normalizar estrutura

Transformar a entrada numa árvore editorial determinística:

```text
book
 ├ metadata
 ├ front_matter
 ├ chapters[]
 │   ├ title
 │   └ blocks[]
 └ back_matter
```

Blocos iniciais:
- paragraph;
- heading;
- quote;
- image;
- caption;
- page_break;
- list;
- note.

Não usar HTML arbitrário como autoridade estrutural.

### W003 — validar assets

Para cada imagem:
- caminho atribuído;
- MIME/assinatura;
- dimensões;
- tamanho;
- hash;
- sem symlink/junction;
- sem URL externa;
- sem objeto incorporado ativo.

### W004 — selecionar perfil

Só perfis allowlisted e versionados.

Perfil desconhecido → BLOCKED.

### W005 — criar pacote ODT

Construção determinística de:
- `mimetype`;
- `META-INF/manifest.xml`;
- `content.xml`;
- `styles.xml`;
- `meta.xml`;
- assets permitidos.

Preferir geração ODF determinística pelo adapter a macros.

### W006 — estilos de página

Aplicar:
- tamanho;
- orientação;
- margens espelhadas;
- gutter;
- first/left/right page styles quando necessário;
- início de capítulo em página definida pelo perfil.

### W007 — estilos tipográficos

Todos os parágrafos devem usar estilos nomeados.

Proibir formatação manual invisível quando existir estilo equivalente.

### W008 — capítulos e secções

- heading hierarchy válida;
- page break explícito;
- secções não sobrepostas;
- sem heading level skip não autorizado;
- bookmarks/IDs estáveis quando aplicável.

### W009 — viúvas, órfãos e continuidade

Configurar/testar:
- orphan control;
- widow control;
- keep-with-next em títulos;
- keep-together quando aplicável;
- não deixar título isolado no fundo da página.

PASS estrutural não substitui inspeção de paginação.

### W010 — cabeçalhos, rodapés e paginação

- páginas iniciais de capítulo conforme perfil;
- numeração coerente;
- páginas preliminares com esquema próprio quando definido;
- cabeçalho não deve aparecer onde o perfil o proíbe;
- conteúdo dinâmico apenas por campos Writer conhecidos/allowlisted.

### W011 — imagens e legendas

- imagem vinculada ao asset copiado para o ODT;
- tamanho/âncora definidos;
- legenda ligada logicamente;
- sem links externos;
- sem crop destrutivo do original;
- hash do original preservado.

### W012 — sumário/índice

Gerar a partir da hierarquia real de headings.

Não aceitar índice escrito manualmente como prova de estrutura.

### W013 — notas e referências

Primeira versão:
- footnotes/endnotes estruturadas;
- referências externas tratadas como texto/citação, não hiperlinks ativos por defeito.

Zotero é capability separada; quando integrado, entrega metadados/proveniência ao Kernel.

### W014 — guardar candidate editável

Resultado:
- `resultado.odt`;
- SHA-256;
- perfil;
- versão do adapter;
- hashes dos assets;
- relatório de validação.

Creative recebe cópia delimitada após validação.

### W015 — renderizar PDF

Usar LibreOffice instalado, perfil efémero e macros no nível máximo de bloqueio.

Saída:
- `resultado.pdf`;
- hash;
- número de páginas;
- evidência do export.

### W016 — validar PDF

Validação mínima:
- assinatura PDF/EOF;
- tamanho;
- páginas > 0;
- texto esperado em amostras;
- dimensões de página;
- sem ficheiro truncado.

Validação visual é gate separado.

### W017 — round-trip

Reabrir `resultado.odt` e verificar:
- estilos obrigatórios;
- hierarquia;
- número de capítulos;
- assets;
- metadados;
- relações essenciais.

Exportar novamente não deve alterar semanticamente a estrutura esperada.

### W018 — comparação editável ↔ PDF

Comparar:
- títulos;
- sequência de capítulos;
- número/posição aproximada de assets;
- texto amostrado;
- contagem de páginas plausível;
- ausência de páginas vazias inesperadas segundo regras do perfil.

Divergência → REVIEW/BLOCKED, nunca PASS automático.

### W019 — revisão humana

A Folha apresenta:
- ODT;
- PDF;
- perfil aplicado;
- avisos;
- diferenças/limitações;
- hashes.

A pessoa decide se aprova.

### W020 — promoção e recuperação

Canonical só recebe os artefactos vinculados à decisão humana.

Depois de restart:
- hashes conferem;
- artefactos permanecem;
- aprovação não é repetida;
- LibreOffice não é reexecutado para reconstruir história.

## Testes obrigatórios por bloco

Cada microprocesso deve ter:

1. caso positivo mínimo;
2. caso positivo Unicode/pt-PT;
3. limite;
4. input malformado;
5. conteúdo ativo/malicioso;
6. path/symlink/junction;
7. timeout/ferramenta ausente quando aplicável;
8. output incompleto;
9. adulteração após geração;
10. restart/recovery quando houver estado.

## Matriz editorial inicial

O primeiro corpus artificial deve incluir:

- livro curto 3 capítulos;
- capítulo que começa em página direita;
- parágrafos que forcem viúvas/órfãos;
- título perto do fundo da página;
- citações longas;
- lista;
- notas;
- imagens portrait/landscape;
- legenda;
- caracteres portugueses;
- travessões/aspas;
- página preliminar;
- sumário;
- capítulo sem imagem;
- capítulo com duas imagens;
- texto suficiente para pelo menos 20 páginas.

Depois:
- 100 documentos gerados por combinações de perfil/conteúdo;
- 1.000 testes estruturais/adversariais;
- corpus de regressão fixo com hashes/expectativas;
- E2E Writer real no Windows.

## O que não entra na primeira versão

- macros;
- Basic;
- extensões LibreOffice;
- scripts embutidos;
- links externos automáticos;
- objetos OLE;
- folhas de cálculo incorporadas;
- colaboração cloud;
- publicação automática;
- alteração do original;
- geração de texto por IA dentro do adapter Writer.

## Implementação preferida

Ordem de preferência:

1. **ODF/ODT determinístico + LibreOffice para render/export**;
2. UNO apenas para operações que o ODF determinístico não consiga representar/testar de forma robusta;
3. nunca macros como mecanismo normal.

Isto mantém o adapter pequeno, auditável e independente da UI do Writer.

## Critério de PASS da capability

Só declarar **WRITER_EDITORIAL=PASS** quando, no mesmo HEAD:

- ODT real criado;
- abre no LibreOffice Writer;
- estilos/páginas/estrutura conferidos;
- PDF real exportado;
- round-trip passa;
- adulteração bloqueia;
- original intacto;
- Creative recebe candidate;
- Human Gate obrigatório;
- Canonical vazio antes da decisão;
- restart não reexecuta LibreOffice;
- regressão total Nexus continua verde.

Até lá, F007 continua corretamente descrita apenas como conversão DOCX/ODT → PDF.
