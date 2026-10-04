# Estado integrado e baseline de trabalho — 2026-10-04

Branch de continuidade: `lab-integrated-20261004`
PR de integração: #14

Este documento passa a ser o índice de trabalho do Lab. Não apaga história nem substitui leis/arquitetura congelada.

## Regra principal

Trabalhar sempre a partir do último conjunto validado.

- não recomeçar;
- não reimplementar o que já passou;
- não apagar evidência histórica;
- não misturar FAIL experimental com baseline estável;
- cada nova fase parte da baseline PASS anterior;
- uma alteração nova só entra na baseline depois de regressão completa.

## Cadeia validada

| Nível | Origem | Resultado útil preservado | Estado |
|---|---|---|---|
| Núcleo/Work | PR #8 | recovery bidirecional, binding, hardening Store/Windows | HISTÓRICO; conteúdo útil herdado pelo Lab |
| Lab por fases | PR #9 | core/blocos/completo/prático + runners Windows | PASS |
| Spiff + Conductor | PR #10 | Kernel manda; Spiff/Conductor efémeros; 5000 casos | PASS |
| Performance | PR #11 | benchmark e limites reais do Conductor | PASS EXPERIMENTAL |
| Front Door | PR #13 | prefixos, natural/ELIZA rules, LT shadow, Python mínimo | PASS LAB |
| Integração | PR #14 | junta PR #11 e PR #13 sobre PR #10 | EM VALIDAÇÃO FINAL WINDOWS |

## Evidência já provada

### Nexus Lab por fases

| Suite | Resultado |
|---|---:|
| Core | 140 PASS |
| Blocos | 1075 PASS |
| Completo | 1222 PASS |
| Prático Windows | 18 PASS |
| Wrapper PowerShell | PASS |

### Kernel + Spiff + Conductor

| Fase | Casos | Resultado |
|---|---:|---|
| S0 smoke | smoke + limites | PASS |
| S1 ida | 1000 | PASS |
| S2 volta | 1000 | PASS |
| S3 limites/single-dispatch | 1000 | PASS |
| S4 classificações | 1000 | PASS |
| S5 stress seed fixa | 1000 | PASS |
| Total | 5000 | PASS |

### Front Door

| Fase | Casos/iterações lógicas | Resultado |
|---|---:|---|
| L0 prefixos | 1000 + negativos | PASS |
| L1 linguagem natural | 2000 | PASS |
| L2 ambiguidades | 1500 | PASS |
| LanguageTool shadow | 1500 + negativos | PASS |
| L3 adversarial | 2000 | PASS após correção de gerador |
| L4 limites/malformed | 1000 | PASS na última Front Door Lab |
| Total lógico aproximado | 9000+ | PASS da frente |

Nota: contagens pytest são menores porque vários testes iteram centenas/milhares de casos internamente. Não confundir número de funções pytest com número de casos exercitados.

## Performance Conductor

| Comparação | Mediana baseline | Mediana candidata | Resultado |
|---|---:|---:|---|
| 5 set encadeados vs 1 multi-set | 5.435 ms | 5.518 ms | -1.53%; sem benefício |
| 10 set sequenciais vs parallel | 10.509 ms | 11.042 ms | -5.06%; parallel pior |
| foreach 100 set, conc. 1 vs 20 | 57.293 ms | 53.324 ms | +6.93%; ganho pequeno |
| script subprocess vs set interno | 28.155 ms | 1.392 ms | +95.06%; ~20.2x |

Conclusão:
- evitar subprocessos para glue/compare/report simples;
- não usar parallel por defeito;
- concorrência só quando ganho medido;
- manter subprocessos quando representam método/ferramenta realmente independente.

## Autoridade e divisão de funções

