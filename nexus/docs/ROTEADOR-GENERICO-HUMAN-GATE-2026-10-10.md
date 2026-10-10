# Nexus — contrato de roteamento por capacidades (10-10-2026)

## Evidência do Writer existente (antes da generalização)

1. Folha `/api/interpret` consulta `frontdoor.parse`, sem execução.
2. `/api/prepare-run` traduz texto por `propose_operation` e valida pedido/anexo; emite ticket temporário de uso único vinculado ao SHA-256 do pedido completo.
3. `/api/confirm-run` consome o ticket, exige confirmação humana literal e verifica novamente os bytes e o SHA; só então chama `Host.start`.
4. `host.py` valida sessão, integridade, exclusão de execução concorrente; `Store.create` grava original, pedido, proveniência inicial e estado.
5. `Host._run` valida o original e o processo, marca `EXECUTING` antes de uma única chamada externa; `prepare_task` fornece apenas dados/capacidades delimitados.
6. Writer (`book`/`convert_pdf`): `writer_sandy.convert` com Sandy LPAC/Job; outros processos: `runner.py` em `launch_confined` no Windows. O retorno `{result,trace}` é validado, PDF copiado após verificação de hash, `Store.accept` materializa candidato em Creative.
7. `/api/prepare` volta a verificar candidato e conteúdo, emite ticket de revisão SHA-256; `/api/approve` só chama `Store.promote` com `HumanDecision` vinculado ao conteúdo após confirmação humana. Negação/expiração/mudança/repetição não executam nem promovem.

```text
Pedido humano na Folha
   │
   ▼
Parser determinístico → proposta única de capability autorizada → preflight do adaptador
   │
   ▼
PREPARE-RUN (preview, SHA do input + ticket com TTL)
   │
   ├── negar / ambíguo / alterado / expirado → BLOCKED, sem executar
   ▼
CONFIRM-RUN (human TRUE) → Host.start → Store/Kernel + integridade
   │
   ▼
Preparação confinada → adaptador pinado (Writer Sandy; restantes runner/LPAC)
   │
   ▼
Resultado {result, trace} + artefactos validados → Store.accept → Creative
   │
   ▼
PREPARE + APPROVE (segunda confirmação humana vinculada ao SHA)
   │
   ▼
Canonical + proveniência; restart nunca repete ferramenta
```

## Interface genérica — sem alterar Kernel nem Store

- **Capacidade** = processo já admitido em `laws/policy.json`, `schemas/request.json`, `runner.PROCESS_TO_TOOL` e `runner.PROCESS_FILES`. O identificador vem de um conjunto finito de **N** adaptadores inspecionados; não pode ser nome livre, caminho, executável ou sugestão da IA.
- **Seleção** = texto da Folha + prefixo/intent + regras de operação exatas, determinísticas, sem modelo e com recusa perante zero ou várias correspondências. Uma regra nunca concede autoridade por si.
- **Adaptador** = `name/process`, `tool`, `validate_input(filename, original_bytes)`, `preview`; não dispõe de Store, tickets nem capacidade de chamar diretamente o Host.
- **Pré-validação** = entrada no limite 2 MiB, UTF-8 obrigatório nas capacidades textuais; extensão e ZIP DOCX/ODT validados para Writer; cada ferramenta conserva validações internas no seu sandbox.
- **Execução** = apenas `Host.start` após ticket humano; Host confirma integridade, estado, processo e confina o executor já existente; adaptadores nunca recebem autoridade para escrever em Canonical.
- **Resultado** = envelope `{result,trace}` sujeito a `schemas/result.json`, impressão digital do processo e verificação de artefactos. Primeiro Creative; segundo ticket e `HumanDecision` antes de Canonical.
- **Vários passos** = cada execução externa precisa do seu próprio ticket de pré-execução; a transição de um resultado para o pedido seguinte exige inspeção/decisão humana. Não há execução automática em cadeia.
- **Fail closed** = processo desconhecido, ferramenta não instalada/configurada, entrada suspeita, pedido contraditório, negação, ticket repetido/expirado, alteração do original, saída inválida ou falta de isolamento → BLOCKED/FAIL, nunca PASS.
- **Limite** = acrescentar um processo além dos 10 atuais exige alterar contratos/leis e passar revisão humana; esta versão não adiciona processos novos ao Kernel/Store.

## Distinção entre funcionalidades reais e propostas

- Writer converte ODT/DOCX em PDF quando Writer+Sandy estão fisicamente instalados.
- OpenNotebook `interpret`, `video`, `podcast`, `visual_podcast` requer serviço local configurado e fornece candidato; não prova geração física de vídeo/podcast.
- LanguageTool `proofread` requer Java e JAR local, verificados pelo Host.
- `music` produz especificação ACE-Step, **não gera áudio**.
- `web` produz uma consulta rastreável, **não pesquisa a internet**.
- `verify` calcula/verifica hashes sem modelo.

## Estado da validação

Esta especificação não declara o produto concluído. A integração final depende de testes unitários, E2E Windows de **duas ferramentas diferentes e duas decisões por ferramenta**, teste negativo, CI completo no mesmo SHA e revisão de falhas existentes. A `main` não deve ser alterada até todas as verificações passarem.
