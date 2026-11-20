// PROPESA · función "usuarios": alta, cambios y baja de usuarios (solo el Administrador).
// También crea el primer Administrador cuando la base todavía no tiene ninguna cuenta ("setup").
// Usa la llave de servicio, que solo existe aquí (nunca en la app).
import { createClient } from "npm:@supabase/supabase-js@2.119.0"; // v1.46.0: versión fija (auditoría técnica R14)

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const ROLES = ["admin", "piso", "consulta", "cliente"]; // cliente (v1.13.0): compradores de fuera, solo ven la disponibilidad
const WEAK = ["admin123", "piso123", "ver123", "123456", "1234567", "12345678", "123456789", "password", "contraseña", "propesa", "propesa1", "langosta", "qwerty", "abc123", "111111", "000000"];

const out = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });
const txt = (v: unknown, max: number) => String(v ?? "").trim().slice(0, max);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return out(405, { error: "Método no permitido" });
  try {
    const adm = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
    const b = await req.json().catch(() => ({}));
    const action = String(b.action || "");
    const name = txt(b.name, 80), email = txt(b.email, 120).toLowerCase(), pw = String(b.password ?? "");
    const role = ROLES.includes(b.role) ? b.role : "", notify = !!b.notify;   // v1.46.0: un rol desconocido ya no se vuelve «consulta» (R14/T9)

    const checkPw = () => pw.length < 8 ? "La contraseña debe tener al menos 8 caracteres."
      : WEAK.includes(pw.toLowerCase()) ? "Esa contraseña es muy fácil de adivinar. Elige otra." : null;
    // v1.7.0 (auditoría #15): "setup" solo cuando no hay NINGÚN perfil. Antes bastaba con que no hubiera Administrador:
    // si alguien borraba a los Administradores desde el panel, cualquiera que abriera la página se volvía Administrador.
    const profiles = async () => {
      const { count, error } = await adm.from("profiles").select("id", { count: "exact", head: true });
      if (error) throw error;
      return count || 0;
    };
    const admins = async () => {
      const { count } = await adm.from("profiles").select("id", { count: "exact", head: true }).eq("role", "admin");
      return count || 0;
    };
    // Crea la cuenta (o toma la que ya existe con ese correo) y su perfil.
    const upsertUser = async (r: string, nt: boolean) => {
      let id: string | null = null;
      const c = await adm.auth.admin.createUser({ email, password: pw, email_confirm: true, user_metadata: { name } });
      if (c.data?.user) id = c.data.user.id;
      else {
        const { data: found } = await adm.rpc("auth_user_id", { mail: email });
        if (!found) return { error: c.error?.message || "No se pudo crear la cuenta." };
        const { data: had } = await adm.from("profiles").select("id").eq("id", found).maybeSingle();
        if (had) return { error: "Ese correo ya existe." };
        id = found as string;
        const u = await adm.auth.admin.updateUserById(id, { password: pw, email_confirm: true, user_metadata: { name } });
        if (u.error) return { error: u.error.message };
      }
      const p = await adm.from("profiles").upsert({ id, name, email, role: r, notify: nt });
      if (p.error) return { error: p.error.message };
      return { id };
    };

    if (action === "setup") {
      if (await admins()) return out(403, { error: "Ya existe un Administrador. Entra con tu correo y contraseña." });
      if (await profiles()) return out(403, { error: "Ya hay cuentas en la base. Para dar de alta un Administrador, pide ayuda a quien administra Supabase." });
      if (!name) return out(400, { error: "Escribe tu nombre." });
      if (!/.+@.+\..+/.test(email)) return out(400, { error: "Escribe un correo válido." });
      const bad = checkPw(); if (bad) return out(400, { error: bad });
      const r = await upsertUser("admin", true);
      if (r.error) return out(400, r);
      // v1.55.2 (auditoría de seguridad): si dos personas abren la Configuración inicial al mismo tiempo, las dos pasan la revisión de
      // arriba. Después de crear, se vuelve a contar: si ya hay otro perfil, se deshace esta cuenta y gana la que se creó primero.
      const { data: firsts } = await adm.from("profiles").select("id,created_at").order("created_at", { ascending: true }).order("id").limit(2);
      if ((firsts || []).length > 1 && firsts![0].id !== r.id) {
        await adm.auth.admin.deleteUser(r.id as string);
        return out(403, { error: "Ya hay cuentas en la base. Entra con tu correo y contraseña." });
      }
      return out(200, { ok: true, id: r.id });
    }

    // Todo lo demás: solo un Administrador con sesión.
    const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    const { data: who } = token ? await adm.auth.getUser(token) : { data: { user: null } };
    if (!who?.user) return out(401, { error: "Tu sesión venció. Vuelve a entrar." });
    const { data: me } = await adm.from("profiles").select("role").eq("id", who.user.id).maybeSingle();
    if (me?.role !== "admin") return out(403, { error: "Solo el Administrador gestiona usuarios." });

    if ((action === "create" || action === "update") && !role) return out(400, { error: "Elige el rol de la cuenta." });
    if (action === "create") {
      if (!name) return out(400, { error: "Escribe el nombre." });
      if (!/.+@.+\..+/.test(email)) return out(400, { error: "Escribe un correo válido." });
      const bad = checkPw(); if (bad) return out(400, { error: bad });
      const r = await upsertUser(role, notify);
      return r.error ? out(400, r) : out(200, { ok: true, id: r.id });
    }

    const id = txt(b.id, 60);
    const { data: cur } = await adm.from("profiles").select("id,role,email").eq("id", id).maybeSingle();
    if (!cur) return out(404, { error: "Ese usuario ya no existe." });

    if (action === "update") {
      if (!name) return out(400, { error: "Escribe el nombre." });
      if (!/.+@.+\..+/.test(email)) return out(400, { error: "Escribe un correo válido." });
      if (cur.role === "admin" && role !== "admin" && (await admins()) < 2) return out(400, { error: "Debe quedar al menos un Administrador." });
      if (pw) { const bad = checkPw(); if (bad) return out(400, { error: bad }); }
      const ch: Record<string, unknown> = { user_metadata: { name } };
      if (pw) ch.password = pw;
      if (email !== String(cur.email || "").toLowerCase()) {
        const { data: other } = await adm.rpc("auth_user_id", { mail: email });
        if (other && other !== id) return out(400, { error: "Ese correo ya existe." });
        ch.email = email; ch.email_confirm = true;
      }
      const u = await adm.auth.admin.updateUserById(id, ch);
      if (u.error) return out(400, { error: u.error.message });
      const p = await adm.from("profiles").update({ name, email, role, notify }).eq("id", id);
      if (p.error) return out(400, { error: p.error.message });
      if (pw && id !== who.user.id) await adm.rpc("cerrar_sesiones", { uid: id });   // v1.46.0: contraseña nueva = fuera de sus equipos
      return out(200, { ok: true });
    }

    // v1.46.0 (auditoría técnica R8): cerrar la sesión de una cuenta en todos sus equipos (tablet perdida, alguien que ya no
    // trabaja ahí). Borra sus sesiones en Supabase Auth: al vencer su acceso (máximo una hora) la app le pide entrar otra vez.
    if (action === "cerrar_sesiones") {
      if (id === who.user.id) return out(400, { error: "Para cerrar tu propia sesión usa «Salir»." });
      const { data: n, error } = await adm.rpc("cerrar_sesiones", { uid: id });
      if (error) return out(400, { error: error.message });
      return out(200, { ok: true, sesiones: n || 0 });
    }
    if (action === "delete") {
      if (id === who.user.id) return out(400, { error: "No puedes eliminar tu propio usuario." });
      if (cur.role === "admin" && (await admins()) < 2) return out(400, { error: "Debe quedar al menos un Administrador." });
      const d = await adm.auth.admin.deleteUser(id);
      if (d.error) return out(400, { error: d.error.message });
      return out(200, { ok: true });
    }
    return out(400, { error: "Acción desconocida." });
  } catch (e) {
    // v1.55.2 (auditoría de seguridad): el detalle va al registro de la función (Supabase → Edge Functions → Logs), no a la pantalla.
    console.error("usuarios:", e);
    return out(500, { error: "No se pudo completar. Intenta de nuevo en un momento." });
  }
});
