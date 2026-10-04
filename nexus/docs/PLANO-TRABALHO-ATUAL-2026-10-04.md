# PLANO DE TRABALHO ATUAL — 2026-10-04

Estado de partida:
- baseline histórica: PR #17 / SHA `30ff272794c222203da8157df50d09154ee1bc2a`;
- runtime Python limpo: PR #21 / SHA `7f02d6fca998bf78810a653dcd312ad09d19c34b`;
- ramo ativo desta fase: `integration-open-notebook-mcp-tiny-20261004`.
- Conductor, Spiff e YAML de execução permanecem fora do runtime ativo.

## Método obrigatório

Para cada alteração, sem exceção:

1. rever código e contratos afetados;
2. fazer uma alteração pequena;
3. teste unitário do bloco;
4. teste bidirecional ida/volta quando aplicável;
5. casos bons, maus, ambíguos, adversariais e limites;
6. timeout, ferramenta ausente, resposta malformed e adulteração;
7. regressão do bloco anterior;
8. restart/idempotência/proveniência quando o bloco toca no Kernel/Store;
9. teste real da ferramenta, não apenas health check;
10. E2E quando todos os blocos da fase estiverem verdes;
11. FAIL real é preservado e explicado;
12. corrigir apenas a causa mínima;
13. repetir até PASS ou até a limitação real ficar entendida/documentada;
14. só depois passar ao bloco seguinte.

Nenhum bloco é considerado fechado apenas com teste de ida.

---

## FASE A — MCP Python genérico

### A1 — Cliente MCP local
Estado: EM IMPLEMENTAÇÃO.

Objetivo:
- stdio local;
- descoberta dinâmica de tools;
- chamada estruturada;
- allowlist explícita do Kernel;
- ambiente reduzido;
- sem credenciais cloud herdadas;
- limite de tamanho da resposta;
- nenhuma autoridade MCP sobre Creative/Canonical.

Testes obrigatórios:
- listar tools reais;
- chamar tool real;
- ida e volta Unicode;
- tool proibida;
- tool inexistente;
- tool que devolve erro;
- servidor ausente;
- timeout;
- resposta malformed;
- resposta excessiva;
- restart da chamada sem duplicar efeitos quando aplicável.

Gate:
- PASS do bloco + regressão completa.

### A2 — OpenNotebook MCP real
Estado: PENDENTE após A1.

Objetivo:
- ligar ao servidor `open-notebook-mcp` real;
- descobrir as tools em runtime;
- não fixar o Nexus ao número 33/39;
- testar primeiro `search_capabilities`, que não depende do backend;
- depois testar tools que exigem OpenNotebook ativo.

Nota factual atual:
- README diz 39;
- `server.py` analisado expõe 33 tools reais;
- podcast existe no OpenNotebook mas ainda não está exposto nesse MCP;
- Work fica responsável por expor podcast e criar extensão visual/FFmpeg dentro do OpenNotebook.

Testes:
- descoberta MCP real;
- comparação lista declarada vs lista executável;
- chamada real `search_capabilities`;
- backend ausente deve falhar de forma controlada;
- quando backend estiver disponível: leitura/escrita por famílias;
- ida/volta e proveniência da chamada.

---

## FASE B — Tiny local Qwen 3B

### B1 — Boundary do tiny
Estado: EM IMPLEMENTAÇÃO.

Objetivo:
- tiny só classifica uma das 7 intenções:
  `arquivo, web, fontes, trabalhar, perguntar, calcular, tema`;
- ou devolve UNKNOWN;
- sem tools;
- sem Store;
- sem Canonical;
- sem autorização;
- sem paths/comandos;
- contexto curto.

Testes:
- 7 intenções;
- ambiguidade;
- Unicode;
- erros de pontuação;
- prompt injection;
- resposta JSON inválida;
- intenção proibida;
- timeout;
- processo ausente;
- tentativa de devolver autoridade.

### B2 — Qwen 3B real
Estado: PENDENTE.

Objetivo:
- apontar o boundary ao Qwen 3B local do utilizador;
- medir precisão e falsos positivos;
- UNKNOWN sempre que houver dúvida real;
- se continuar ambíguo: ASK_HUMAN.

Gate:
- corpus controlado;
- corpus ruidoso;
- regressão dos 100.000 casos existentes;
- teste bidirecional Natural -> tiny -> intenção -> Markdown -> retorno.

---

## FASE C — Folha / ELIZA / Kernel

