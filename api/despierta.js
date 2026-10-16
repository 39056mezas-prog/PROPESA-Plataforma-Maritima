// PROPESA · Mantener despierta la base de Supabase (v1.8.0).
// El plan gratis de Supabase pausa la base después de 7 días sin uso, y en la veda (16 feb – 15 sep) casi nadie abre la app.
// Vercel llama a esta dirección una vez al día (vercel.json → "crons") y aquí se hace una consulta pequeña a la base:
// «¿ya hay Administrador?» (la misma que hace la pantalla de acceso). No lee datos de la operación ni cambia nada.
// Si algún día cambian de base, poner aquí la dirección y la llave pública nuevas (las mismas de index.html, SBC),
// o definirlas en Vercel como SUPABASE_URL y SUPABASE_KEY. Si existe CRON_SECRET en Vercel, solo Vercel puede llamarla.
const SB_URL = process.env.SUPABASE_URL || 'https://lktqwmfmdhusscudgflo.supabase.co';
const SB_KEY = process.env.SUPABASE_KEY || 'sb_publishable_P4M21JmU4WcoKQbeI-P3Dw_6Rl5opEe';

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const secret = process.env.CRON_SECRET;
  if (secret && req.headers.authorization !== `Bearer ${secret}`) return res.status(401).json({ ok: false });
  try {
    const r = await fetch(SB_URL + '/rest/v1/rpc/has_admin', {
      method: 'POST',
      headers: { apikey: SB_KEY, 'Content-Type': 'application/json' },
      body: '{}',
    });
    // 200 = la base respondió (y cuenta como uso). Otro número = la base está pausada o falló: se ve en Vercel → Logs.
    return res.status(r.ok ? 200 : 502).json({ ok: r.ok, base: r.status, hora: new Date().toISOString() });
  } catch (e) {
    return res.status(502).json({ ok: false, error: String((e && e.message) || e), hora: new Date().toISOString() });
  }
};
