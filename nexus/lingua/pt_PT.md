# Português europeu — léxico operacional e gramática local

<!-- nexus-pt-PT-v1 -->

Fonte em **Markdown** para índice SQLite FTS5 local, reconstruível e consultivo.
Este conjunto é um léxico operacional limitado, não o dicionário integral da
língua portuguesa nem uma gramática exaustiva. O conhecimento linguístico
não concede execução, aprovação ou promoção a Canonical.

## Dicionário operacional

| forma | lema | intenção |
| --- | --- | --- |
| guarda | guardar | arquivo |
| guardar | guardar | arquivo |
| guarde | guardar | arquivo |
| guardes | guardar | arquivo |
| guardem | guardar | arquivo |
| arquiva | arquivar | arquivo |
| arquivar | arquivar | arquivo |
| arquive | arquivar | arquivo |
| arquives | arquivar | arquivo |
| arquivem | arquivar | arquivo |
| salva | salvar | arquivo |
| salvar | salvar | arquivo |
| salve | salvar | arquivo |
| salves | salvar | arquivo |
| pesquisa | pesquisar | web |
| pesquisar | pesquisar | web |
| pesquise | pesquisar | web |
| pesquisem | pesquisar | web |
| pesquiza | pesquisar | web |
| procura | procurar | web |
| procurar | procurar | web |
| procure | procurar | web |
| procurem | procurar | web |
| encontra | encontrar | fontes |
| encontrar | encontrar | fontes |
| encontre | encontrar | fontes |
| encontrem | encontrar | fontes |
| revê | rever | trabalhar |
| reve | rever | trabalhar |
| rever | rever | trabalhar |
| reveja | rever | trabalhar |
| revejam | rever | trabalhar |
| corrige | corrigir | trabalhar |
| corrigir | corrigir | trabalhar |
| corrija | corrigir | trabalhar |
| corrijam | corrigir | trabalhar |
| melhora | melhorar | trabalhar |
| melhorar | melhorar | trabalhar |
| melhore | melhorar | trabalhar |
| melhorem | melhorar | trabalhar |
| reescreve | reescrever | trabalhar |
| reescrever | reescrever | trabalhar |
| reescreva | reescrever | trabalhar |
| reescrevam | reescrever | trabalhar |
| trabalha | trabalhar | trabalhar |
| trabalhar | trabalhar | trabalhar |
| explica | explicar | perguntar |
| explicar | explicar | perguntar |
| explique | explicar | perguntar |
| expliquem | explicar | perguntar |
| responde | responder | perguntar |
| responder | responder | perguntar |
| responda | responder | perguntar |
| respondam | responder | perguntar |
| calcula | calcular | calcular |
| calcular | calcular | calcular |
| calcule | calcular | calcular |
| calculem | calcular | calcular |
| soma | somar | calcular |
| somar | somar | calcular |
| some | somar | calcular |
| somem | somar | calcular |

## Gramática de cláusulas

<!-- nexus-pt-grammar-v1 -->
| regra | formas |
| --- | --- |
| pergunta_inicio | como ; de que forma ; qual é a forma de ; qual e a forma de |
| negacao_inicio | não ; nao ; nunca ; jamais ; nem ; sem |
| segunda_acao | e ; e também ; e depois ; e a seguir ; mas depois ; depois ; em seguida |
| segunda_clausula | e também ; e depois ; e a seguir ; mas depois ; em seguida |
| pergunta_modal | explica ; explica-me ; podes explicar ; poderias explicar ; consegues explicar ; diz-me ; podes dizer-me |
| pedido_modal | podes ; poderias ; pode ; poderia ; consegues ; consegue ; quero que ; preciso que ; quero ; pretendo ; gostaria de ; preciso de ; ajuda-me a |
| contexto_web | web ; internet ; online ; net |
| contexto_fontes | fonte ; fontes |
<!-- /nexus-pt-grammar-v1 -->

A gramática portuguesa diferencia «como guardar» de «guarda», conserva
negação, citação e segundas ações sob decisão humana. Os marcadores gramaticais
são reconhecidos por regex a partir deste Markdown; as formas do dicionário
são consultadas com FTS5 MATCH parametrizado mais igualdade lexical exata.
Alterar este ficheiro obriga a rever o digest fixado em frontdoor.py e a
executar regressões. Um futuro dicionário geral (por exemplo Hunspell pt-PT)
deve permanecer separado do léxico de comandos; pertencer ao dicionário
nunca transforma uma palavra isolada em autorização de execução.
O índice efémero reconstrói-se deste ficheiro local, não é o Store/Creative/
Canonical e não necessita de rede, Docker, Ollama ou Java.

## Contrato do Front Door

