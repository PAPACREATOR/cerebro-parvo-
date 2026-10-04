# Relatório — organização dos testes do Nexus-Lab

Data: 2026-10-04

## Objetivo

Executar a futura versão do Nexus por fases no `C:\Nexus-Lab`, sem contaminar `C:\Nexus`.

## Ordem

1. `TESTAR-NUCLEO.bat`
2. `TESTAR-BLOCOS.bat`
3. `TESTAR-NEXUS-COMPLETO.bat`
4. `TESTAR-PRATICO.bat`

Todos usam o mesmo `nexus/windows/check-nexus.ps1`, que continua a executar `all` por defeito.

## Núcleo

Inclui Store, Host, startup, crash/recovery, reverse provenance, vaults, schemas e adversarial.

Objetivo:
- estado;
- Human Gate;
- Creative/Canonical;
- proveniência;
- restart/recovery;
- idempotência;
- segurança do núcleo.

## Blocos

Inclui Conductor/workflows, Windows hash, LanguageTool, Office, Notebook e multimédia.

Objetivo:
- testar as peças antes do sistema completo;
- localizar falhas por capability;
- não atribuir um FAIL externo ao Kernel sem prova.

## Nexus completo

Executa `pytest nexus/tests` inteiro, incluindo a matriz determinística de 100 000 casos.

Objetivo:
- regressão integral;
- detectar interferência entre blocos;
- confirmar integridade.

## Prático v1

Executa os contratos que já usam Windows/Conductor real:
- ferramenta Windows sem IA;
- hash Windows em ambiente reduzido;
- ida/volta real Windows + restart;
- leitura real das famílias por Conductor.

Limite:
- ainda não prova instalações reais de LibreOffice, LanguageTool e OpenNotebook no PC Lab;
- estes testes serão acrescentados quando cada capability for instalada/ligada no Lab;
- depois serão acrescentados testes práticos de uso pela Folha e, mais tarde, Nexus completo/homelab.

## Regra

Cada fase produz:
- SHA;
- PASS/FAIL;
- state.json;
- stdout/stderr;
- JUnit XML;
- relatório do verificador.

Nenhum PASS remoto ou parcial promove automaticamente a versão antiga.

## Promoção

O `C:\Nexus-Lab` aprovado integralmente será a nova versão oficial.
`C:\Nexus` atual permanece congelado até decisão humana de promoção.
