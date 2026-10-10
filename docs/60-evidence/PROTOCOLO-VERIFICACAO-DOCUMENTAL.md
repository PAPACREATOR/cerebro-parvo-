# Protocolo de verificação e atualização documental

**Aplicação:** todas as páginas atuais do Nexus e contribuições que afirmem comportamento do produto. Não altera código. Este protocolo rege o trabalho da PR #49, não impõe alterações às branches dos outros.

## Unidade auditável

Cada afirmação operacional deve ter: (a) contrato humano/invariante, (b) ficheiro ou símbolo no **SHA integral**, (c) teste/workflow e respetivo ambiente **quando existe**, (d) resultado preciso PASS/FAIL/BLOCKED/NOT RUN/UNKNOWN, (e) alcance/limite, (f) data de observação. Sem estes elementos, escrever «implementação observada no código», «hipótese» ou «evidência por confirmar», nunca «funciona».

### Estados que não se confundem

| Estado | Significado admissível |
| --- | --- |
| DESENHADO | Regra/plano; nenhuma funcionalidade comprovada |
| IMPLEMENTADO (leitura estática) | Ficheiros/rotas encontrados num SHA; não foram necessariamente exercitados |
| PASS (teste identificado) | Teste especificado e concluído no ambiente e SHA indicados |
| FAIL | Falha observada e preservada até correção e repetição no mesmo alvo |
| BLOCKED | Execução ou prova impedida por limite explícito |
| NOT RUN | Teste não executado |
| UNKNOWN | Prova insuficiente |
| APROVADO | Aceitação humana expressa para âmbito e versão indicados, após os gates aplicáveis |

`Draft` é **estatuto GitHub**, não estado de teste. `SUCCESS` de workflow pode coexistir com SKIP ou cobrir apenas um subconjunto.

## Procedimento de compatibilidade, por ordem

1. Identificar `main`, branch de documentação, **baseline** e candidata posterior, todos com SHA. Nunca tratar branches divergentes como um só produto.
2. Ler alterações em PRs, issues e comentários posteriores; verificar se a decisão humana prevalece sobre um ADR antigo.
3. Consultar as superfícies **apenas em leitura**: `nexus/app.py`, `frontdoor.py`, `frontdoor_rules.json`, `natural_bridge.py`, `host.py`, `store.py`, `approval_binding.py`, `adapters/runner.py`, `windows_sandbox.py`, schemas e instalação conforme o claim.
4. Para cada capability, distinguir: parser reconhece? existe regra de seleção? API disponibiliza? Host autoriza? runner executa? Store aceita? existe teste? houve ensaio físico?
5. Rever cobertura e logs no SHA indicado. Não somar suites sobrepostas nem transformar mocks em serviços reais.
6. Editar só Markdown não protegido em **branch documental própria**. Sem scripts novos, workflows novos, alterações a manifestos ou ficheiros do runtime.
7. Verificar todas as referências Markdown relativas novas/alteradas, os links históricos afetados e os destinos existentes. Âncoras e URLs externos requerem verificação separada.
8. Conferir diff final contra a base documental: **apenas `.md`**, nenhuma eliminação/movimento de originais, nenhum ficheiro de código alterado.
9. Registar SHA, caminhos editados, provas e limitações; deixar Draft para revisão humana, sem merge automático.

## Prioridade documental

- [Constituição](../../CEREBRO_CONSTITUTION.md): invariantes;
- [Estado de código por SHA](../10-current/COMPATIBILIDADE-CODIGO-2026-10-10.md): cruzamento verificável;
- [Matriz de PRs](MATRIZ-PRS-2026-10-10.md): níveis de prova;
- [Estado operacional histórico/por ciclos](../../nexus/docs/PONTO-DE-SITUACAO.md): ler por data e SHA;
- [Histórico preservado](../99-history/README.md): evolução, não ordem de instalação.

## Proibições

Não tocar em código; não alterar testes, JSON/YAML de regras, hashes, scripts de instalação, workflows, UI executável, Kernel, Host ou Store. Não corrigir um FAIL alterando a narrativa. Não mover documentos históricos sem manifesto de caminhos/links e revisão. Não declarar copia física do PC nem ausência de segredos por amostragem. Não aplicar merges em `main` nem transportar automaticamente alterações da PR #45 para a #49.

A adequação da documentação ao **HEAD futuro** exige nova verificação quando o candidato mudar.
