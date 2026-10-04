# Estrutura do Snapshot Completo do PC Nexus

Estado: estrutura apenas. Ainda não executa cópia nem recolha.

## Objetivo

Criar um snapshot reconstruível e auditável do ambiente Nexus do PC, preservando:

- conteúdo de `C:\Nexus`;
- estado Git;
- versões de ferramentas e ambientes;
- serviços/processos relevantes;
- permissões/ACLs;
- hashes SHA-256;
- inventário de software;
- referências a ficheiros grandes;
- resultados de testes;
- proveniência do snapshot.

O snapshot não altera a arquitetura Nexus nem substitui os cofres.

## Layout lógico

```
Nexus-PC-Snapshots/
  YYYYMMDD-HHMMSS/
    snapshot.json
    STATUS.json

    filesystem/
      Nexus/
        ... espelho de C:\Nexus ...

    inventory/
      machine.json
      windows.json
      python.json
      git.json
      software.json
      services.json
      ports.json
      environment.json

    security/
      acl-nexus.txt
      ownership.json
      excluded-secrets.json

    repositories/
      nexus-repository.json
      git-status.txt
      git-branches.txt
      git-remotes.txt
      git-diff-stat.txt

    hashes/
      files-sha256.jsonl
      root-summary.json

    tests/
      results.json
      logs/

    cloud/
      drive-reference.json

    notes/
      README.md
```

## Estados

`PREPARING -> COPYING -> HASHING -> VERIFYING -> COMPLETE`

Falhas:

`FAIL`, `BLOCKED`, `PARTIAL`

Nunca declarar `COMPLETE` sem:

1. cópia concluída;
2. manifesto escrito;
3. hashes calculados;
4. verificação de amostra;
5. inventário guardado;
6. estado Git registado;
7. exclusões explícitas;
8. referência cloud válida.

## Fonte de verdade

- GitHub: código, manifestos, scripts, coordenação e resultados.
- Google Drive privado: bytes do snapshot completo.
- PC: execução real.
- Snapshot: evidência imutável de um momento do PC.

## Exclusões obrigatórias do GitHub público

Nunca publicar:

- passwords;
- tokens;
- chaves;
- cookies;
- credenciais;
- dados pessoais;
- conteúdo privado dos cofres;
- ficheiros grandes que pertençam apenas ao snapshot cloud.

No snapshot cloud privado, credenciais também devem ser excluídas ou substituídas por metadados seguros.

## Contrato de reconciliação

Cada snapshot deve indicar:

- snapshot_id;
- UTC;
- hostname;
- raiz local;
- branch/commit do repositório;
- lista de ficheiros;
- SHA-256;
- versões;
- exclusões;
- testes;
- referência cloud;
- estado final.

A branch `pc-full-mirror-20261004` recebe apenas o conteúdo versionável do repositório local.
O snapshot cloud recebe o estado completo do PC Nexus.
