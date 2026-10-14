# Especificação mínima — Grafo sem visual

## Princípio

Esta especificação **não altera** Kernel, Host, Store, Folha, FTS5, Human Gate nem qualquer teste existente.

O grafo é apenas uma **camada derivada e reconstrutível**, como o FTS5.

- Sem interface visual.
- Sem IA a criar relações.
- Sem graph database.
- Sem cloud.
- Sem alteração ao código atual.
- SQLite apenas, num ficheiro separado.

## Objetivo

Permitir que o Nexus encontre não só texto parecido, mas também relações relevantes:

- cita;
- deriva de;
- contradiz;
- depende de;
- foi aprovado por;
- refere.

## Ficheiro novo

Criar apenas:

```text
nexus/graph/graph_minimo.py
nexus/graph/README.md
```

Nenhum ficheiro existente é modificado nesta fase.

## Base de dados

Ficheiro:

```text
nexus/graph/graph.sqlite
```

É derivado e pode ser apagado/reconstruído.

## Tabelas

```sql
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  tipo TEXT NOT NULL,
  titulo TEXT NOT NULL,
  fonte_path TEXT,
  conteudo_hash TEXT,
  estado TEXT NOT NULL DEFAULT 'creative'
);

CREATE TABLE IF NOT EXISTS edges (
  id TEXT PRIMARY KEY,
  origem_id TEXT NOT NULL,
  destino_id TEXT NOT NULL,
  relacao TEXT NOT NULL,
  propriedades TEXT,
  criado_em TEXT NOT NULL,
  aprovado_por TEXT,
  UNIQUE(origem_id, destino_id, relacao)
);

CREATE INDEX IF NOT EXISTS idx_edges_origem ON edges(origem_id);
CREATE INDEX IF NOT EXISTS idx_edges_destino ON edges(destino_id);
```

## Tipos de nós

Apenas estes, no início:

- `nota`
- `fonte`
- `decisao`
- `projeto`
- `pessoa`
- `ideia`

## Tipos de relação

Apenas estes, no início:

- `cita`
- `deriva_de`
- `contradiz`
- `depende_de`
- `refere`
- `aprovado_por`

## Regras

1. Uma relação só existe se tiver origem e destino válidos.
2. Uma relação canónica só entra após aprovação humana.
3. Relações em Creative podem ser criadas manualmente ou por processo determinístico.
4. A IA pode sugerir uma relação, mas nunca criá-la diretamente.
5. Similaridade não cria relação.
6. O grafo pode ser apagado e reconstruído sem perda de conhecimento.
7. Nenhuma relação altera o conteúdo original.

## Funções mínimas

```python
def criar_node(id, tipo, titulo, fonte_path=None, conteudo_hash=None, estado="creative")
def criar_edge(origem_id, destino_id, relacao, propriedades=None, aprovado_por=None)
def backlinks(node_id)
def ligacoes(node_id)
def vizinhanca(node_id, saltos=1)
```

## Consulta mínima

```sql
-- Ligações de saída
SELECT destino_id, relacao FROM edges WHERE origem_id = ?;

-- Backlinks
SELECT origem_id, relacao FROM edges WHERE destino_id = ?;

-- Vizinhança a 1 salto
SELECT destino_id, relacao FROM edges WHERE origem_id = ?
UNION
SELECT origem_id, relacao FROM edges WHERE destino_id = ?;
```

## Integração futura

Só depois de o grafo mínimo estar testado:

1. A pesquisa FTS5 pode devolver resultados.
2. O grafo pode expandir esses resultados com relações a 1 salto.
3. A Folha mostra: resultado + relações + proveniência.
4. Nada é promovido para Canonical sem Human Gate.

## Critério de sucesso

- Criar 10 nós e 10 relações de teste.
- Apagar o `graph.sqlite`.
- Reconstruir o grafo a partir dos ficheiros de origem.
- Obter exatamente os mesmos backlinks e relações.
- Confirmar que nenhum ficheiro existente foi alterado.
- Confirmar que nenhuma relação canónica foi criada sem aprovação humana.
