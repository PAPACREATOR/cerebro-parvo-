# ADR — convergência num único Nexus Windows

Data: 07-10-2026 (decisão na issue #33; progresso consultado a 10/10). Estado: **vigente como orientação**, implementação **Draft/pendente de aceitação**.

**Problema:** a PR #31 revê contratos do núcleo transacional antigo, enquanto a PR #32 contém o runtime Windows atual. Não se pode declarar o produto uno somando PASS de branches diferentes.

**Decisão:** usar PR #32 como baseline candidata; trazer garantias da #31 como testes do runtime ativo. Só corrigir produção perante FAIL real, com a alteração mínima. PR #45 reúne trabalho posterior em isolamento, sem autorização para merge nem release.

**Porquê:** copiar dois Kernels ou portar componentes em bloco criaria duplicação de autoridade, risco de regressão e relatórios de teste incomparáveis. O objetivo é uma única implementação verificável por SHA, sem alterar M1–M14, Creative/Canonical e recuperação.

**Critério:** CI aplicável no mesmo HEAD, testes de segurança, side effects, crash/recovery, Windows/LPAC e aceitação física separada. Até então **NOT READY**.

Fontes: [issue #33](https://github.com/PAPACREATOR/cerebro-parvo-/issues/33), [PR #31](https://github.com/PAPACREATOR/cerebro-parvo-/pull/31), [PR #32](https://github.com/PAPACREATOR/cerebro-parvo-/pull/32), [PR #45](https://github.com/PAPACREATOR/cerebro-parvo-/pull/45).