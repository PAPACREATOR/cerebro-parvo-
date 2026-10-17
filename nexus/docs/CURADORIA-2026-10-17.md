# Curadoria da documentação — 2026-10-17

## Objetivo

Organizar a documentação do Nexus em três camadas claras:

1. **Estado vivo** — o que o sistema é e consegue fazer agora.
2. **Contratos e arquitetura** — as regras que mantêm o sistema coerente.
3. **Histórico e evidência** — decisões, testes e relatórios que provam o caminho.

## Decisões

### 1. `PONTO-DE-SITUACAO.md` é a fonte de verdade

Este documento continua a ser o ponto de entrada para saber:

- o que está implementado;
- o que está testado;
- o que está pendente;
- que evidência suporta cada afirmação;
- que gates ainda não foram fechados.

### 2. Criar um índice único

O novo [`INDEX.md`](INDEX.md) passa a ser o mapa da documentação.

Ele separa:

- estado;
- arquitetura;
- capacidades;
- Windows e segurança;
- proveniência;
- evidência;
- contexto e estudos.

### 3. Não apagar histórico

Nenhum documento é eliminado nesta curadoria.

Os documentos datados permanecem porque registam decisões, testes, falhas corrigidas e a genealogia do Nexus.

### 4. Separar leitura pública de leitura técnica

O README principal deve responder rapidamente a:

- o que é o Nexus;
- que problema resolve;
- o que já funciona;
- como testar;
- o que ainda não está pronto.

A profundidade técnica pertence a `nexus/docs/`.

### 5. Prioridade de leitura

Para alguém novo:

1. README principal.
2. `INDEX.md`.
3. `PONTO-DE-SITUACAO.md`.
4. Fluxos de produto.
5. Contratos e arquitetura.

Para desenvolvimento:

1. `PONTO-DE-SITUACAO.md`.
2. `RECONCILIACAO-BANCADAS-E-ESTUDO-2026-10-17.md`.
3. Contratos relevantes.
4. Testes e evidência por SHA.

## Próximas melhorias

- Criar um `QUICKSTART.md` de cinco minutos.
- Extrair do ponto de situação um `ESTADO-ATUAL.md` curto.
- Separar relatórios concluídos em `docs/historico/` apenas quando deixarem de orientar o presente.
- Adicionar screenshots ou GIF da Folha ao README principal.
- Manter este índice atualizado em cada PR relevante.
