-- PROPESA · v1.4.1 (14/oct/2026): guardar sin pisar lo que otro equipo cambió.
-- La app manda cada cambio con "b" = cómo estaba el registro en la base cuando el equipo lo cambió.
-- Si en la base ya es distinto (otro equipo lo cambió antes), no se guarda: gana la base y la función lo devuelve
-- para que la app lo muestre. Sin "b" (cambios que ya estaban en cola antes de la v1.4.1) se guarda como antes.
-- Corre con los permisos de quien llama (security invoker): las reglas de app_records siguen igual.
create or replace function public.push(rows jsonb)
  returns table (k text, v jsonb)
  language plpgsql security invoker set search_path = public as
$$
#variable_conflict use_column
declare r jsonb; nv jsonb; cur jsonb;
begin
  for r in select value from jsonb_array_elements(rows) loop
    nv := nullif(r->'v', 'null'::jsonb);
    select a.v into cur from public.app_records a where a.k = r->>'k' for update;
    if not found then
      insert into public.app_records (k, v) values (r->>'k', nv) on conflict (k) do nothing;
      if not found then return query select a.k, a.v from public.app_records a where a.k = r->>'k'; end if;
    elsif cur is not distinct from nv then
      null;                                               -- ya está igual: no se reescribe
    elsif r ? 'b' and cur is distinct from nullif(r->'b', 'null'::jsonb) then
      return query select r->>'k', cur;                   -- otro equipo lo cambió antes: gana la base
    else
      update public.app_records a set v = nv where a.k = r->>'k';
    end if;
  end loop;
end $$;
revoke all on function public.push(jsonb) from public, anon;
grant execute on function public.push(jsonb) to authenticated;
