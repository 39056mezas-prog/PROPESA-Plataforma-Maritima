// PROPESA · Enviar PDF por correo con Resend (v1.49.0; v1.50.0: varios PDF y copia oculta al archivo).
// Vercel serverless function: recibe los PDF en base64, los destinatarios (Para, CC y la copia oculta al archivo de Gmail),
// el asunto y el mensaje, y manda un solo correo con todos los PDF adjuntos usando la API de Resend.
// Vercel no acepta más de 4.5 MB por llamada: la app junta máximo 3 MB de PDF (en base64 son unos 4 MB).
//
// Solo lo pueden usar personas con sesión en la app (Administrador o Encargado de piso): la app manda su sesión de
// Supabase en «Authorization: Bearer …» y aquí se revisa con Supabase antes de mandar nada. Así nadie de fuera puede
// usar este enlace para mandar correos. Las respuestas («Responder») le llegan a quien lo envió.
//
// Variables de entorno en Vercel (Settings → Environment Variables):
//   RESEND_API_KEY  — llave de Resend (empieza con "re_...")
//   EMAIL_FROM      — remitente, p.ej. "PROPESA <noreply@propesa.org>" (opcional; si no está, usa onboarding@resend.dev)
//   SUPABASE_URL, SUPABASE_KEY — opcionales; si no están, se usan los de la app (son públicos).
//
// Para pruebas sin dominio verificado en Resend, el remitente es onboarding@resend.dev
// y solo se puede mandar a la dirección del dueño de la cuenta de Resend.
// Una vez que se verifique el dominio (propesa.org), se pone EMAIL_FROM con ese dominio.

