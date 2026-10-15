-- PROPESA · Primer esquema de Supabase (aplicado el 12/oct/2026 en el proyecto propesa_bc).
-- Desde la v1.4.0 la app NO usa estas tablas: guarda todo en public.app_records (ver migrations/20261014_sincronizacion.sql y docs/SUPABASE.md).
-- Las reglas "ver" y "perfil propio o admin" de aquí se ajustaron en esa migración.
-- Todavía no se ha conectado ninguna cuenta. Este archivo se revisa y se aplica cuando se decida activar la sincronización.
-- Pesos de existencia en gramos (igual que la app). Las llaves son UUID para que varias tablets puedan crear datos sin chocar.

create table public.profiles (
  id uuid primary key references auth.users on delete cascade,
  name text not null,
  role text not null default 'consulta' check (role in ('admin','piso','consulta')),
  notify boolean not null default false,            -- recibe el informe por correo al cerrar un embarque
  created_at timestamptz not null default now()
);
create or replace function public.my_role() returns text
  language sql stable security definer set search_path = public as
$$ select role from public.profiles where id = auth.uid() $$;

create table public.lots (
  id uuid primary key default gen_random_uuid(),
  lot text not null unique,                         -- lote de recepción (MAYÚSCULAS)
  origin text not null,                             -- proveedor
  tank text not null,
  received_at timestamptz not null,
  temp_tank_f numeric, temp_product_f text,
  kg_per_box_in_tank numeric,                       -- "Kg por caja en tanque"
  waste_kg numeric,
  final_count_kg numeric, closed boolean not null default false,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(), updated_by uuid references auth.users
);
create table public.movements (                     -- existencia por talla; solo se agregan filas (las correcciones son reversas)
  id uuid primary key default gen_random_uuid(),
  lot_id uuid not null references public.lots on delete restrict,
  type text not null, size text not null, grams integer not null,
  reversed_of uuid references public.movements,
  created_at timestamptz not null default now(), created_by uuid references auth.users
);
create table public.orders (
  id uuid primary key default gen_random_uuid(),
  etd date not null,
  created_at timestamptz not null default now(), created_by uuid references auth.users
);
create table public.order_lines (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders on delete cascade,
  city text not null, consignee text not null,      -- clave del consignatario (p. ej. YISHUNHAI)
  client text not null, boxes integer not null check (boxes > 0)
);
create table public.shipments (                     -- un embarque puede juntar varias órdenes
  id uuid primary key default gen_random_uuid(),
  name text not null,
  hieleras_by_size integer[] not null default '{0,0,0,0}',
  components jsonb not null default '[]',           -- [[nombre, kg unitario, cantidad]]
  expected_gross_kg numeric not null default 0,
  alive integer, closed boolean not null default false, closed_at timestamptz, closed_by uuid references auth.users,
  updated_at timestamptz not null default now()
);
create table public.shipment_orders (
  shipment_id uuid not null references public.shipments on delete cascade,
  order_id uuid not null references public.orders on delete cascade,
  city text not null, consignee text not null,
  primary key (shipment_id, order_id, city, consignee)
);
create table public.boxes (                         -- las cajas se cuentan al EMPACAR cada pedido
  id uuid primary key default gen_random_uuid(),
  seq bigint generated always as identity,
  line_id uuid not null references public.order_lines on delete restrict,
  lot_id uuid not null references public.lots on delete restrict,
  shipment_id uuid not null references public.shipments on delete restrict,
  live_count integer not null check (live_count > 0),
  category text not null check (category in ('R','V','B')),   -- Rojo, Verde, Blanco
  created_at timestamptz not null default now(), created_by uuid references auth.users
);
create table public.notes (                         -- solo texto (en Empaque no hay fotos)
  id uuid primary key default gen_random_uuid(),
  scope text not null, scope_ref text,              -- 'recepcion', 'emp:<línea>', 'emb:<embarque>', 'cierre'
  body text not null, ref text, author text not null,
  created_at timestamptz not null default now()
);
create table public.reports (                       -- PDF final de cada paso (el mismo que se manda por correo)
  id uuid primary key default gen_random_uuid(),
  kind text not null, shipment_id uuid references public.shipments,
  file_path text not null,                          -- ruta en el bucket "reportes"
  sent_to text[] not null default '{}',
  created_at timestamptz not null default now(), created_by uuid references auth.users
);

-- Seguridad: nadie entra sin sesión. Ver = todos; capturar = admin y piso; borrar/administrar = admin.
do $$ declare t text; begin
  foreach t in array array['profiles','lots','movements','orders','order_lines','shipments','shipment_orders','boxes','notes','reports'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy "ver" on public.%I for select to authenticated using (true)', t);
  end loop;
  foreach t in array array['movements','boxes','notes'] loop
    execute format('create policy "capturar" on public.%I for insert to authenticated with check (public.my_role() in (''admin'',''piso''))', t);
  end loop;
  foreach t in array array['lots','orders','order_lines','shipments','shipment_orders','reports'] loop
    execute format('create policy "capturar" on public.%I for insert to authenticated with check (public.my_role() = ''admin'')', t);
    execute format('create policy "editar" on public.%I for update to authenticated using (public.my_role() = ''admin'')', t);
  end loop;
  foreach t in array array['movements','boxes','notes','lots','orders','order_lines','shipments','shipment_orders'] loop
    execute format('create policy "borrar" on public.%I for delete to authenticated using (public.my_role() = ''admin'')', t);
  end loop;
end $$;
create policy "perfil propio o admin" on public.profiles for update to authenticated using (id = auth.uid() or public.my_role() = 'admin');
-- El encargado de piso captura el conteo final del lote y las vivas al llegar:
create policy "piso conteo final" on public.lots for update to authenticated using (public.my_role() = 'piso');
create policy "piso vivas" on public.shipments for update to authenticated using (public.my_role() = 'piso');

-- Cambios en vivo para las pantallas de consulta (computadora o celular)
alter publication supabase_realtime add table public.lots, public.movements, public.orders, public.order_lines, public.shipments, public.shipment_orders, public.boxes, public.notes;

-- PDF de cada paso
insert into storage.buckets (id, name, public) values ('reportes', 'reportes', false) on conflict do nothing;
create policy "leer reportes" on storage.objects for select to authenticated using (bucket_id = 'reportes');
create policy "subir reportes" on storage.objects for insert to authenticated with check (bucket_id = 'reportes' and public.my_role() in ('admin','piso'));