| Componente | Função | Estado autoritativo? | Pode promover Canonical? |
|---|---|---:|---:|
| Humano | decisão final | SIM | SIM |
| Kernel/Store | política, estado, recovery, proveniência, Gate | SIM | só executa decisão humana |
| Front Door | reconhecer intenção candidata | NÃO | NÃO |
| ELIZA/rules | matcher/clarificador | NÃO | NÃO |
| LanguageTool | shadow/sugestões | NÃO | NÃO |
| Spiff | lógica transitória de agente | NÃO | NÃO |
| Conductor | executar capabilities/flows técnicos | NÃO | NÃO |
| Markdown | representação humana/auditável | NÃO por si | NÃO |
| YAML | definição versionada de processo | NÃO | NÃO |
| JSON | envelope de execução | NÃO | NÃO |
| Tiny/IA futura | capability opcional | NÃO | NÃO |

## Python mínimo

A regra em vigor:
- Python = cola genérica mínima;
- prefixos/regras naturais = JSON declarativo;
- processos = YAML;
- execução = JSON;
- pedido/conhecimento = Markdown;
- LanguageTool = adaptador existente;
- estado/recovery/Human Gate = Kernel/Store;
- Spiff/Conductor = motores efémeros.

Não voltar a colocar regras de negócio extensas no Python.

## Fluxo integrado alvo

`Folha -> texto/prefixo -> Front Door -> ELIZA/rules -> LanguageTool shadow se necessário -> Markdown -> JSON -> Kernel -> [Conductor | Spiff | Spiff->Conductor] -> capability -> resultado -> Creative -> proveniência -> volta ao pedido original -> Human Gate -> Canonical`

### Já ligado/provado
- Kernel -> Store/Gate/recovery/proveniência;
- Kernel/Spiff/Conductor conjunto;
- Front Door isolada;
- LanguageTool shadow isolado;
- objetos Markdown F009;
- JSON/request Nexus;
- capabilities Conductor individuais.

### Ainda por ligar ponta-a-ponta
1. Front Door -> objeto Markdown;
2. Markdown -> envelope JSON validado;
3. JSON -> Kernel mantendo original/hash;
4. Kernel dispatcher -> rota Conductor/Spiff/Spiff->Conductor;
5. resultado -> Creative -> proveniência inversa até texto original;
6. Human Gate desde um pedido humano real;
7. replay multi-passo sem reexecutar capability durável;
8. capabilities reais uma a uma no Windows Lab;
9. hardening final;
10. sincronização PC servidor -> telemóvel;
11. encriptação final.

## Limpeza segura

### PRESERVAR
- todas as leis;
- testes PASS existentes;
- relatórios de FAIL e correções;
- PR #9, #10, #11 e #13 como história/evidência;
- `C:\Nexus` antigo congelado;
- snapshots/rollback.

### USAR COMO CONTINUIDADE
- `lab-integrated-20261004` depois de todos os gates PASS.

### NÃO USAR COMO BASE NOVA
- PR #8 isolada: o seu HEAD teve FAIL Windows por manifesto de integridade desatualizado; o conteúdo útil foi herdado/corrigido depois.
- branches experimentais antigas isoladamente, quando já estão incorporadas na integrada.

### NÃO APAGAR AINDA
- branches/PRs históricas;
- relatórios de FAIL;
- testes experimentais que documentam limites reais.

Só limpar fisicamente depois da integração estar PASS e existir snapshot/rollback.

## Próxima sequência

1. fechar os quatro gates da PR #14;
2. congelar SHA integrado PASS;
3. ligar Front Door -> Markdown;
4. testar;
5. ligar Markdown -> JSON;
6. testar;
7. ligar JSON -> Kernel;
8. testar ida/volta;
9. ligar dispatcher Kernel -> Spiff/Conductor;
10. testar milhares de bons/maus/erros/restart;
11. só depois capabilities externas e hardening final.

## Estado atual

A PR #14 já teve:
- Auditoria: PASS;
- Nexus Front Door Lab: PASS;
- Spiff + Conductor Lab: PASS;
- Nexus Windows: ainda em execução no momento desta escrita.

Não promover nem apagar nada até o Nexus Windows fechar PASS.