const RESEND_URL = 'https://api.resend.com/emails';
const SB_URL = process.env.SUPABASE_URL || 'https://lktqwmfmdhusscudgflo.supabase.co';
const SB_KEY = process.env.SUPABASE_KEY || 'sb_publishable_P4M21JmU4WcoKQbeI-P3Dw_6Rl5opEe';
const MAX_RCPT = 50;
const MAX_PDFS = 10;
const MAX_B64 = 4200000; // ~3 MB de PDF en base64; deja lugar al resto de la llamada (límite de Vercel: 4.5 MB)
// v1.55.2 (auditoría de seguridad): tope de correos por persona. Vive en la memoria de cada copia de la función (Vercel puede
// tener varias), así que es un freno contra el abuso o un error que mande sin parar, no una cuenta exacta.
const RATE_MAX = 40, RATE_MS = 10 * 60 * 1000, sentBy = new Map();
const rateOk = id => {
  const now = Date.now(), t = (sentBy.get(id) || []).filter(x => now - x < RATE_MS);
  if (t.length >= RATE_MAX) { sentBy.set(id, t); return false; }
  t.push(now); sentBy.set(id, t);
  if (sentBy.size > 500) for (const [k, v] of sentBy) if (!v.some(x => now - x < RATE_MS)) sentBy.delete(k);
  return true;
};
// v1.55.2: el adjunto siempre se llama «….pdf» (antes se podía mandar un PDF con nombre «x.html» o «x.exe»).
const pdfName = n => {
  const c = String(n).replace(/[^\w.\-áéíóúñÁÉÍÓÚÑ ]/g, '_').replace(/^[.\s]+/, '').slice(0, 116) || 'documento';
  return /\.pdf$/i.test(c) ? c : c + '.pdf';
};
const MAIL_RE = /^[^\s@<>,;:"'`\\()[\]]+@[^\s@<>,;:"'`\\()[\]]+\.[^\s@<>,;:"'`\\()[\]]{2,}$/;

const list = v => (Array.isArray(v) ? v : String(v || '').split(','))
  .map(e => String(e).trim().toLowerCase())
  .filter(e => e.length <= 120 && MAIL_RE.test(e));

// ¿Quién manda? Revisa la sesión con Supabase y su rol (admin o piso).
async function whoSends(req) {
  const h = req.headers.authorization || '';
  const m = /^Bearer\s+(.+)$/i.exec(h);
  if (!m) return null;
  const tk = m[1];
  const u = await fetch(SB_URL + '/auth/v1/user', { headers: { apikey: SB_KEY, Authorization: 'Bearer ' + tk } });
  if (!u.ok) return null;
  const user = await u.json().catch(() => null);
  if (!user || !user.id) return null;
  const p = await fetch(SB_URL + '/rest/v1/profiles?select=role,name&id=eq.' + encodeURIComponent(user.id),
    { headers: { apikey: SB_KEY, Authorization: 'Bearer ' + tk } });
  if (!p.ok) return null;
  const rows = await p.json().catch(() => []);
  const role = rows && rows[0] && rows[0].role;
  if (role !== 'admin' && role !== 'piso') return null;
  return { id: user.id, email: user.email || '', name: (rows[0] && rows[0].name) || '' };
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Solo se acepta POST.' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ ok: false, error: 'Falta la llave RESEND_API_KEY en las variables de entorno de Vercel.' });
  }

  let who = null;
  try { who = await whoSends(req); } catch (e) { console.error('send-email auth:', e); }
  if (!who) {
    return res.status(401).json({ ok: false, error: 'Tu sesión no es válida o tu usuario no puede mandar correos. Vuelve a entrar a la app.' });
  }

  const { to, cc, bcc, subject, body, pdf, filename, pdfs } = req.body || {};
  // v1.50.0: «pdfs» = [{filename, pdf}]; «pdf» + «filename» (un solo PDF) se sigue aceptando.
  const files = (Array.isArray(pdfs) ? pdfs : pdf ? [{ filename, pdf }] : [])
    .filter(f => f && typeof f.pdf == 'string' && typeof f.filename == 'string');

  if (!to || !subject || !files.length) {
    return res.status(400).json({ ok: false, error: 'Faltan datos del correo: a quién, asunto o el PDF.' });
  }
  if (files.length > MAX_PDFS) {
    return res.status(400).json({ ok: false, error: `Son demasiados PDF en un correo (máximo ${MAX_PDFS}).` });
  }
  // Solo PDF: el base64 de un PDF empieza con «JVBER» (%PDF).
  if (files.some(f => !/^JVBER/.test(f.pdf) || !/^[A-Za-z0-9+/=]+$/.test(f.pdf))) {
    return res.status(400).json({ ok: false, error: 'Solo se pueden adjuntar PDF.' });
  }
  if (files.reduce((a, f) => a + f.pdf.length, 0) > MAX_B64) {
    return res.status(413).json({ ok: false, error: 'Los PDF pesan demasiado para un correo (máximo 3 MB). Quita un PDF.' });
  }

  const recipients = [...new Set(list(to))];
  const copies = [...new Set(list(cc))].filter(e => !recipients.includes(e));
  const hidden = [...new Set(list(bcc))].filter(e => !recipients.includes(e) && !copies.includes(e));

  if (!recipients.length) {
    return res.status(400).json({ ok: false, error: 'No hay destinatarios válidos en «Para».' });
  }
  if (recipients.length + copies.length + hidden.length > MAX_RCPT) {
    return res.status(400).json({ ok: false, error: `Son demasiados destinatarios (máximo ${MAX_RCPT}).` });
  }

  if (!rateOk(who.id)) {
    console.warn('send-email: tope de correos', who.email);
    return res.status(429).json({ ok: false, error: `Mandaste muchos correos seguidos (máximo ${RATE_MAX} en 10 minutos). Espera unos minutos.` });
  }

  const from = process.env.EMAIL_FROM || 'PROPESA <onboarding@resend.dev>';
  const replyTo = MAIL_RE.test(String(who.email || '').toLowerCase()) ? who.email : undefined;

  const payload = {
    from,
    to: recipients,
    ...(copies.length ? { cc: copies } : {}),
    ...(hidden.length ? { bcc: hidden } : {}),
    ...(replyTo ? { reply_to: replyTo } : {}),
    subject: String(subject).replace(/[\r\n]+/g, ' ').slice(0, 200),
    text: String(body || 'Se adjuntan los PDF.').slice(0, 8000),
    attachments: files.map(f => ({
      filename: pdfName(f.filename),
      content: f.pdf,  // base64
    })),
  };

  try {
    const r = await fetch(RESEND_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await r.json().catch(() => ({}));

    if (r.ok) {
      console.log('send-email: enviado', { por: who.email, destinatarios: recipients.length + copies.length + hidden.length, pdf: files.length });
      return res.status(200).json({ ok: true, id: data.id });
    }

    console.error('Resend error:', r.status, data);
    return res.status(r.status >= 400 && r.status < 500 ? 400 : 502).json({
      ok: false,
      error: data.message || 'El servicio de correo no aceptó el envío.',
    });
  } catch (e) {
    console.error('send-email error:', e);
    return res.status(502).json({
      ok: false,
      error: 'No se pudo conectar con el servicio de correo.',
    });
  }
};