### C1 — ligar resolução natural ao runtime
Estado: PENDENTE.

Fluxo:
`Humano -> Folha -> ELIZA -> LanguageTool shadow -> tiny Qwen 3B -> ASK_HUMAN se necessário -> Markdown interno -> Kernel`.

Regras:
- humano nunca escreve Markdown;
- Markdown é interno;
- ELIZA não tem autoridade;
- tiny não tem autoridade;
- só uma intenção única pode avançar;
- dúvida real volta ao humano.

Testes:
- prefixos;
- linguagem natural;
- pontuação/acentos/espaços;
- instruções duplas;
- negações;
- texto citado que contém comandos;
- ida/volta byte-a-byte;
- adulteração do Markdown bloqueada.

### C2 — mapear intenção para capability
Estado: PENDENTE.

Objetivo:
- deixar de obrigar o humano a escolher radio buttons técnicos;
- Kernel decide qual capability autorizada corresponde à intenção;
- MCP apenas executa a capability já autorizada.

---

## FASE D — OpenNotebook funcional

Estado: PENDENTE após A/B/C.

Responsabilidade Nexus:
- ligar e testar MCP;
- controlar allowlist;
- validar outputs;
- Creative;
- proveniência;
- Human Gate.

Responsabilidade Work/OpenNotebook:
- trabalhar no interior do OpenNotebook;
- reutilizar o gerador de podcast já existente;
- expor podcast pelo MCP;
- acrescentar visual podcast com FFmpeg.

Não reconstruir no Nexus:
- outline de podcast;
- transcript;
- speakers;
- TTS;
- mistura de áudio;
- MP3.

---

## FASE E — triangulação de conhecimento

Estado: PENDENTE.

Comparar a mesma pergunta em:
1. OpenNotebook;
2. Web Search;
3. Zotero.

Medir:
- fontes;
- cobertura;
- atualidade;
- contradições;
- omissões;
- citações;
- proveniência;
- resultado -> fonte;
- fonte -> resultados que a utilizaram.

Nenhuma das três fontes ganha autoridade automática.

---

## FASE F — Wiki/FTS5 oficial

Estado atual:
- laboratório forte;
- 100.000/100.000 PASS;
- ainda não ligado ao Host oficial.

Objetivo:
- ligar como vista derivada/reconstruível;
- nunca como segundo cérebro;
- manter relações bidirecionais;
- reconstrução integral a partir do Store.

---

## FASE G — LibreOffice Writer

Estado: PENDENTE.

Objetivo:
- template Writer real `.ott`;
- design suíço;
- Helvetica/Helvetica Neue quando disponível, fallback livre compatível;
- grelha;
- margens;
- estilos de título/corpo/legenda/tabela;
- viúvas/órfãs;
- imagens;
- paginação;
- PDF final pelo adapter LibreOffice já existente.

Sequência:
1. contrato visual;
2. criar `.ott`;
3. abrir no LibreOffice real;
4. gerar documento;
5. exportar PDF;
6. comparar ida/volta e hashes;
7. stress com livros/documentos longos.

---

## FASE H — Podcast visual

Responsabilidade principal: Work/OpenNotebook.

Entrada:
- podcast MP3 já produzido pelo OpenNotebook.

Extensão:
`MP3 + transcript/outline + imagens/frames -> FFmpeg local -> MP4`.

Nexus apenas:
- chama capability;
- valida resultado;
- guarda proveniência;
- Creative;
- Human Gate.

---

## FASE I — hardening final

Pendente:
- sandbox/ACL Windows;
- backup/restauro integral;
- crash/restart com MCP;
- idempotência de writes MCP;
- concorrência;
- ferramenta que desaparece durante execução;
- PC físico do utilizador;
- E2E completo desde linguagem natural até resultado final e retorno à fonte.

---

## Ordem de execução imediata

1. A1 MCP Python genérico.
2. B1 tiny boundary.
3. A2 OpenNotebook MCP real.
4. B2 Qwen 3B real.
5. C1 Folha/ELIZA/tiny/Markdown/Kernel.
6. C2 intenção -> capability.
7. D OpenNotebook funcional.
8. E OpenNotebook/Web/Zotero.
9. F Wiki oficial.
10. G Writer suíço.
11. H Podcast visual via Work/OpenNotebook.
12. I Hardening + E2E final.

Regra permanente: **não avançar para o ponto seguinte enquanto o anterior não tiver PASS suficiente ou uma limitação real compreendida, registada e isolada.**
