# Nexus Minimal — protótipo Windows

Folha → Kernel/Host Python → adapter na fronteira nativa Windows → JSON validado → Creative. MCP externo é transporte opcional. A promoção para Canonical exige confirmação humana ligada ao conteúdo.

Estado, SHA validado e falhas pendentes: [ponto de situação único](docs/PONTO-DE-SITUACAO.md). A linha de produto já está integrada em `main` pelas PRs #50/#51/#53/#55. A [reconciliação de GitHub](docs/ESTADO-CONSOLIDACAO-2026-10-11.md) distingue os candidatos históricos do runtime atual e dos testes ainda pendentes.

## Arranque determinístico

Requisitos: Windows, Python 3.12, Git e checkout oficial limpo. Conferir o SHA exato do `main` que se pretende autorizar e os gates associados; não aceitar automaticamente o antigo SHA da PR #32. Na raiz desse checkout:

```powershell
$accepted = git rev-parse HEAD
powershell.exe -NoProfile -File nexus/windows/bootstrap-nexus-local.ps1 -RepoRoot (Get-Location).Path -ExpectedHead $accepted -AuthorizePrepare
```

O bootstrap core existente reutiliza preparação, inventário e plano; cria o atalho Nexus.lnk com o launcher e binding fora do repositório. HEAD diferente, origin incorreto ou checkout alterado recusam o arranque. Uma atualização exige aceitar explicitamente o novo SHA e repetir o bootstrap. O bundle completo é opcional e depende da aceitação no PC.

O core exige jsonschema; MCP/trio estão em `requirements-mcp.txt` para integrações externas e testes de protocolo. O bootstrap instala também dependências de teste para verificar gates. A Folha mantém dez processos declarados e um roteador determinístico de propostas exatas, ligados à confirmação pré-execução. As sete intenções da Front Door **não** concedem autorização genérica para ferramentas desconhecidas; ambiguidades ficam por esclarecer. A pesquisa `?? pesquisar termo` devolve apenas resultados Canonical aprovados; `?? pesquisar rascunhos termo` permite incluir Creative explicitamente. Writer/Sandy já foi integrado; continuam pendentes aceitação física e provas finais das ferramentas reais.

A Folha abre no navegador, apenas em 127.0.0.1. Verificar texto/anexo calcula SHA-256 por Windows CNG e Python/hashlib e compara os resultados. Este circuito não chama IA. Os dados ficam em `nexus/runtime/`, excluído do Git. O arranque reserva a memória: uma segunda instância com os mesmos dados é recusada antes de recuperar ou alterar pedidos. Se a janela for encerrada normalmente, a tarefa ativa termina antes de libertar a memória. Um crash liberta o bloqueio no sistema operativo; o próximo arranque faz a recuperação existente. Não apagar `.nexus.lock`: a sua existência não indica que a aplicação esteja aberta.

[Contrato e testes do arranque único](docs/F011-ARRANQUE-UNICO.md). Usar um diretório local; esta proteção não é isolamento Windows nem coordenação com versões antigas do Nexus.

[Correção do hash no ambiente reduzido e prova Windows](docs/F012-HASH-WINDOWS-ISOLADO.md): 1154 testes passaram no runner; inclui o percurso HTTP até ao gate e os dois workflows de hash, sem depender de `ConvertTo-Json`.

## Cognição opcional

A opção Interpretar requer Open Notebook configurado em `http://127.0.0.1:5055`, com modelo local e transformação que devolva o contrato `schemas/cognitive.json`: título, resumo e citações exatas. Criar localmente `nexus/runtime/open-notebook.json` com quatro campos: `base_url`, `password`, `model_id`, `transformation_id`. A password é a da API local; nunca a guardar no Git. Esta versão não instala nem configura automaticamente a bancada.

Ensaio anterior: Open Notebook 1.14.0, SurrealDB 2.7.0 e Qwen3-4B Q4_K_M via llama.cpp b6500. Texto UTF-8 até 6000 caracteres; PDF/DOCX ainda não suportados no ramo cognitivo. Saída sempre candidata UNKNOWN. Formato e citações verificáveis não provam veracidade.

## Revisão de português opcional

Com Java e LanguageTool instalados, criar no diretório de dados `languagetool.json` com `java` (caminho absoluto de `java.exe`) e `jar` (caminho absoluto de `languagetool-commandline.jar`). Esta configuração é administrativa e local; não pode ser fornecida pelo modelo. Escolher **Rever português** na Folha. Aceita texto UTF-8 até 6000 caracteres. Usa CLI, sem servidor nem IA; apresenta sugestões em Creative e conserva o original. Sem alertas não significa texto correto.

