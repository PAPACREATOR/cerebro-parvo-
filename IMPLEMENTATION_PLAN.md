# Plano de execução vigente

1. Usar a documentação reconciliada e os contratos corrigidos, preservando genealogia.
2. Auditar o candidato importado contra IMP-001. Implementar/corrigir apenas o âmbito dessa tarefa quando autorizado; fechar os testes de receção e integração de referência/stream.
3. Só após PASS completo de IMP-001, fechar política/contrato de IMP-002 e avançar sequencialmente.
4. Resolver G10 antes de afirmar persistência autoritativa em IMP-003/004/005/018/019. Não fingir atomicidade conjunta SQLite/filesystem/EventLog.
5. Formar B1 ingestão (001–007), B2 adaptação (008–015), B3 persistência (016–020), B4 falha/apresentação/recovery (021–023), B5 eliminação separada (024–026) apenas com IMP aprovados.
6. Executar regressão, T1–T10 e E2E-01–15 conforme fontes; completar contratos de outras famílias M1–M14.

O código candidato já contém esboços de etapas posteriores. A sua preservação não equivale a ter passado estes portões. Não criar novos módulos para preencher a matriz por contagem.

[IMP-001](tasks/IMP-001.md) · [Pendências](docs/PENDENCIAS.md) · [Conformidade](docs/MATRIZ-CONFORMIDADE.md).
