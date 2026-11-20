// v1.50.0 · Prueba del servidor de correo (api/send-email.js) sin internet: se finge Supabase y Resend.
// v1.55.2: el adjunto siempre termina en .pdf y hay tope de correos por persona (auditoría de seguridad).
// Correr: node pruebas/correo_servidor_t.js  → debe terminar en «TODO BIEN».
const assert = require('assert');
const path = require('path');
process.env.RESEND_API_KEY = 're_prueba';
const send = require(path.join(__dirname, '..', 'api', 'send-email.js'));

let sent = null;
global.fetch = async (url, opt) => {
  const ok = (j) => ({ ok: true, status: 200, json: async () => j });
  if (url.includes('/auth/v1/user')) return /Bearer bueno/.test(opt.headers.Authorization) ? ok({ id: 'u1', email: 'yo@propesa.org' }) : { ok: false, status: 401, json: async () => ({}) };
  if (url.includes('/rest/v1/profiles')) return ok([{ role: 'piso', name: 'Martha' }]);
  if (url.includes('api.resend.com')) { sent = JSON.parse(opt.body); return ok({ id: 'r1' }); }
  throw new Error('url inesperada ' + url);
};
const call = async (body, tk = 'bueno') => {
  let st = 0, js = null;
  const res = { setHeader() {}, status(s) { st = s; return this; }, json(j) { js = j; return this; } };
  sent = null;
  await send({ method: 'POST', headers: { authorization: 'Bearer ' + tk }, body }, res);
  return { st, js };
};
const PDF = Buffer.from('%PDF-1.4 prueba').toString('base64');

(async () => {
  // sin sesión: no manda nada
  let r = await call({ to: 'a@b.com', subject: 's', pdfs: [{ filename: 'a.pdf', pdf: PDF }] }, 'malo');
  assert.strictEqual(r.st, 401); assert.strictEqual(sent, null);

  // varios PDF + copia oculta al archivo
  r = await call({ to: 'a@b.com', cc: 'c@d.com', bcc: ['archivo@gmail.com', 'a@b.com'], subject: 'Hola', body: 'x',
    pdfs: [{ filename: 'uno.pdf', pdf: PDF }, { filename: 'dos.pdf', pdf: PDF }] });
  assert.strictEqual(r.st, 200, JSON.stringify(r.js));
  assert.deepStrictEqual(sent.bcc, ['archivo@gmail.com']); // el que ya va en «Para» no se repite
  assert.strictEqual(sent.attachments.length, 2);
  assert.strictEqual(sent.reply_to, 'yo@propesa.org');

  // un solo PDF a la manera de la v1.49.0
  r = await call({ to: 'a@b.com', subject: 'Hola', pdf: PDF, filename: 'a.pdf' });
  assert.strictEqual(r.st, 200); assert.strictEqual(sent.attachments.length, 1); assert.ok(!sent.bcc);

  // solo PDF
  r = await call({ to: 'a@b.com', subject: 'Hola', pdfs: [{ filename: 'a.exe', pdf: Buffer.from('MZ').toString('base64') }] });
  assert.strictEqual(r.st, 400); assert.strictEqual(sent, null);

  // muy pesado
  const big = 'JVBER' + 'A'.repeat(4300000);
  r = await call({ to: 'a@b.com', subject: 'Hola', pdfs: [{ filename: 'a.pdf', pdf: big }] });
  assert.strictEqual(r.st, 413); assert.strictEqual(sent, null);

  // sin PDF
  r = await call({ to: 'a@b.com', subject: 'Hola', pdfs: [] });
  assert.strictEqual(r.st, 400);
  // v1.55.2: el nombre del adjunto siempre termina en .pdf
  r = await call({ to: 'a@b.com', subject: 'Hola', pdfs: [{ filename: 'factura.html', pdf: PDF }, { filename: 'Packing list.PDF', pdf: PDF }] });
  assert.strictEqual(r.st, 200);
  assert.deepStrictEqual(sent.attachments.map(a => a.filename), ['factura.html.pdf', 'Packing list.PDF']);

  // v1.55.2: tope de 40 correos en 10 minutos por persona (ya van 3 de este usuario)
  for (let i = 0; i < 37; i++) { r = await call({ to: 'a@b.com', subject: 'n' + i, pdf: PDF, filename: 'a.pdf' }); assert.strictEqual(r.st, 200); }
  r = await call({ to: 'a@b.com', subject: 'uno más', pdf: PDF, filename: 'a.pdf' });
  assert.strictEqual(r.st, 429); assert.strictEqual(sent, null);
  console.log('TODO BIEN');
})().catch(e => { console.error(e); process.exit(1); });
