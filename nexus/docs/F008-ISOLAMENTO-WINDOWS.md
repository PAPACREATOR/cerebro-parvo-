# F008 — isolamento Windows (PENDENTE)

Prioridade humana reforçada em 01-10-2026. O workflow interpret.yaml já está implementado; a fronteira de conta Windows não.

INPUT: conta padrão Nexus, área de trabalho atribuída por tarefa, ferramentas de leitura/execução, cofres e leis pertencentes ao Host/humano.
OUTPUT: testes reais demonstram escrita na área de trabalho e acesso negado aos cofres/leis pela identidade da ferramenta. Host entrega somente contexto permitido e valida outputs.
LEIS: IA sem autoridade; conta padrão sem administração; Human Gate só no Host; nenhuma migração de conhecimento sem restauro verificado.
DEPENDÊNCIAS: Windows LocalUser, ACL NTFS, processo com credenciais explícitas. Não inventar serviço permanente.

## Passos e testes

1. Criar conta padrão com palavra-passe introduzida pela pessoa na janela Windows; nunca em chat/log/Git.
2. Preparar área de ensaio com sentinelas sintéticas. Verificar SID e ausência no grupo Administradores.
3. Executar processo realmente como Nexus; provar escrita no diretório atribuído e bloqueio de leitura/escrita dos cofres e alteração de ferramentas/leis.
4. Tentar alcançar outra execução e dados fora do pacote; uma conta dedicada por si não garante isolamento entre execuções nem de rede. Registar limites e corrigir perante FAIL.
5. Só após PASS ligar a execução restrita ao Host/Conductor. Token de sessão e credenciais dos cofres não entram no processo.
6. Repetir para Notebook/Tiny: se continuarem na conta humana, o isolamento completo continua por provar.
7. Testar timeout, cancelamento, reinício e recuperação. Preservar os dados atuais até cópia/restauro demonstrado.

Estado atual: script interativo preparado, conta não criada na última verificação. Nenhum PASS de isolamento anunciado. O manifesto de hashes e os gates existentes não bloqueiam escrita direta por processos com os direitos do utilizador.

## Revalidação pedida — 01-10-2026

Cognitivo na cópia atual: PASS em 10.57 s; interpret.yaml executado por Conductor; Open Notebook/Tiny retornaram JSON candidato UNKNOWN, duas citações exatas, Canonical vazio e credencial temporária removida. A existência deste workflow foi confirmada no índice Git.

Isolamento: **FAIL reproduzível**. Um filho Python -I com process_environment do Host leu e alterou uma sentinela sintética numa pasta de cofre de ensaio. Mesmo utilizador mantém os seus direitos de ficheiros. Não foi tocado conhecimento real. A conta Nexus continua ausente na verificação. Próximo trabalho: corrigir esta fronteira, sem avançar para capacidades adicionais.

Este FAIL de requisito não desaparece com os 109 PASS da regressão existente: a suite cobre o comportamento implementado, não comprova isolamento de OS.
