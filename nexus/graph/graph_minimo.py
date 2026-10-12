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
        with self._connect() as con:
            actual = con.execute(
                "SELECT id FROM edges WHERE origem_id = ? AND destino_id = ? AND relacao = ?",
                (origem_id, destino_id, relacao),
            ).fetchone()
        return actual[0]

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


    def exportar_json(self) -> str:
        """Exporta apenas o índice derivado; não exporta a autoridade do Store."""
        with self._connect() as con:
            nodes = [dict(zip(
                ("id", "tipo", "titulo", "fonte_path", "conteudo_hash", "estado"), row
            )) for row in con.execute(
                "SELECT id,tipo,titulo,fonte_path,conteudo_hash,estado FROM nodes ORDER BY id"
            )]
            edges = [dict(zip(
                ("id", "origem_id", "destino_id", "relacao", "propriedades",
                 "criado_em", "aprovado_por"),
                (*row[:4], json.loads(row[4]) if row[4] else None, *row[5:])
            )) for row in con.execute(
                "SELECT id,origem_id,destino_id,relacao,propriedades,criado_em,aprovado_por "
                "FROM edges ORDER BY id"
            )]
        return json.dumps({"version": 1, "nodes": nodes, "edges": edges},
                          ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def reconstruir_json(self, documento: str | bytes | dict) -> None:
        """Valida integralmente antes de substituir, numa única transação.

        Este JSON é um índice não autoritativo. Nunca promove conteúdo a Canonical.
        """
        if isinstance(documento, (str, bytes)):
            if len(documento) > 8_000_000:
                raise ValueError("Índice demasiado grande.")
            try:
                def sem_duplicados(pares):
                    d = {}
                    for k, v in pares:
                        if k in d:
                            raise ValueError("Chave JSON duplicada.")
                        d[k] = v
                    return d
                documento = json.loads(documento, object_pairs_hook=sem_duplicados,
                                       parse_constant=lambda _: (_ for _ in ()).throw(
                                           ValueError("Valor JSON inválido.")))
            except (UnicodeError, json.JSONDecodeError) as error:
                raise ValueError("JSON inválido.") from error
        if (type(documento) is not dict or set(documento) !=
                {"version", "nodes", "edges"} or type(documento["version"]) is not int
                or documento["version"] != 1 or type(documento["nodes"]) is not list
                or type(documento["edges"]) is not list
                or len(documento["nodes"]) > 10000 or len(documento["edges"]) > 50000):
            raise ValueError("Contrato do grafo inválido.")

        def identificador(value):
            return (type(value) is str and 1 <= len(value) <= 200
                    and not any(ord(c) < 32 for c in value))

        nodes, ids = [], set()
        for item in documento["nodes"]:
            if type(item) is not dict or set(item) != {
                "id", "tipo", "titulo", "fonte_path", "conteudo_hash", "estado"
            }:
                raise ValueError("Nó inválido.")
            if (not identificador(item["id"]) or item["id"] in ids
                    or type(item["tipo"]) is not str or item["tipo"] not in TIPOS_NODE
                    or type(item["titulo"]) is not str or len(item["titulo"]) > 2000
                    or not item["titulo"].strip()
                    or type(item["estado"]) is not str
                    or item["estado"] not in {"creative", "canonical", "arquivado"}
                    or not all(v is None or (type(v) is str and len(v) <= 4096)
                               for v in (item["fonte_path"], item["conteudo_hash"]))):
                raise ValueError("Nó inválido ou duplicado.")
            ids.add(item["id"])
            nodes.append(tuple(item[k] for k in
                               ("id", "tipo", "titulo", "fonte_path",
                                "conteudo_hash", "estado")))
        edges, edge_ids, triples = [], set(), set()
        for item in documento["edges"]:
            if type(item) is not dict or set(item) != {
                "id", "origem_id", "destino_id", "relacao", "propriedades",
                "criado_em", "aprovado_por"
            }:
                raise ValueError("Relação inválida.")
            triple = (item["origem_id"], item["destino_id"], item["relacao"])
            if (not all(identificador(item[k]) for k in
                        ("id", "origem_id", "destino_id"))
                    or item["id"] in edge_ids or item["origem_id"] == item["destino_id"]
                    or item["origem_id"] not in ids or item["destino_id"] not in ids
                    or type(item["relacao"]) is not str
                    or item["relacao"] not in RELACOES or triple in triples
                    or item["propriedades"] is not None and
                       type(item["propriedades"]) is not dict
                    or type(item["criado_em"]) is not str
                    or not 1 <= len(item["criado_em"]) <= 80
                    or item["aprovado_por"] is not None and
                       (type(item["aprovado_por"]) is not str
                        or not identificador(item["aprovado_por"]))):
                raise ValueError("Relação inválida ou duplicada.")
            properties = (json.dumps(item["propriedades"], ensure_ascii=False)
                          if item["propriedades"] is not None else None)
            if properties is not None and len(properties) > 16000:
                raise ValueError("Propriedades demasiado grandes.")
            edge_ids.add(item["id"])
            triples.add(triple)
            edges.append((item["id"], *triple, properties, item["criado_em"],
                          item["aprovado_por"]))
        with self._connect() as con:
            con.execute("DELETE FROM edges")
            con.execute("DELETE FROM nodes")
            con.executemany(
                "INSERT INTO nodes(id,tipo,titulo,fonte_path,conteudo_hash,estado) "
                "VALUES(?,?,?,?,?,?)", nodes
            )
            con.executemany(
                "INSERT INTO edges(id,origem_id,destino_id,relacao,propriedades,"
                "criado_em,aprovado_por) VALUES(?,?,?,?,?,?,?)", edges
            )

    def reconstruir_snapshots(self, snapshots: list[dict]) -> None:
        """Materializa ligações comprovadas pelo mesmo hash de entrada.

        O chamador tem de fornecer snapshots previamente verificados pelo Store.
        Não infere ligações semânticas nem assinala aprovação por si próprio.
        """
        import hashlib
        if type(snapshots) is not list or len(snapshots) > 10000:
            raise ValueError("Seleção inválida.")
        nodes, edges, source_ids = [], [], set()
        seen = set()
        for item in snapshots:
            if type(item) is not dict:
                raise ValueError("Snapshot inválido.")
            run_id, source = item.get("run_id"), item.get("input_sha256")
            digest = item.get("content_sha256")
            if (type(run_id) is not str or len(run_id) != 32
                    or any(c not in "0123456789abcdef" for c in run_id)
                    or run_id in seen or type(source) is not str or len(source) != 64
                    or any(c not in "0123456789abcdef" for c in source)
                    or type(digest) is not str or len(digest) != 64
                    or any(c not in "0123456789abcdef" for c in digest)
                    or item.get("authority") not in {"canonical", "creative"}):
                raise ValueError("Snapshot inválido.")
            seen.add(run_id)
            nodes.append(dict(id=run_id, tipo="nota", titulo="Resultado verificado",
                              fonte_path=None, conteudo_hash=digest,
                              estado=item["authority"]))
            src_id = "fonte:" + source
            if src_id not in source_ids:
                source_ids.add(src_id)
                nodes.append(dict(id=src_id, tipo="fonte", titulo="Origem verificada",
                                  fonte_path=None, conteudo_hash=source, estado="creative"))
            edges.append(dict(id=hashlib.sha256((run_id + ":" + source).encode()).hexdigest(),
                              origem_id=run_id, destino_id=src_id, relacao="deriva_de",
                              propriedades={"evidencia": "input_sha256"},
                              criado_em="1970-01-01T00:00:00+00:00",
                              aprovado_por=None))
        self.reconstruir_json({"version": 1, "nodes": nodes, "edges": edges})

    def relacionados(self, node_id: str, permitidos: set[str], limite: int = 8) -> list[str]:
        """Outros resultados com a mesma origem, exclusivamente dentro do escopo."""
        if (type(node_id) is not str or type(permitidos) is not set
                or any(type(item) is not str for item in permitidos)
                or type(limite) is not int or not 1 <= limite <= 8):
            raise ValueError("Consulta de relações inválida.")
        if node_id not in permitidos:
            return []
        with self._connect() as con:
            rows = con.execute(
                "SELECT DISTINCT outro.origem_id FROM edges atual "
                "JOIN edges outro ON outro.destino_id = atual.destino_id "
                "WHERE atual.origem_id = ? AND atual.relacao = 'deriva_de' "
                "AND outro.relacao = 'deriva_de' AND outro.origem_id != ? "
                "ORDER BY outro.origem_id", (node_id, node_id)
            )
            return [other for (other,) in rows if other in permitidos][:limite]


if __name__ == "__main__":
    g = GraphMinimo()
    g.criar_node("nota-1", "nota", "Capítulo 3")
    g.criar_node("fonte-1", "fonte", "Entrevista A")
    g.criar_edge("nota-1", "fonte-1", "cita")
    print("Backlinks de fonte-1:", g.backlinks("fonte-1"))
    print("Vizinhança de nota-1:", g.vizinhanca("nota-1"))
