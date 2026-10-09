# Contribuir

Contribuições são bem-vindas, sobretudo reprodução independente, testes adversariais, documentação, revisão de segurança, integrações pequenas e diagnóstico de bugs.

Antes de programar, leia [docs/00-start-here/](docs/00-start-here/README.md) e [docs/30-help/](docs/30-help/README.md).

## Antes de programar

1. Procure uma issue existente.
2. Reproduza o problema.
3. Explique comportamento esperado e observado.
4. Prefira `usar > adaptar > criar`.
5. Não introduza dependência quando Kernel + MCP/API/CLI existente já resolvem a função.
6. Preserve autoridade humana, Creative/Canonical, proveniência, recovery e IA sem autoridade.
7. Não enfraqueça AppContainer/LPAC/Job/ACL para transformar FAIL em PASS.
8. Trabalho experimental deve ficar em branch/lab isolado até existir evidência.

## Pull requests

Um PR deve:

- ser pequeno e focado;
- indicar a issue/problema que resolve;
- incluir testes positivos, negativos e adversariais quando aplicável;
- declarar dependências/licenças novas;
- não conter segredos nem dados pessoais;
- explicar em linguagem natural o comportamento do processo/regra;
- preservar FAIL/BLOCKED/NOT RUN como tal;
- não mover ou redesenhar o Kernel sem falha concreta demonstrada por teste.

Código de terceiros não deve ser copiado sem origem, commit/versão e licença.

## Onde ajudar

Veja [docs/30-help/README.md](docs/30-help/README.md). As issues #35–#39 foram preparadas para colaboração externa sem trabalhar por cima do runtime principal.

## Licenciamento das contribuições

O projeto usa PolyForm Noncommercial 1.0.0 para a distribuição comunitária e pretende manter a possibilidade de licenciamento comercial separado.

PRs com código ou documentação original só devem ser fundidos quando o contribuidor aceitar o [Contributor License Agreement](CONTRIBUTOR_LICENSE_AGREEMENT.md). O contribuidor mantém o copyright; o acordo concede ao mantenedor os direitos necessários para distribuir e relicenciar a contribuição, incluindo em ofertas comerciais.

A aceitação é registada pelo checkbox correspondente no template do pull request. Para contribuições de empresas ou situações de propriedade intelectual complexa, pode ser necessário um acordo separado.

## O que não prometemos

Contribuir não cria automaticamente emprego, participação societária, royalties ou direito a receitas. Qualquer relação comercial ou remuneração exige acordo escrito separado.
