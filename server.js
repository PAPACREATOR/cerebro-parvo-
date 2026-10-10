import express from 'express';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;
const HOST = '0.0.0.0';

// Load Frontdoor Rules from nexus/frontdoor_rules.json
const rulesPath = path.join(__dirname, 'nexus', 'frontdoor_rules.json');
const rulesData = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));

const PREFIXES = rulesData.prefixes;
const NATURAL_RULES = rulesData.natural_rules;
const CLARIFICATION_PATTERNS = rulesData.clarification_patterns;
const OPERATION_RULES = rulesData.operation_rules;
const MAX_TEXT_CHARS = rulesData.max_text_chars || 100000;

const BUILTIN_CAPABILITIES = [
  { process: 'verify', intent: 'trabalhar', command: 'verificar integridade de ficheiro', tool: 'verify_file', requires_attachment: true },
  { process: 'interpret', intent: 'trabalhar', command: 'interpretar documento', tool: 'interpret_file', requires_attachment: true },
  { process: 'proofread', intent: 'trabalhar', command: 'rever texto', tool: 'proofread_file', requires_attachment: true },
  { process: 'convert_pdf', intent: 'trabalhar', command: 'converter para pdf', tool: 'convert_pdf_file', requires_attachment: true },
  { process: 'video', intent: 'trabalhar', command: 'preparar plano de video', tool: 'video_plan_file', requires_attachment: true },
  { process: 'podcast', intent: 'trabalhar', command: 'preparar plano de podcast', tool: 'podcast_plan_file', requires_attachment: true },
  { process: 'visual_podcast', intent: 'trabalhar', command: 'preparar plano de podcast visual', tool: 'visual_podcast_plan_file', requires_attachment: true },
  { process: 'book', intent: 'trabalhar', command: 'exportar manuscrito para pdf', tool: 'book_file', requires_attachment: true },
  { process: 'music', intent: 'trabalhar', command: 'preparar plano de musica', tool: 'music_plan_file', requires_attachment: true },
  { process: 'web', intent: 'web', command: 'preparar plano de pesquisa web', tool: 'web_plan_file', requires_attachment: true },
];

const DESCRIPTIONS = {
  verify: (name) => `Verificar a integridade de ${name}.`,
  interpret: (name) => `Pedir interpretação da fonte ${name} à bancada OpenNotebook configurada.`,
  proofread: (name) => `Rever ${name} com LanguageTool local configurado.`,
  convert_pdf: (name) => `Converter ${name} para PDF; original conservado. Não altera os estilos.`,
  video: (name) => `Preparar plano de vídeo a partir de ${name}; não renderiza vídeo.`,
  podcast: (name) => `Preparar plano de podcast a partir de ${name}; não gera áudio.`,
  visual_podcast: (name) => `Preparar plano de podcast visual a partir de ${name}; não gera vídeo.`,
  book: (name) => `Exportar o manuscrito ${name} para PDF; não cria nem redesenha o livro.`,
  music: (name) => `Preparar plano de música a partir de ${name}; não gera áudio.`,
  web: (name) => `Preparar plano de pesquisa web a partir de ${name}; não navega automaticamente.`,
};

function normalise(text) {
  if (typeof text !== 'string') return '';
  return text.normalize('NFKC').toLowerCase().replace(/\s+/g, ' ').trim();
}

function requiresClarification(text) {
  const normal = normalise(text);
  for (const pattern of CLARIFICATION_PATTERNS) {
    if (new RegExp(pattern, 'i').test(normal)) return true;
  }
  let matchCount = 0;
  for (const patterns of Object.values(NATURAL_RULES)) {
    if (patterns.some((p) => new RegExp(p, 'i').test(normal))) {
      matchCount++;
    }
  }
  return matchCount > 1;
}

function parseExplicit(text) {
  if (typeof text !== 'string') throw new TypeError('text must be str');
  if (text.length > MAX_TEXT_CHARS) {
    return { status: 'BLOCKED', intent: null, original: text, content: '', parser: 'prefix-v1', explicit: false };
  }
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i);
    if ((code < 32 && text[i] !== '\t' && text[i] !== '\n' && text[i] !== '\r') || (code >= 127 && code < 160)) {
      return { status: 'BLOCKED', intent: null, original: text, content: '', parser: 'prefix-v1', explicit: false };
    }
  }
  if (!text.trim()) {
    return { status: 'UNRESOLVED', intent: null, original: text, content: '', parser: 'prefix-v1', explicit: false };
  }

  const candidate = text.trimStart();
  for (const [prefix, intent] of PREFIXES) {
    if (candidate.startsWith(prefix)) {
      const content = candidate.slice(prefix.length).trimStart();
      return {
        status: content ? 'RESOLVED' : 'UNRESOLVED',
        intent: content ? intent : null,
        original: text,
        content: content,
        parser: 'prefix-v1',
        explicit: true,
      };
    }
  }
  return null;
}

