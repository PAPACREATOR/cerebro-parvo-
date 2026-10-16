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
