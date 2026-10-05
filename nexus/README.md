# Nexus Minimal — protótipo Windows

Folha → Kernel/Host Python → MCP/ferramenta → JSON validado → Creative. A promoção para Canonical exige confirmação humana ligada ao conteúdo.

Estado, SHA validado e falhas pendentes: [ponto de situação único](docs/PONTO-DE-SITUACAO.md). A branch candidata da [PR #23](https://github.com/PAPACREATOR/cerebro-parvo-/pull/23) ainda não foi integrada em `main`.

## Arranque determinístico

Requisitos: Windows, Python 3.12 e Git. Na raiz do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r nexus/requirements.txt
.\.venv\Scripts\python.exe -m nexus.app
```

A Folha abre no navegador, apenas em 127.0.0.1. Verificar texto/anexo calcula SHA-256 por Windows/.NET e Python e compara os resultados. Este circuito não chama IA. Os dados ficam em `nexus/runtime/`, excluído do Git. O arranque reserva a memória: uma segunda instância com os mesmos dados é recusada antes de recuperar ou alterar pedidos. Se a janela for encerrada normalmente, a tarefa ativa termina antes de libertar a memória. Um crash liberta o bloqueio no sistema operativo; o próximo arranque faz a recuperação existente. Não apagar `.nexus.lock`: a sua existência não indica que a aplicação esteja aberta.

[Contrato e testes do arranque único](docs/F011-ARRANQUE-UNICO.md). Usar um diretório local; esta proteção não é isolamento Windows nem coordenação com versões antigas do Nexus.

[Correção do hash no ambiente reduzido e prova Windows](docs/F012-HASH-WINDOWS-ISOLADO.md): 1154 testes passaram no runner; inclui o percurso HTTP até ao gate e os dois workflows de hash, sem depender de `ConvertTo-Json`.

## Cognição opcional

A opção Interpretar requer Open Notebook configurado em `http://127.0.0.1:5055`, com modelo local e transformação que devolva o contrato `schemas/cognitive.json`: título, resumo e citações exatas. Criar localmente `nexus/runtime/open-notebook.json` com quatro campos: `base_url`, `password`, `model_id`, `transformation_id`. A password é a da API local; nunca a guardar no Git. Esta versão não instala nem configura automaticamente a bancada.

Ensaio anterior: Open Notebook 1.14.0, SurrealDB 2.7.0 e Qwen3-4B Q4_K_M via llama.cpp b6500. Texto UTF-8 até 6000 caracteres; PDF/DOCX ainda não suportados no ramo cognitivo. Saída sempre candidata UNKNOWN. Formato e citações verificáveis não provam veracidade.

## Revisão de português opcional

Com Java e LanguageTool instalados, criar no diretório de dados `languagetool.json` com `java` (caminho absoluto de `java.exe`) e `jar` (caminho absoluto de `languagetool-commandline.jar`). Esta configuração é administrativa e local; não pode ser fornecida pelo modelo. Escolher **Rever português** na Folha. Aceita texto UTF-8 até 6000 caracteres. Usa CLI, sem servidor nem IA; apresenta sugestões em Creative e conserva o original. Sem alertas não significa texto correto.

[Evidência e limites desta integração](docs/F006-LANGUAGETOOL.md).

## Conversão PDF opcional

Com LibreOffice instalado, criar no diretório de dados `libreoffice.json` com o campo `executable`: caminho absoluto de `soffice.com`. Selecionar **Converter para PDF** e anexar ODT ou DOCX até 2 MB. O PDF fica em Creative e pode ser descarregado. A aprovação inclui o hash do ficheiro; PDF alterado bloqueia download/promoção. Usar inicialmente documentos confiáveis de ensaio. ODT teve prova real; DOCX ainda precisa de ensaio nesta versão.

[Contrato, testes e limites](docs/F007-LIBREOFFICE.md).

## Testes

```powershell
.\.venv\Scripts\python.exe -m pip install -r nexus/requirements-test.txt
.\.venv\Scripts\python.exe -m pytest nexus/tests -q -o pythonpath=.
```

A suite combina testes reais de Python/MCP/PowerShell com falhas controladas. Não exige modelo nem Notebook. O teste cognitivo real é evidência separada, descrita em `docs/F005-COGNICAO.md`. O workflow GitHub **Nexus Windows** executa esta suite num runner Windows; a auditoria histórica continua separada. Um PASS do runner não prova as instalações do PC pessoal.

## Organização

[Estado, inventário documental e próximas validações](docs/PONTO-DE-SITUACAO.md).

- `app.py`, `host.py`: Folha local e execução governada pelo Kernel.
- `store.py`, `approval_binding.py`: Creative, gate e recuperação de aprovação.
- `laws/`, `schemas/`: leis e contratos; o executor candidato é Python, sem a antiga pasta de workflows YAML.
- `adapters/`: ferramentas determinísticas e chamada delimitada ao Notebook.
- `ui/`: interface; `tests/`: verificação; `docs/`: contratos e evidência histórica datada.

Consultar primeiro o [ponto de situação revisto](docs/PONTO-DE-SITUACAO.md) e os contratos [F011](docs/F011-ARRANQUE-UNICO.md), [F012](docs/F012-HASH-WINDOWS-ISOLADO.md) e [F013](docs/F013-PROVENIENCIA-INVERSA.md). O [relatório de publicação](docs/PUBLICACAO-2026-10-01.md) conserva a revisão de 01-10. Preferência: self-hosted, serviços opcionais e mínimo consumo. O Host não incorpora um motor de agentes nem um modelo.

## Multimédia externa

A [extensão avatar OpenNotebook](lab/open_notebook_avatar/README.md) transforma áudio existente e retrato em MP4 por API/MCP. A geração real curta em CPU Linux tem evidência própria; a suite CI substitui o modelo aprendido. Pedido escrito na Folha até vídeo final, episódio longo e Windows/GPU exigem validação específica.

ACE-Step/Forge são ferramentas externas com instalador e health checks. Consultar o ponto de situação antes de usar `windows/sync-nexus-pc.ps1`: o script sincroniza a branch corrente, que pode ter gates pendentes. Não confundir um health check com geração de imagem/música comprovada.

## Limites conhecidos

O gate protege o percurso da aplicação; ainda não há isolamento Windows por conta/ACL entre ferramentas e cofres. Um processo com os mesmos direitos do utilizador pode alterar ficheiros. O manifesto verifica alterações acidentais, não é uma raiz de confiança externa. A recuperação testada não substitui backup/restauro. Wiki, integração Zotero/web, desenho e música permanecem pendentes.

Licença do código Nexus: [PolyForm Noncommercial 1.0.0](../LICENSE). Dependências mantêm as suas licenças e não são redistribuídas nesta pasta.