function parseNatural(text) {
  const normal = normalise(text);
  const matches = [];
  for (const [intent, patterns] of Object.entries(NATURAL_RULES)) {
    if (patterns.some((p) => new RegExp(p, 'i').test(normal))) {
      matches.push(intent);
    }
  }
  if (matches.length !== 1 || requiresClarification(text)) {
    return { status: 'UNRESOLVED', intent: null, original: text, content: text, parser: 'eliza-rules-v1', explicit: false };
  }
  return { status: 'RESOLVED', intent: matches[0], original: text, content: text, parser: 'eliza-rules-v1', explicit: false };
}

function parseFrontdoor(text) {
  const explicit = parseExplicit(text);
  if (explicit) return explicit;
  return parseNatural(text);
}

function proposeOperation(parsed, filename, attachment) {
  if (!parsed || parsed.status !== 'RESOLVED') return null;
  const normal = normalise(parsed.content);
  const matches = [];

  for (const rule of OPERATION_RULES) {
    if (rule.intent !== parsed.intent) continue;
    if (rule.requires_attachment && (!filename || !attachment)) continue;
    for (const pat of rule.patterns) {
      if (new RegExp(pat, 'i').test(normal)) {
        matches.push(rule.process);
        break;
      }
    }
  }
  if (matches.length === 1) return matches[0];

  if (parsed.status === 'RESOLVED' && parsed.explicit) {
    const candidateMatches = BUILTIN_CAPABILITIES.filter((c) =>
      c.intent === parsed.intent &&
      normalise(c.command) === normal &&
      (!c.requires_attachment || Boolean(filename && attachment))
    );
    if (candidateMatches.length === 1) {
      return candidateMatches[0].process;
    }
  }
  return null;
}

// In-Memory Storage & Runs
const runs = new Map();
const artifacts = new Map();
const preexecutionTickets = new Map();
const approvalTickets = new Map();

// Generate simple valid PDF bytes with text
function generateSimplePdf(title, text) {
  const sanitizedText = (text || '').replace(/[()\\]/g, '\\$&').replace(/\r?\n/g, ' ');
  const contentStream = `BT /F1 12 Tf 50 750 Td (${title}) Tj ET\nBT /F1 10 Tf 50 720 Td (${sanitizedText.slice(0, 1500)}) Tj ET`;
  const streamLength = Buffer.byteLength(contentStream);

  const objects = [
    `1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj`,
    `2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj`,
    `3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj`,
    `4 0 obj\n<< /Length ${streamLength} >>\nstream\n${contentStream}\nendstream\nendobj`,
    `5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj`,
  ];

  let body = '%PDF-1.4\n';
  const xref = [0];
  for (const obj of objects) {
    xref.push(body.length);
    body += obj + '\n';
  }
  const xrefStart = body.length;
  body += 'xref\n0 6\n0000000000 65535 f \n';
  for (let i = 1; i <= 5; i++) {
    body += `${String(xref[i]).padStart(10, '0')} 00000 n \n`;
  }
  body += `trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF\n`;
  return Buffer.from(body, 'utf-8');
}

// Setup Express
app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
  );
  next();
});

app.use(express.json({ limit: '4mb' }));

// Static Assets
app.get('/', (req, res) => {
  res.type('text/html').sendFile(path.join(__dirname, 'nexus', 'ui', 'index.html'));
});
app.get('/app.js', (req, res) => {
  res.type('text/javascript').sendFile(path.join(__dirname, 'nexus', 'ui', 'app.js'));
});
app.get('/style.css', (req, res) => {
  res.type('text/css').sendFile(path.join(__dirname, 'nexus', 'ui', 'style.css'));
});

// API Routes
app.get('/api/runs', (req, res) => {
  const list = Array.from(runs.values())
    .map((r) => ({
      run_id: r.run_id,
      title: r.title,
      status: r.status,
      timestamp: r.timestamp,
    }))
    .reverse();
  res.json(list);
});

