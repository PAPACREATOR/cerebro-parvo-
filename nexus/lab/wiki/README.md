# Laboratório Wiki — pesquisa web e conhecimento de escritor

Este laboratório é isolado e não altera o núcleo Nexus nem o trabalho de outras branches. Pedro Coelho é o decisor final.

Objetivo: testar 100000 casos sintéticos de pesquisa web normal, organização Markdown, relações bidirecionais, pesquisa, falhas, reconstrução de índice, reutilização em novo processo e espaço de disco.

O estudo inclui temas, sites, páginas, fontes, pesquisas, notas, conclusões e usos criativos típicos de um escritor-investigador. Não usa IA, Tiny/OpenBook, Spiff, Conductor real, APIs externas, dados pessoais ou publicação real.

A suite deve produzir PASS/FAIL/NOT RUN, contagens, hashes, relações, consultas, falhas reproduzidas, espaço por componente, custo médio por caso e relatório final para a equipa. O índice é reconstruível e nunca é a fonte de verdade.

O resultado não autoriza integração automática em nenhuma branch oficial.

## Complemento executável de 04/10

Ver `../../docs/COMPLEMENTO-WIKI-INFORMACAO-GERADA-2026-10-04.md` e `../../docs/RELATORIO-FINAL-WIKI-100K.md`.

Comando: `python nexus/lab/wiki/test_web_research_wiki_100k.py --cases 100000 --output nexus/lab/wiki/results`. A contagem é de objetos sintéticos, não de cenários independentes. O envelope experimental não é o contrato F009. Resultados de execução ficam em `summary.json`; falha devolve código diferente de zero.
