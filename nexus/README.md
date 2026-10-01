# Nexus Minimal — protótipo Windows

Folha → Host Python → Microsoft Conductor → YAML → ferramenta → JSON validado → Creative. A promoção para Canonical exige confirmação humana ligada ao conteúdo.

## Arranque determinístico

Requisitos: Windows, Python 3.12 e Git. Na raiz do repositório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r nexus/requirements.txt
.\.venv\Scripts\python.exe -m nexus.app
```

A Folha abre no navegador, apenas em 127.0.0.1. Verificar texto/anexo calcula SHA-256 por Windows/.NET e Python e compara os resultados. Este circuito não chama IA. Os dados ficam em `nexus/runtime/`, excluído do Git. Não executar duas instâncias sobre o mesmo diretório de dados.

## Cognição opcional

A opção Interpretar requer Open Notebook configurado em `http://127.0.0.1:5055`, com modelo local e transformação que devolva o contrato `schemas/cognitive.json`: título, resumo e citações exatas. Criar localmente `nexus/runtime/open-notebook.json` com quatro campos: `base_url`, `password`, `model_id`, `transformation_id`. A password é a da API local; nunca a guardar no Git. Esta versão não instala nem configura automaticamente a bancada.

Ensaio anterior: Open Notebook 1.14.0, SurrealDB 2.7.0 e Qwen3-4B Q4_K_M via llama.cpp b6500. Texto UTF-8 até 6000 caracteres; PDF/DOCX ainda não suportados no ramo cognitivo. Saída sempre candidata UNKNOWN. Formato e citações verificáveis não provam veracidade.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pip install -r nexus/requirements-test.txt
.\.venv\Scripts\python.exe -m pytest nexus/tests -q -o pythonpath=.
```

A suite combina testes reais de Conductor/PowerShell com falhas controladas. Não exige modelo nem Notebook. O teste cognitivo real é evidência separada, descrita em `docs/F005-COGNICAO.md`.

## Organização

- `app.py`, `host.py`: Folha local e delegação ao Conductor.
- `store.py`, `approval_binding.py`: Creative, gate e recuperação de aprovação.
- `laws/`, `schemas/`, `processes/`: leis, contratos e workflows.
- `adapters/`: ferramentas determinísticas e chamada delimitada ao Notebook.
- `ui/`: interface; `tests/`: verificação; `docs/`: contratos e evidência histórica datada.

Consultar [estado revisto](docs/PUBLICACAO-2026-10-01.md) antes dos relatórios anteriores. Preferência: self-hosted, serviços opcionais e mínimo consumo. O Host não incorpora um motor de agentes nem um modelo.

## Limites conhecidos

O gate protege o percurso da aplicação; ainda não há isolamento Windows por conta/ACL entre ferramentas e cofres. Um processo com os mesmos direitos do utilizador pode alterar ficheiros. O manifesto verifica alterações acidentais, não é uma raiz de confiança externa. A recuperação testada não substitui backup/restauro. Wiki, integração LibreOffice/Zotero/LanguageTool/web, desenho e música permanecem pendentes.

Licença do código Nexus: [PolyForm Noncommercial 1.0.0](../LICENSE). Dependências mantêm as suas licenças e não são redistribuídas nesta pasta.
