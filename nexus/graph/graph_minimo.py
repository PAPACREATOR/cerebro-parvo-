"""Grafo mínimo do Nexus — sem visual, sem IA, sem dependências externas.

Camada derivada e reconstrutível. Não altera Kernel, Host, Store, Folha,
FTS5, Human Gate nem qualquer teste existente.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

RELACOES = {
    "cita",
    "deriva_de",
    "contradiz",
    "depende_de",
    "refere",
    "aprovado_por",
}

TIPOS_NODE = {
    "nota",
    "fonte",
    "decisao",
    "projeto",
    "pessoa",
    "ideia",
}


class GraphMinimo:
    def __init__(self, db_path: str | Path = "nexus/graph/graph.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript(
                """
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

                CREATE INDEX IF NOT EXISTS idx_edges_origem
                  ON edges(origem_id);

                CREATE INDEX IF NOT EXISTS idx_edges_destino
                  ON edges(destino_id);
                """
            )

    def criar_node(
        self,
        node_id: str,
        tipo: str,
        titulo: str,
        fonte_path: str | None = None,
        conteudo_hash: str | None = None,
        estado: str = "creative",
    ) -> str:
        if tipo not in TIPOS_NODE:
            raise ValueError(f"Tipo de nó não permitido: {tipo}")
        if estado not in {"creative", "canonical", "arquivado"}:
            raise ValueError(f"Estado não permitido: {estado}")

        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO nodes
                (id, tipo, titulo, fonte_path, conteudo_hash, estado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (node_id, tipo, titulo, fonte_path, conteudo_hash, estado),
            )
        return node_id

    def criar_edge(
        self,
        origem_id: str,
        destino_id: str,
        relacao: str,
        propriedades: dict | None = None,
        aprovado_por: str | None = None,
    ) -> str:
        if relacao not in RELACOES:
            raise ValueError(f"Relação não permitida: {relacao}")
        if origem_id == destino_id:
            raise ValueError("Uma relação não pode ligar um nó a si próprio.")

        with self._connect() as con:
            origem = con.execute(
                "SELECT 1 FROM nodes WHERE id = ?", (origem_id,)
            ).fetchone()
            destino = con.execute(
                "SELECT 1 FROM nodes WHERE id = ?", (destino_id,)
            ).fetchone()

            if not origem:
                raise ValueError(f"Nó de origem não existe: {origem_id}")
            if not destino:
                raise ValueError(f"Nó de destino não existe: {destino_id}")

            destino_estado = con.execute(
                "SELECT estado FROM nodes WHERE id = ?", (destino_id,)
            ).fetchone()[0]

            if destino_estado == "canonical" and not aprovado_por:
                raise ValueError(
                    "Relação para nó canónico exige aprovação humana."
                )

            edge_id = uuid.uuid4().hex
            con.execute(
                """
                INSERT OR IGNORE INTO edges
                (id, origem_id, destino_id, relacao, propriedades,
                 criado_em, aprovado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge_id,
                    origem_id,
                    destino_id,
                    relacao,
                    json.dumps(propriedades, ensure_ascii=False)
                    if propriedades
                    else None,
                    datetime.now(timezone.utc).isoformat(),
                    aprovado_por,
                ),
            )
        return edge_id

    def ligacoes(self, node_id: str) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT destino_id, relacao, propriedades
                FROM edges WHERE origem_id = ?
                """,
                (node_id,),
            ).fetchall()
        return self._rows(rows, "destino_id")

    def backlinks(self, node_id: str) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT origem_id, relacao, propriedades
                FROM edges WHERE destino_id = ?
                """,
                (node_id,),
            ).fetchall()
        return self._rows(rows, "origem_id")

    def vizinhanca(self, node_id: str, saltos: int = 1) -> list[dict]:
        if saltos not in {1, 2}:
            raise ValueError("Apenas 1 ou 2 saltos são permitidos.")

        with self._connect() as con:
            rows = con.execute(
                """
                WITH RECURSIVE vizinho(id, profundidade) AS (
                  SELECT ?, 0
                  UNION
                  SELECT
                    CASE WHEN e.origem_id = v.id
                         THEN e.destino_id ELSE e.origem_id END,
                    v.profundidade + 1
                  FROM edges e
                  JOIN vizinho v
                    ON e.origem_id = v.id OR e.destino_id = v.id
                  WHERE v.profundidade < ?
                )
                SELECT DISTINCT id, profundidade FROM vizinho
                WHERE id != ?
                ORDER BY profundidade, id;
                """,
                (node_id, saltos, node_id),
            ).fetchall()
        return [{"id": row[0], "saltos": row[1]} for row in rows]

    @staticmethod
    def _rows(rows, campo_id: str) -> list[dict]:
        resultado = []
        for destino, relacao, propriedades in rows:
            resultado.append(
                {
                    campo_id: destino,
                    "relacao": relacao,
                    "propriedades": json.loads(propriedades)
                    if propriedades
                    else None,
                }
            )
        return resultado


if __name__ == "__main__":
    g = GraphMinimo()
    g.criar_node("nota-1", "nota", "Capítulo 3")
    g.criar_node("fonte-1", "fonte", "Entrevista A")
    g.criar_edge("nota-1", "fonte-1", "cita")
    print("Backlinks de fonte-1:", g.backlinks("fonte-1"))
    print("Vizinhança de nota-1:", g.vizinhanca("nota-1"))
