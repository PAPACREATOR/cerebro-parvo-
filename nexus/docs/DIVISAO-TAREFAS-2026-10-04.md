# Divisão de tarefas — 04/10/2026, 23h Lisboa

Pedido de Pedro: localizar o trabalho das outras sessões e dividir tarefas.

| Sessão / evidência | Responsabilidade | Próximo trabalho | Estado |
|---|---|---|---|
| Sessão principal PR21 | Exterior Nexus: Kernel/Host/Store, Folha/ELIZA/LanguageTool, MCP, tiny separado, allowlist, Human Gate | Validar integração dos contratos entregues por Work; seguir ordem operacional própria | Atividade recente comprovada por commits/comentários; execução atual do chat não observável |
| Esta sessão Work, PR23 | Interior Open Notebook: avatar/podcast/FFmpeg, modelos, wrappers finos MCP e testes | Sincronizar avatar sobre21; repetir regressão; depois wrappers do podcast existente | Avatar entregue; sincronização nesta alteração; wrappers gerais ainda pendentes |
| Pedro/Codex Windows | C:\Nexus-Lab, modelos/hardware reais e instalação | Executar gates físicos após validação GitHub | Não disparado nesta sessão |
| Revisor interno desta sessão | Revisão independente de bases, paths e gates | Conferir a divisão e prevenir cópias antigas | Revisão read-only; não é um dos outros chats |

## Reserva de ficheiros

Work: `nexus/lab/open_notebook_avatar/**`, workflow avatar, relatório/evidência avatar. Estado global só com reconciliação manual.

Principal: `nexus/mcp_client.py`, `nexus/tiny_classifier.py`, `nexus/requirements.txt`, fixtures/testes MCP/tiny, Kernel/Host/Store e plano operacional atual. Work não os substitui com cópias herdadas de22.

Nenhuma mudança em main ou branch21 por esta sessão. Baseline17 preservada como genealogia; PR22 fechada não é continuação autoritativa. PR19/20 são experiências históricas, não novas tarefas atribuídas.

## Interface entre responsáveis

Servidor adicional stdio `python -m notebook_avatar.mcp_server`, origem REST fixa localhost:5055.

- `render_podcast_avatar(episode_id:str, avatar:str, device='cpu', batch_size=8) -> dict`: gera/recupera MP4+proveniência do episódio existente. Efeito apenas output configurado, sem modificar áudio/retrato de origem.
- `get_podcast_avatar(job_id:str) -> dict`: leitura/validação, não chama IA nem render novamente.
- Saída: job_id; input hashes; output file/hash/duration/bytes; status PASS técnico; authority UNTRUSTED; outcome candidate. Autoridade permanece no Kernel/Humano.

Principal valida allowlist e circuito real antes de integrar. Work não reconstrói TTS/podcast. Ainda pendente expor operações gerais podcast existentes via wrappers finos; consulta não cria autorização automática para delete.

## Evidência e reconhecimento

PR21 HEAD consultado0753f573f2dee739a4e43a5e255a4999319cc605. Aviso naPR23: comentário5984504095. Divisão publicada naPR21: comentário5984901664.

Consultar comentários recentes e HEAD antes de cada edição; publicar base, paths, testes e próximo gate. Reserva publicada não prova leitura/aceitação por outro chat. Não existe API disponível de estado em tempo real dos outros chats.