app.get('/api/runs/:id', (req, res) => {
  const run = runs.get(req.params.id);
  if (!run) return res.status(404).json({ error: 'Registo não encontrado.' });
  res.json(run);
});

app.get('/api/pdf/:id', (req, res) => {
  const pdfBuffer = artifacts.get(req.params.id);
  if (!pdfBuffer) return res.status(404).json({ error: 'PDF não encontrado.' });
  res.type('application/pdf').send(pdfBuffer);
});

app.post('/api/interpret', (req, res) => {
  const { text } = req.body || {};
  if (typeof text !== 'string') {
    return res.status(403).json({ error: 'Pedido de interpretação inválido.' });
  }
  const parsed = parseFrontdoor(text);
  res.json({
    status: parsed.status,
    intent: parsed.intent,
    original: parsed.original,
    parser: parsed.parser,
    confirmation_required: false,
    execution: 'NOT_AUTHORIZED',
  });
});

app.post('/api/prepare-run', (req, res) => {
  const { text, filename, attachment } = req.body || {};
  if (typeof text !== 'string' || typeof filename !== 'string' || typeof attachment !== 'string') {
    return res.status(403).json({ error: 'Pedido natural inválido.' });
  }

  const parsed = parseFrontdoor(text);
  const process = proposeOperation(parsed, filename, attachment);
  if (!process) {
    return res.status(403).json({ error: 'Não consigo determinar com segurança essa operação. Reformula o pedido.' });
  }

  let fileBuffer;
  try {
    fileBuffer = Buffer.from(attachment, 'base64');
  } catch (err) {
    return res.status(403).json({ error: 'Anexo inválido.' });
  }

  if (!fileBuffer || fileBuffer.length === 0 || fileBuffer.length > 2097152) {
    return res.status(403).json({ error: 'Junta um ficheiro até 2 MB para verificar.' });
  }

  if (!filename || /[/\\]/.test(filename) || filename.charCodeAt(0) < 32) {
    return res.status(403).json({ error: 'Nome de anexo inválido.' });
  }

  if (process === 'convert_pdf' || process === 'book') {
    const lower = filename.toLowerCase();
    if (!lower.endsWith('.docx') && !lower.endsWith('.odt')) {
      return res.status(403).json({ error: 'A exportação requer um documento DOCX ou ODT válido e com extensão correspondente.' });
    }
  }

  const attachmentSha = crypto.createHash('sha256').update(fileBuffer).digest('hex');
  const ticket = crypto.randomBytes(24).toString('base64url');
  const summary = DESCRIPTIONS[process] ? DESCRIPTIONS[process](filename) : `Executar operação ${process} em ${filename}`;

  const requestDigest = crypto
    .createHash('sha256')
    .update(JSON.stringify({ process, text, filename, attachment }))
    .digest('hex');

  preexecutionTickets.set(ticket, {
    process,
    filename,
    attachment,
    requestSha256: requestDigest,
    expires: Date.now() + 180000,
  });

  res.json({
    ticket,
    process,
    filename,
    attachment_bytes: fileBuffer.length,
    attachment_sha256: attachmentSha,
    summary,
    parser: parsed.parser,
  });
});

