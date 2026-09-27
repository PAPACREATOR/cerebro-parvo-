# Ambiente de auditoria e desenvolvimento

O ambiente usado nesta reconciliação foi Linux, Python 3.12.14 e pytest 8.3.5 numa venv isolada. O pacote recebido declara Python >=3.10; isto não demonstra compatibilidade em todas essas versões nem no Windows alvo.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-auditoria.txt
.venv/bin/python ferramentas/verificar_documentacao.py
cd implementacao/candidata-2026-09-27
../../.venv/bin/python -m pytest -q --color=no
```

Em Windows, usar o Python do ambiente em `.venv\Scripts\python.exe`. Esse procedimento ainda não foi executado no computador de Pedro. Não instalar globalmente nem reinstalar ferramentas já verificadas. Testes do produto usam dados artificiais e diretórios temporários.

Activepieces, LibreOffice, Zotero, LanguageTool, Second-Brain e IA não foram instalados/integrados nesta tarefa. Instalar componentes apenas na etapa cujo contrato os exija e com versão, proveniência, permissões, teste e recuperação definidos.
