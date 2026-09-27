# Pendências e portões

| ID | Lacuna | Consequência / fecho necessário |
| --- | --- | --- |
| P01 | Receção completa IMP-001 | Fechar fronteira referência/stream/Folha, erros/interrupção e critérios dedicados; sem avanço a IMP-002 |
| P02 | Política IMP-002 | Limites, vazio, transferência íntegra; valores dos testes são fixtures, não decisões de produto |
| P03 | G10 / IMP-003–005, 018–019 | Eventos/recibos/fronteiras transacionais e replay; materialize permanece bloqueado |
| P04 | IMP-008–015 | Confiança de formato, prioridade/versionamento de adaptador, limites/sandbox, schema e classificação |
| P05 | IMP-020 | Reconstrução real de FTS/cache e política de pesquisa com derivados sujos |
| P06 | IMP-024–026 | Original/quarentena/backup/retenção, autorização atual, uso único e efeitos restritos |
| P07 | M1–M14 além da importação | Catálogo de restantes famílias e contratos; não inventar correspondência completa com os 26 IMP |
| P08 | Integrações e Windows | Activepieces/ferramentas/IA, isolamento, concorrência, crash/restart/restore, testes Windows e usabilidade |
| P09 | Terceiros | Fixar commit/licença/ficheiro antes de reutilizar código real |

Fechar por ordem de dependência, um microprocesso de cada vez. Guardar também falhas e casos não executados. Pesquisa/conceção adicional só para resolver lacuna concreta; não reabrir toda a arquitetura.