<!-- nexus-frontdoor-contract-v1 -->
~~~json
{
  "version": "1.0",
  "max_text_chars": 100000,
  "prefixes": [
    [
      "@@",
      "arquivo"
    ],
    [
      "\"\"",
      "fontes"
    ],
    [
      "??",
      "perguntar"
    ],
    [
      "&",
      "trabalhar"
    ],
    [
      "%",
      "calcular"
    ],
    [
      "#",
      "tema"
    ],
    [
      "@",
      "web"
    ]
  ],
  "clarification_patterns": [
    "\\b(?:evita(?:r)?|pro[ií]bo|sem|deixa(?:r)?\\s+de)(?:\\s+\\w+){0,2}\\s+(?:guarda(?:r)?|arquiva(?:r)?|salva(?:r)?|verific(?:a|ar|as|ares))\\b",
    "\\b(?:não|nao|nunca|jamais)(?:\\s+\\w+){0,3}\\s+(?:guard(?:a(?:r|s)?|es)|arquiv(?:a(?:r|s)?|es)|salv(?:a(?:r|s)?|es)|corrig(?:e(?:r|s)?|as)|revê|reve|rever|melhor(?:a(?:r|s)?|es)|verific(?:a|ar|as|ares)|verifiqu(?:e|es))\\b",
    "\\b(?:não|nao|nunca|jamais)(?:\\s+\\w+){0,3}\\s+(?:calcul(?:a(?:r|s)?|es)|som(?:a(?:r|s)?|es)|pesquis(?:a(?:r|s)?|es)|procur(?:a(?:r|s)?|es)|reescreve(?:r|s)?|explica(?:r|s)?)\\b",
    "[«“\\\"][^«»“”\\\"]*(?:guarda|corrige|calcula|pesquisa|arquiva|verifica|verificar)[^«»“”\\\"]*(?:[»”\\\"]|$)",
    "\\b(?:a palavra|a frase|o termo)\\s+(?:guarda|corrige|calcula|pesquisa|arquiva)\\b"
  ],
  "natural_rules": {
    "arquivo": [
      "\\bguarda(?:r)?\\b",
      "\\barquiva(?:r)?\\b",
      "\\bsalva(?:r)?\\b",
      "\\bguarda isto\\b"
    ],
    "web": [
      "\\bpesquis[ae](?:r)?\\b.*\\b(?:web|internet|online|net)\\b",
      "\\bprocura(?:r)?\\b.*\\b(?:web|internet|online|net)\\b",
      "\\bpesquiza(?:r)?\\b.*\\b(?:web|internet|online|net)\\b"
    ],
    "fontes": [
      "\\b(?:encontra|procura|pesquisa|pesquiza)\\b.*\\bfontes?\\b",
      "\\bquais\\b.*\\bfontes?\\b",
      "\\bda(?:-me)?\\b.*\\bfontes?\\b"
    ],
    "trabalhar": [
      "\\btrabalha(?:r)?\\b",
      "\\b(?:reve|revê|rever)\\b",
      "\\bmelhora(?:r)?\\b",
      "\\breescreve(?:r)?\\b",
      "\\bcorrige(?:r)?\\b",
      "\\bverific(?:a|ar|as|ares)\\b.*\\bintegridade\\b",
      "^interpretar documento$"
    ],
    "perguntar": [
      "\\bexplica(?:r)?\\b",
      "\\bresponde(?:r)?\\b",
      "\\bo que (?:e|é)\\b",
      "\\bquem (?:e|é)\\b",
      "\\bporqu[eê]\\b",
      "\\bcomo\\b"
    ],
    "calcular": [
      "\\bcalcula(?:r)?\\b",
      "\\bfaz(?:er)?\\b.*\\bconta\\b",
      "\\bquanto (?:e|é)\\b",
      "\\bsoma(?:r)?\\b"
    ],
    "tema": [
      "(?:^|\\be também\\s+)(?:tema|assunto)\\b",
      "(?:^|\\be também\\s+)quero falar sobre\\b"
    ]
  },
  "operation_rules": [
    {
      "process": "verify",
      "intent": "trabalhar",
      "requires_attachment": true,
      "patterns": [
        "\\bverific(?:a|ar|as|ares)\\b.*\\bintegridade\\b.*\\b(?:ficheiro|documento|arquivo)\\b"
      ]
    },
    {
      "process": "convert_pdf",
      "intent": "trabalhar",
      "requires_attachment": true,
      "patterns": [
        "^converter para pdf$"
      ]
    },
    {
      "process": "book",
      "intent": "trabalhar",
      "requires_attachment": true,
      "patterns": [
        "^exportar manuscrito para pdf$"
      ]
    }
  ]
}
~~~
<!-- /nexus-frontdoor-contract-v1 -->

Este bloco Markdown contém as regras mecânicas com a sintaxe dos padrões
regex, os sete prefixos e os processos permitidos. O ficheiro JSON histórico
permanece como **espelho selado de compatibilidade**, devendo ser idêntico à
versão carregada daqui. Alterações de regras exigem atualização conjunta,
verificação de integridade e testes; não autorizam processos novos.

## Padrão de ligação Python

A fonte é Markdown; `lingua/indexer.py` lê uma versão SHA-256 aprovada,
valida as tabelas e o contrato, e cria FTS5 em memória. O `frontdoor.py`
compara a intenção por regex + pesquisa lexical exata, pergunta ao humano
quando há conflito e nunca chama ferramentas nem muda o conhecimento canónico.
Capítulos adicionais em Markdown são apenas **fontes para pesquisa**;
não criam verbos executáveis, processos, permissões nem aprovação.