[Evidência e limites desta integração](docs/F006-LANGUAGETOOL.md).

## Conversão PDF opcional

Com LibreOffice e Sandy instalados e verificados, criar no diretório de dados `libreoffice.json` com **exatamente dois campos**: `executable`, caminho absoluto de `soffice.com`, e `sandy`, caminho absoluto do binário `sandy.exe` da versão aprovada. A instalação e os hashes têm de corresponder aos contratos atuais; não executar Writer sem essa validação. Selecionar **Converter para PDF** e anexar ODT ou DOCX até 2 MB. O PDF fica em Creative e pode ser descarregado. A aprovação inclui o hash do ficheiro; PDF alterado bloqueia download/promoção. Usar inicialmente documentos confiáveis de ensaio. ODT teve prova real; DOCX ainda precisa de ensaio nesta versão.

[Contrato, testes e limites](docs/F007-LIBREOFFICE.md). O timeout original da PR #32 é evidência histórica. Posteriormente a PR #50 teve **PASS real do Writer/Sandy em Windows** no seu SHA; isso não prova a instalação no PC pessoal nem substitui a repetição no candidato final, como se explica na issue #36. O Writer editorial completo (livros, estilos, paginação, gutter, viúvas/órfãos, imagens, sumário e round-trip) tem contrato separado em [CAPABILITY-WRITER-EDITORIAL.md](docs/CAPABILITY-WRITER-EDITORIAL.md) e ainda não deve ser confundido com a conversão PDF já provada.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pip install -r nexus/requirements-test.txt
.\.venv\Scripts\python.exe -m pytest nexus/tests -q -o pythonpath=.
```

A suite combina testes reais de Python/MCP/PowerShell com falhas controladas. Não exige modelo nem Notebook. O teste cognitivo real é evidência separada, descrita em `docs/F005-COGNICAO.md`. O workflow GitHub **Nexus Windows** executa esta suite num runner Windows; a auditoria histórica continua separada. Um PASS do runner não prova as instalações do PC pessoal.

## Organização

[Estado, inventário documental e próximas validações](docs/PONTO-DE-SITUACAO.md).

- `app.py`, `host.py`: Folha local e execução governada pelo Host/Kernel. O `server.js` da raiz é gateway Node **opcional**, sem Store, execução ou aprovação própria; o servidor Python é suficiente para a Folha.
- `store.py`, `approval_binding.py`: Creative, gate e recuperação de aprovação.
- `laws/`, `schemas/`: leis e contratos; o executor candidato é Python, sem a antiga pasta de workflows YAML.
- `adapters/`: ferramentas determinísticas e chamada delimitada ao Notebook.
- `ui/`: interface; `tests/`: verificação; `docs/`: contratos e evidência histórica datada.

Consultar primeiro o [ponto de situação revisto](docs/PONTO-DE-SITUACAO.md) e os contratos [F011](docs/F011-ARRANQUE-UNICO.md), [F012](docs/F012-HASH-WINDOWS-ISOLADO.md) e [F013](docs/F013-PROVENIENCIA-INVERSA.md). O [relatório de publicação](docs/PUBLICACAO-2026-10-01.md) conserva a revisão de 01-10. Preferência: self-hosted, serviços opcionais e mínimo consumo. O Host não incorpora um motor de agentes nem um modelo.

## Multimédia externa

A [extensão avatar OpenNotebook](lab/open_notebook_avatar/README.md) transforma áudio existente e retrato em MP4 por API/MCP. A geração real curta em CPU Linux tem evidência própria; a suite CI substitui o modelo aprendido. Pedido escrito na Folha até vídeo final, episódio longo e Windows/GPU exigem validação específica.

ACE-Step/Forge são ferramentas externas com instalador e health checks. Consultar o ponto de situação antes de usar `windows/sync-nexus-pc.ps1`: o script sincroniza a branch corrente, que pode ter gates pendentes. Não confundir um health check com geração de imagem/música comprovada.

## Limites conhecidos

O runtime lançado pelo Host já usa fronteira nativa Windows/AppContainer LPAC + Job Object nos percursos validados. Isto limita os processos que o Host lança; não promete controlar todo o Windows nem ferramentas externas já iniciadas fora dessa fronteira. Provisioning protegido de ferramentas externas continua pendente. O manifesto verifica integridade do código selado, não substitui uma raiz de confiança externa. Recuperação testada não substitui backup/restauro. Zotero, Writer editorial completo, modelos/GPU físicos e algumas capabilities multimédia permanecem pendentes.

Licença do código Nexus: [PolyForm Noncommercial 1.0.0](../LICENSE). Dependências mantêm as suas licenças e não são redistribuídas nesta pasta.
