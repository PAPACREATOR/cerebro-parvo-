# Nexus — quadro operacional de execução

Data: 2026-10-04
Branch: `work/audit-bidirectional-20261004`
Objetivo: acelerar implementação sem alterar leis/arquitetura congeladas.

## Regra de execução

Cada item segue obrigatoriamente:

`AUDITAR -> COMPARAR -> TESTE FAIL-FIRST -> CORREÇÃO MÍNIMA -> TESTE IDA -> TESTE VOLTA -> SEGURANÇA -> WINDOWS-LAB -> REGISTO -> PROMOTABLE`

Estados permitidos: `PASS / FAIL / BLOCKED / NOT RUN`.

Nenhum PASS de CI substitui o teste no Windows real em `C:\Nexus-Lab`.

## Divisão de funções

| Papel | Função exclusiva |
|---|---|
| Work | implementação/CI remoto em commits pequenos |
| GPT revisor | auditoria, comparação, contratos, testes diferenciais, revisão de regressões |
| Codex no PC | aplicar commit aprovado em `C:\Nexus-Lab`, executar Windows real e devolver evidência |
| Pedro | autoridade final: arquitetura, promoção, merge e decisões humanas |

## Fila atual

| # | Microprocesso | Estado | Critério de passagem |
|---|---|---|---|
| 01 | Crash depois de resultado externo persistido e antes de `Store.accept` | EM TESTE | restart não reduz evidência existente a FAIL genérico; reconciliação fica explícita |
| 02 | Crash antes de chamar executor | NOT RUN | operação recuperável sem efeitos externos duplicados |
| 03 | Crash durante executor | NOT RUN | estado conservado; sem promoção; retry apenas por regra idempotente |
| 04 | Crash depois de Creative e antes de Human Gate | NOT RUN | Creative verificável; Canonical intacto |
| 05 | Crash durante promoção Canonical | NOT RUN | reconciliação COMMITTED/RECOVERY_REQUIRED sem aprovação inventada |
| 06 | Idempotência de reexecução | NOT RUN | mesmo operation/input não duplica efeitos |
| 07 | Human Gate adversarial | NOT RUN | bypass/replay/ticket errado/alteração pós-review bloqueados |
| 08 | Proveniência bidirecional por capability | NOT RUN | resultado -> processo -> ferramenta -> input fecha por hashes/IDs |
| 09 | Conductor efémero | NOT RUN | restart Kernel não depende de memória Conductor |
| 10 | Spiff vs Conductor | BLOCKED | só comparar routing/loops/gates/subflows quando espelho local reproduzível chegar |
| 11 | Windows ACL/conta Nexus por capability | NOT RUN | mínimo privilégio + bypass bloqueado |
| 12 | LibreOffice real | NOT RUN | ida/volta, timeout, input inválido, hash, Creative |
| 13 | LanguageTool real | NOT RUN | ida/volta, falha Java/LT, sem IA |
| 14 | Open Notebook/tiny | NOT RUN | contexto mínimo, saída candidata, sem autoridade |
| 15 | Zotero | NOT RUN | referência real, proveniência e ausência explícita |
| 16 | Snapshot/restore completo | NOT RUN | hashes + inventário + restauro demonstrado |
| 17 | 100 000 casos diferenciais/property-based | NOT RUN | tabela AGREEMENT/CONFLICT/UNKNOWN/FAIL |
| 18 | Regressão integrada Windows | NOT RUN | sem falha crítica aberta |
| 19 | Hardening Windows final | NOT RUN | isolamento, credenciais, rede, permissões, rollback |
| 20 | PC servidor <-> telemóvel | NOT RUN | autenticação/cifra/idempotência; PC continua autoridade |

## Regra de não duplicação

Antes de iniciar um item:
1. ler este quadro;
2. ler PR #7 e comentários recentes;
3. verificar branch/commit em curso;
4. não editar ficheiro que outro executor esteja a alterar;
5. deixar commit, testes e próximo passo registados.

## Promoção

Só marcar `PROMOTABLE` depois de:
- testes relevantes PASS;
- ida/volta PASS;
- segurança do microprocesso PASS;
- regressão PASS;
- teste Windows real em `C:\Nexus-Lab` PASS;
- diff explícito contra produção;
- rollback demonstrável.
