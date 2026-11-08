#!/bin/sh
# Corre las pruebas. Requiere: python3, Playwright con Chromium.
#   sh pruebas/correr_todo.sh                    → todas, varias a la vez (una por núcleo del equipo)
#   sh pruebas/correr_todo.sh ajustes_t menu_t   → solo esas (para probar solo lo que cambió)
#   J=1 sh pruebas/correr_todo.sh                → una por una
# v1.39.0: la lista sale sola de los archivos *_t.py (antes había que acordarse de agregarla aquí) y corren en paralelo,
# cada una con su carpeta temporal. rendimiento_t mide tiempos: corre al final y sola, para que las demás no la hagan ver lenta.
# Las que usan el Supabase de mentira van una tras otra (comparten el puerto 8790).
cd "$(dirname "$0")/.." || exit 1
python3 -m http.server 8765 >/dev/null 2>&1 & S=$!; sleep 1
# Las pruebas de pantallas usan el modo local (datos solo en el navegador, sin la base compartida).
# sincronizacion_t usa un Supabase de mentira (pruebas/supabase_falso.py, puerto 8790).
export BASE="${BASE:-http://localhost:8765/index.html?modo=local}"
J="${J:-$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)}"
if [ $# -gt 0 ]; then L="$*"; else L="e2e $(cd pruebas && ls *_t.py | sed 's/\.py$//' | tr '\n' ' ')"; fi
uno='t=$1; o=$(mktemp -d); if OUT="$o" python3 -I "pruebas/$t.py" >"/tmp/propesa_$t.log" 2>&1 && ! grep -q "^FAIL" "/tmp/propesa_$t.log";
 then printf "%-24s OK (%s verificaciones)\n" "$t" "$(grep -c "^PASS" /tmp/propesa_$t.log)"; else printf "%-24s FALLÓ (ver /tmp/propesa_%s.log)\n" "$t" "$t"; fi; rm -rf "$o"'
R=/tmp/propesa_resumen.txt; : >"$R"
# Las que levantan el Supabase de mentira (puerto 8790) no pueden ir al mismo tiempo: van en fila, junto con las demás.
N=$(cd pruebas && grep -l supabase_falso *_t.py | sed 's/\.py$//' | tr '\n' ' ')
en(){ case " $N " in *" $1 "*) return 0;; esac; return 1; }
for t in $L; do [ "$t" = rendimiento_t ] && continue; en "$t" && echo "$t"; done >/tmp/propesa_fila.txt
( while read -r t; do sh -c "$uno" _ "$t"; done </tmp/propesa_fila.txt | tee -a "$R" ) &
F=$!
for t in $L; do [ "$t" = rendimiento_t ] && continue; en "$t" || echo "$t"; done | xargs -P "$J" -I{} sh -c "$uno" _ {} | tee -a "$R"
wait $F  # solo la fila (el servidor también corre de fondo)
case " $L " in *" rendimiento_t "*) sh -c "$uno" _ rendimiento_t | tee -a "$R";; esac
kill $S
n=$(grep -c "FALLÓ" "$R"); v=$(grep -o "OK ([0-9]*" "$R" | grep -o "[0-9]*" | awk '{s+=$1} END{print s+0}')
echo "$(grep -c . "$R") grupos · $v verificaciones"
[ "$n" -eq 0 ] && echo "TODO BIEN" || { echo "$n pruebas fallaron"; exit 1; }