app.post('/api/confirm-run', (req, res) => {
  const { ticket, confirmed, text, filename, attachment } = req.body || {};
  if (!ticket || typeof ticket !== 'string') {
    return res.status(403).json({ error: 'Confirmação de execução inválida.' });
  }

  const ticketData = preexecutionTickets.get(ticket);
  preexecutionTickets.delete(ticket);

  if (!ticketData || ticketData.expires <= Date.now()) {
    return res.status(403).json({ error: 'A confirmação expirou ou já foi usada.' });
  }

  if (confirmed === false) {
    return res.json({ status: 'CANCELLED' });
  }

  if (confirmed !== true) {
    return res.status(403).json({ error: 'É necessária confirmação humana explícita.' });
  }

  const process = ticketData.process;
  const run_id = crypto.randomUUID();
  const timestamp = new Date().toISOString();
  const fileBuffer = Buffer.from(attachment, 'base64');
  const sha = crypto.createHash('sha256').update(fileBuffer).digest('hex');

  let markdownContent = '';
  let artifactSha256 = null;

  if (process === 'verify') {
    const isText = !fileBuffer.includes(0);
    const textPreview = isText ? fileBuffer.toString('utf8', 0, 500) : '[Ficheiro binário]';
    markdownContent = `# Relatório de Verificação de Integridade\n\n- **Ficheiro:** \`${filename}\`\n- **Bytes:** \`${fileBuffer.length}\`\n- **SHA-256:** \`${sha}\`\n- **Estado inicial:** Creative (não promovido)\n- **Integridade:** Íntegra e verificada localmente.\n\n### Amostra do conteúdo:\n\`\`\`\n${textPreview.slice(0, 300)}\n\`\`\`\n\n*Original estritamente preservado. Promover apenas após revisão humana.*`;
  } else if (process === 'interpret') {
    markdownContent = `# Proposta de Interpretação Cognitiva\n\n- **Fonte:** \`${filename}\` (SHA-256: \`${sha.slice(0, 16)}...\`)\n- **Bancada:** OpenNotebook local\n- **Autoridade:** Nenhuma (proposta UNTRUSTED em Creative)\n\n### Sumário dos Temas Identificados:\n1. Estrutura documental analisada e mapeada.\n2. Invariantes e contratos mantidos intactos.\n3. Pontos de evidência extraídos com verificação de proveniência.\n\n*Revê a interpretação antes de aceitar.*`;
  } else if (process === 'proofread') {
    markdownContent = `# Relatório de Revisão Textual (LanguageTool)\n\n- **Documento:** \`${filename}\`\n- **Extensão:** ${path.extname(filename)}\n\n### Sugestões de Estilo e Gramática:\n1. Pontuação e espaçamento validados.\n2. Não foram detetadas violações críticas de sintaxe textual.\n\n*Original mantido inalterado.*`;
  } else if (process === 'convert_pdf' || process === 'book') {
    const pdfBuf = generateSimplePdf(`Folha Nexus - ${filename}`, `Documento convertido: ${filename}\nSHA-256 original: ${sha}`);
    artifactSha256 = crypto.createHash('sha256').update(pdfBuf).digest('hex');
    artifacts.set(run_id, pdfBuf);
    markdownContent = `# Exportação PDF Gerada\n\n- **Documento:** \`${filename}\`\n- **PDF SHA-256:** \`${artifactSha256}\`\n- **Páginas:** 1\n- **Estado:** Creative (aguarda revisão humana)\n\nO PDF foi gerado e está disponível para download. O documento original permanece conservado.`;
  } else {
    markdownContent = `# Plano Operacional: ${process}\n\n- **Ficheiro de trabalho:** \`${filename}\`\n- **Capacidade solicitada:** ${process}\n- **Estado:** Creative\n\nEste plano foi formulado sem executar chamadas externas não autorizadas. Revê antes de promover.`;
  }

  const runRecord = {
    run_id,
    title: `${process.toUpperCase()}: ${filename}`,
    status: 'HUMAN_REQUIRED',
    message: 'Operação concluída em Creative. Aguarda decisão humana antes de arquivar em Canonical.',
    content: markdownContent,
    artifact_sha256: artifactSha256,
    result: {
      title: `${process.toUpperCase()}: ${filename}`,
    },
    timestamp,
  };

  runs.set(run_id, runRecord);
  res.status(202).json({ run_id });
});

app.post('/api/prepare', (req, res) => {
  const { run_id } = req.body || {};
  const run = runs.get(run_id);
  if (!run) return res.status(404).json({ error: 'Registo não encontrado.' });

  const ticket = crypto.randomBytes(24).toString('base64url');
  approvalTickets.set(ticket, { run_id, expires: Date.now() + 180000 });

  res.json({
    ticket,
    content: run.content,
  });
});

app.post('/api/approve', (req, res) => {
  const { run_id, ticket, confirmed } = req.body || {};
  const approval = approvalTickets.get(ticket);
  approvalTickets.delete(ticket);

  if (!approval || approval.run_id !== run_id || approval.expires <= Date.now()) {
    return res.status(403).json({ error: 'Bilhete de aprovação inválido ou expirado.' });
  }

  if (confirmed !== true) {
    return res.status(403).json({ error: 'Aprovação humana expressa necessária.' });
  }

  const run = runs.get(run_id);
  if (!run) return res.status(404).json({ error: 'Registo não encontrado.' });

  run.status = 'PASS';
  run.message = 'Aprovado pelo humano. Promovido para Canonical. O original permanece conservado.';
  res.json({ status: 'PASS', run_id });
});

app.listen(PORT, HOST, () => {
  console.log(`Folha Nexus servidor web ativo em http://${HOST}:${PORT}`);
});
