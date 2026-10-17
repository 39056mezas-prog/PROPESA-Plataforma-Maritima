#!/bin/sh
# Corre todas las pruebas. Requiere: python3, Playwright con Chromium. Uso: sh pruebas/correr_todo.sh
cd "$(dirname "$0")/.." || exit 1
python3 -m http.server 8765 >/dev/null 2>&1 & S=$!; sleep 1
# Las pruebas de pantallas usan el modo local (datos solo en el navegador, sin la base compartida).
# sincronizacion_t usa un Supabase de mentira (pruebas/supabase_falso.py) y dos navegadores a la vez.
export BASE="${BASE:-http://localhost:8765/index.html?modo=local}"
fallas=0
for t in inicio_t csp_t e2e ajustes_t menu_t correcciones_t piso_t entradas_t cajas_auto_t interruptor_t avisos_t pdf_t botones_t tabla_entrada_t estados_caja_t titulo_t recarga_t teclado_t tanques_t vistas_t sincronizacion_t fotos_t despierta_t atras_t cambio_modo_t eliminar_orden_t hoja_t temperatura_t vista_previa_t pesos_t editar_orden_t teclado_movil_t; do
  printf '%-16s ' "$t"; if python3 -I "pruebas/$t.py" >"/tmp/propesa_$t.log" 2>&1 && ! grep -q '^FAIL' "/tmp/propesa_$t.log"; then echo "OK ($(grep -c '^PASS' /tmp/propesa_$t.log) verificaciones)"; else echo "FALLÓ (ver /tmp/propesa_$t.log)"; fallas=$((fallas+1)); fi
done
kill $S; [ $fallas -eq 0 ] && echo "TODO BIEN" || { echo "$fallas pruebas fallaron"; exit 1; }
