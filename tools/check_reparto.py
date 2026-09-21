#!/usr/bin/env python
"""Verifica que un reparto de prompts cumpla la estructura obligatoria.

La estructura la fija la convención del equipo:

    <AAAA-MM-DD>/<PromptDia|PromptNoche>/Daily-<Dia|Noche>-<AAAA-MM-DD>.md
    <AAAA-MM-DD>/<PromptDia|PromptNoche>/<Maquina>/<Maquina>-Daily-<Dia|Noche>-<AAAA-MM-DD>.md
    <AAAA-MM-DD>/<PromptDia|PromptNoche>/<Maquina>/<NombreCorreccion.Modulo>/<NombreTarea>.md

La unidad de reparto en Atlas es la MAQUINA, no la persona: cada una corre su propia sesion sobre
su propio clon, y el daily se archiva por maquina para poder cruzar un trabajo con el entorno en
el que se hizo (tres de las cuatro son Windows: ver la skill `windows-dev-environment`).

Por qué existe: un reparto al que le falta el daily de una máquina se ve igual de bien a simple
vista que uno completo. Revisarlo a ojo es exactamente lo que esta comprobación reemplaza.

Además exige que **todo prompt de tarea obligue a instalar y cargar el estándar** (sección 1).
Ese chequeo existe porque el primer reparto se entregó con cero menciones a las skills: nadie lo
notó hasta que se contó. Un prompt sin esa sección produce trabajo sin plan, sin evidencia y sin
reporte, que después hay que rehacer.

Exige además un contenido mínimo: tabla de microtareas, kill-test, alcance OUT, tabla de
ambigüedades y Definition of Done del hito. Sin esas piezas el encargo no es ejecutable: sin
microtareas no hay unidad de verificación, y sin kill-test nadie sabe cómo demostrar que NO está
hecho.

**Lo que este script NO puede hacer es juzgar si ese contenido es bueno.** Un prompt con las cinco
piezas presentes y mal escritas pasa el chequeo. Eso lo revisa una persona, no un script.

Uso:
    python tools/check_reparto.py repartos/2026-09-19     # sale 1 si falta algo
    python tools/check_reparto.py repartos/2026-09-19 repartos/2026-09-20 ...
    python tools/check_reparto.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

# Las cuatro estaciones de trabajo del equipo. El nombre de la carpeta va sin espacios para que
# sea manejable desde la terminal y desde git en las tres plataformas.
MAQUINAS = ("MacBook", "Legion", "DellInspiron1", "DellInspiron2")
TURNOS = {"PromptDia": "Dia", "PromptNoche": "Noche"}
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IGNORAR = {".DS_Store", "Thumbs.db"}

# Marcas que tiene que traer todo prompt de tarea. Son el minimo que lo hace ejecutable:
# sin la seccion de instalacion, quien lo recibe trabaja sin plan, sin evidencia y sin reporte.
MARCAS_OBLIGATORIAS = (
    ("instalación OBLIGATORIA", "la seccion 1 de instalacion obligatoria del estandar"),
    ("skills-router", "la entrada al catalogo de skills"),
    ("plan_gate.py --self-test", "el comando que verifica que el estandar quedo instalado"),
)

# Contenido minimo. No juzga la calidad —un script no puede—, pero si que las piezas que hacen
# ejecutable un encargo esten: sin kill-test nadie sabe como demostrar que NO esta hecho; sin
# alcance OUT se toca lo que no se debe; y sin tabla de ambiguedades, las dudas se resuelven por
# conveniencia en vez de registrarse.
CONTENIDO_MINIMO = (
    (re.compile(r"Kill-test", re.I), "el kill-test"),
    (re.compile(r"Ambigüedades registradas", re.I), "la tabla de ambiguedades a registrar"),
    # Ojo: el encabezado de la tabla de microtareas ya dice "Definition of Done", asi que
    # buscar el texto suelto daria por bueno un prompt sin la seccion. Se exige el encabezado.
    (re.compile(r"^#+ .*Definition of Done", re.M | re.I), "el Definition of Done del hito"),
    (re.compile(r"\*\*OUT:\*\*", re.I), "el alcance OUT (lo que NO se toca)"),
)

# Las TRES capas de la regla 20, con CA y DoD en cada una. Este chequeo existe porque un reparto
# se entrego con 0 de 30 prompts usando identificadores de tres capas y 0 con CA de subtarea:
# nadie lo noto hasta que se conto. Un plan de hitos sueltos sin microtareas no tiene unidad de
# verificacion, y "a medias" se vuelve imposible de expresar con honestidad.
HITO = re.compile(r"^#+ (H\d+) — ", re.M)
SUBTAREA = re.compile(r"^#+ (H\d+\.S\d+) — ", re.M)
MICROTAREA = re.compile(r"^\|\s*(H\d+\.S\d+\.M\d+)\s*\|", re.M)
CA = re.compile(r"^\*\*CA:\*\*", re.M)
DOD = re.compile(r"^\*\*DoD:\*\*", re.M)
ESTADO = re.compile(r"^\*\*Estado:\*\*\s*(.+)$", re.M)
ESTADOS_VALIDOS = {"TODO", "EN CURSO", "HECHO", "A MEDIAS", "BLOQUEADO", "DESCARTADO"}


def _subcarpetas(base: Path) -> list[Path]:
    return sorted(p for p in base.iterdir() if p.is_dir() and p.name not in IGNORAR)


def _archivos_md(base: Path) -> list[Path]:
    return sorted(p for p in base.iterdir() if p.is_file() and p.suffix == ".md")


def revisar(raiz: Path) -> list[str]:
    """Devuelve la lista de problemas. Lista vacía = estructura correcta."""
    problemas: list[str] = []

    if not raiz.is_dir():
        return [f"la carpeta de fecha no existe: {raiz}"]

    if not FECHA.match(raiz.name):
        problemas.append(
            f"el primer nivel debe ser una fecha AAAA-MM-DD, y es: '{raiz.name}'")

    fecha = raiz.name
    turnos = _subcarpetas(raiz)
    if not turnos:
        problemas.append(f"{fecha}/: no hay ninguna carpeta de turno")

    for turno in turnos:
        if turno.name not in TURNOS:
            problemas.append(
                f"{fecha}/{turno.name}/: turno no permitido "
                f"(solo {' o '.join(TURNOS)})")
            continue

        sufijo = TURNOS[turno.name]
        daily_equipo = turno / f"Daily-{sufijo}-{fecha}.md"
        if not daily_equipo.is_file():
            problemas.append(f"FALTA el daily de equipo: {_rel(daily_equipo, raiz)}")

        maquinas = _subcarpetas(turno)
        if not maquinas:
            problemas.append(
                f"{fecha}/{turno.name}/: no hay ninguna carpeta de máquina")

        for maquina in maquinas:
            if maquina.name not in MAQUINAS:
                problemas.append(
                    f"{fecha}/{turno.name}/{maquina.name}/: máquina desconocida "
                    f"(esperadas: {', '.join(MAQUINAS)})")
                continue

            daily = maquina / f"{maquina.name}-Daily-{sufijo}-{fecha}.md"
            if not daily.is_file():
                problemas.append(f"FALTA el daily de la máquina: {_rel(daily, raiz)}")

            lotes = _subcarpetas(maquina)
            if not lotes:
                problemas.append(
                    f"{fecha}/{turno.name}/{maquina.name}/: no tiene ninguna carpeta "
                    "<NombreCorreccion.Modulo> con su tarea")
                continue

            for lote in lotes:
                if "." not in lote.name:
                    problemas.append(
                        f"{_rel(lote, raiz)}/: el nombre del lote debe ser "
                        "<NombreCorreccion>.<Modulo>, con un punto")
                tareas = _archivos_md(lote)
                if not tareas:
                    problemas.append(
                        f"{_rel(lote, raiz)}/: no contiene ningún .md de tarea")
                for tarea in tareas:
                    problemas.extend(_revisar_prompt(tarea, raiz))

    return problemas


def _revisar_prompt(tarea: Path, raiz: Path) -> list[str]:
    """Exige que el prompt obligue a instalar y cargar el estándar."""
    try:
        texto = tarea.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{_rel(tarea, raiz)}: no se pudo leer ({exc})"]

    faltantes = [que for marca, que in MARCAS_OBLIGATORIAS if marca not in texto]
    faltantes += [que for patron, que in CONTENIDO_MINIMO if not patron.search(texto)]
    faltantes += _revisar_capas(texto)
    if faltantes:
        return [f"{_rel(tarea, raiz)}: le FALTA {', y '.join(faltantes)}"]
    return []


def _revisar_capas(texto: str) -> list[str]:
    """Las tres capas de la regla 20, cada una con CA, DoD y Estado."""
    hitos = HITO.findall(texto)
    subs = SUBTAREA.findall(texto)
    micros = MICROTAREA.findall(texto)
    fallas = []

    if not hitos:
        fallas.append("la capa de hito (ningún encabezado `H<n> — ...`)")
    if not subs:
        fallas.append("la capa de subtarea (ningún encabezado `H<n>.S<m> — ...`)")
    if not micros:
        fallas.append("microtareas con identificador de tres capas `H<n>.S<m>.M<k>`")
    if fallas:
        return fallas

    # Una subtarea que no cuelga de un hito declarado es un plan de capas sueltas.
    huerfanas = sorted({s.split(".")[0] for s in subs} - set(hitos))
    if huerfanas:
        fallas.append(f"el hito de la(s) subtarea(s) que cuelgan de {', '.join(huerfanas)}")
    sin_micro = sorted(set(subs) - {m.rsplit(".", 1)[0] for m in micros})
    if sin_micro:
        fallas.append(f"microtareas en la(s) subtarea(s) {', '.join(sin_micro)}")

    # CA, DoD y Estado se exigen en hito Y subtarea. Las microtareas los llevan en su fila.
    esperado = len(hitos) + len(subs)
    for patron, nombre in ((CA, "CA"), (DOD, "DoD"), (ESTADO, "Estado")):
        hay = len(patron.findall(texto))
        if hay < esperado:
            fallas.append(
                f"`**{nombre}:**` en {esperado - hay} de las {esperado} capas "
                f"(hay {hay}, hacen falta {esperado}: {len(hitos)} hitos + {len(subs)} subtareas)")

    invalidos = sorted({e.strip() for e in ESTADO.findall(texto)}
                       - ESTADOS_VALIDOS)
    if invalidos:
        fallas.append("estados inventados: " + ", ".join(repr(e) for e in invalidos))

    return fallas


def _rel(p: Path, raiz: Path) -> str:
    try:
        return f"{raiz.name}/{p.relative_to(raiz).as_posix()}"
    except ValueError:
        return str(p)


# ----------------------------------------------------------------- self-test

PROMPT_MINIMO = """# Tarea de prueba

## 1. Antes de escribir una línea — instalación OBLIGATORIA del estándar

Entrá por `skills-router`.

    python .claude/hooks/plan_gate.py --self-test

## 2. Resultado observable

Algo observable pasa.

**Kill-test:** la comprobación más barata que demuestra que NO está hecho.

## 3. Alcance

**IN:** esto.

**OUT:** aquello.

## 4. Plan

### H1 — Un hito

**CA:** Dado algo, cuando pasa algo, entonces algo observable.
**DoD:** Las microtareas en `HECHO` con su salida pegada.
**Estado:** TODO

#### H1.S1 — Una subtarea

**CA:** Dado algo, cuando pasa algo, entonces algo observable.
**DoD:** La microtarea en `HECHO` con su salida.
**Estado:** TODO

| ID | Microtarea | Criterio de aceptación | Definition of Done | Estado |
|---|---|---|---|---|
| H1.S1.M1 | Hacer algo | Está hecho | `<comando>` | TODO |

## 5. Ambigüedades registradas

| ID | Ambigüedad | Quién puede resolverla | Qué bloquea |
|---|---|---|---|
| Q-01 | algo | alguien | algo |

## 6. Definition of Done del hito

- [ ] La microtarea está en `HECHO` o en `BLOCKED`.
"""


def _armar_arbol_ok(base: Path, fecha: str = "2026-09-19") -> Path:
    """Construye un reparto mínimo y correcto: un turno, una máquina, un lote."""
    raiz = base / fecha
    turno = raiz / "PromptNoche"
    (turno / "MacBook" / "Dia1-Algo.Backend").mkdir(parents=True)
    (turno / f"Daily-Noche-{fecha}.md").write_text("x", encoding="utf-8")
    (turno / "MacBook" / f"MacBook-Daily-Noche-{fecha}.md").write_text("x", encoding="utf-8")
    (turno / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md").write_text(
        PROMPT_MINIMO, encoding="utf-8")
    return raiz


def self_test() -> int:
    casos: list[tuple[str, bool]] = []

    def check(nombre: str, condicion: bool) -> None:
        casos.append((nombre, condicion))

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        raiz = _armar_arbol_ok(base / "ok")
        check("arbol correcto no reporta problemas", revisar(raiz) == [])

        raiz = _armar_arbol_ok(base / "sin_daily_equipo")
        (raiz / "PromptNoche" / "Daily-Noche-2026-09-19.md").unlink()
        p = revisar(raiz)
        check("detecta falta de daily de equipo", len(p) == 1)
        check("nombra el daily de equipo faltante",
              "Daily-Noche-2026-09-19.md" in p[0] and "FALTA" in p[0])

        raiz = _armar_arbol_ok(base / "sin_daily_maquina")
        (raiz / "PromptNoche" / "MacBook" / "MacBook-Daily-Noche-2026-09-19.md").unlink()
        p = revisar(raiz)
        check("detecta falta de daily de máquina", len(p) == 1)
        check("nombra el daily de máquina faltante",
              "MacBook-Daily-Noche-2026-09-19.md" in p[0])

        raiz = _armar_arbol_ok(base / "lote_vacio")
        (raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md").unlink()
        p = revisar(raiz)
        check("detecta lote sin tarea", len(p) == 1 and "ningún .md" in p[0])

        raiz = _armar_arbol_ok(base / "sin_lote")
        import shutil as _sh
        _sh.rmtree(raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend")
        p = revisar(raiz)
        check("detecta máquina sin lote", len(p) == 1 and "NombreCorreccion" in p[0])

        raiz = _armar_arbol_ok(base / "lote_sin_punto")
        (raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend").rename(
            raiz / "PromptNoche" / "MacBook" / "Dia1AlgoBackend")
        p = revisar(raiz)
        check("detecta lote sin punto en el nombre",
              any("con un punto" in x for x in p))

        raiz = _armar_arbol_ok(base / "maquina_rara")
        (raiz / "PromptNoche" / "Fulano").mkdir()
        p = revisar(raiz)
        check("detecta máquina desconocida",
              any("máquina desconocida" in x for x in p))

        raiz = _armar_arbol_ok(base / "turno_raro")
        (raiz / "PromptTarde").mkdir()
        p = revisar(raiz)
        check("detecta turno no permitido",
              any("turno no permitido" in x for x in p))

        raiz = _armar_arbol_ok(base / "fecha_mala", fecha="19-09-2026")
        p = revisar(raiz)
        check("detecta primer nivel que no es fecha",
              any("AAAA-MM-DD" in x for x in p))

        check("carpeta inexistente se reporta, no explota",
              len(revisar(base / "no-existe")) == 1)

        raiz = base / "vacia" / "2026-09-19"
        raiz.mkdir(parents=True)
        p = revisar(raiz)
        check("fecha sin turnos se reporta",
              any("ninguna carpeta de turno" in x for x in p))

        # --- la seccion de instalacion del estandar es obligatoria ---
        raiz = _armar_arbol_ok(base / "sin_seccion_skills")
        tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
        tarea.write_text("# Tarea sin el estandar\n\nHace algo.\n", encoding="utf-8")
        p = revisar(raiz)
        check("detecta prompt sin la seccion de instalacion", len(p) == 1)
        check("nombra el prompt y que le falta",
              "Tarea.md" in p[0] and "FALTA" in p[0])

        raiz = _armar_arbol_ok(base / "sin_skills_router")
        tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
        tarea.write_text(
            PROMPT_MINIMO.replace("`skills-router`", "el catalogo"), encoding="utf-8")
        p = revisar(raiz)
        check("detecta prompt sin entrada por skills-router",
              any("catalogo de skills" in x for x in p))

        raiz = _armar_arbol_ok(base / "sin_verificacion")
        tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
        tarea.write_text(
            PROMPT_MINIMO.replace("plan_gate.py --self-test", "instalalo y listo"),
            encoding="utf-8")
        p = revisar(raiz)
        check("detecta prompt sin comando que verifique la instalacion",
              any("quedo instalado" in x for x in p))

        check("el daily NO se exige que traiga la seccion (solo los prompts de tarea)",
              revisar(_armar_arbol_ok(base / "daily_simple")) == [])

        # --- contenido minimo: sin estas piezas el encargo no es ejecutable ---
        for quitar, espera, nombre in (
            ("**Kill-test:** la comprobación más barata que demuestra que NO está hecho.",
             "kill-test", "kill-test"),
            ("## 5. Ambigüedades registradas", "ambiguedades", "ambiguedades"),
            ("## 6. Definition of Done del hito", "Definition of Done", "DoD del hito"),
            ("**OUT:** aquello.", "alcance OUT", "alcance OUT"),
        ):
            raiz = _armar_arbol_ok(base / ("sin_" + nombre.replace(" ", "_")))
            tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
            tarea.write_text(PROMPT_MINIMO.replace(quitar, ""), encoding="utf-8")
            p = revisar(raiz)
            check("detecta prompt sin %s" % nombre,
                  any(espera in x for x in p))

        # --- las tres capas de la regla 20 ---
        for quitar, espera, nombre in (
            ("### H1 — Un hito", "capa de hito", "capa de hito"),
            ("#### H1.S1 — Una subtarea", "capa de subtarea", "capa de subtarea"),
            ("| H1.S1.M1 | Hacer algo | Está hecho | `<comando>` | TODO |",
             "tres capas", "microtareas con ID de tres capas"),
        ):
            raiz = _armar_arbol_ok(base / ("falta_" + nombre.replace(" ", "_")))
            tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
            tarea.write_text(PROMPT_MINIMO.replace(quitar, ""), encoding="utf-8")
            check("detecta prompt sin %s" % nombre,
                  any(espera in x for x in revisar(raiz)))

        # CA, DoD y Estado se exigen en hito Y subtarea, no solo en las microtareas
        for patron, nombre in (("**CA:**", "CA"), ("**DoD:**", "DoD"), ("**Estado:**", "Estado")):
            raiz = _armar_arbol_ok(base / ("sin_%s_de_subtarea" % nombre))
            tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
            # quita solo la segunda aparicion: la de la subtarea
            texto = PROMPT_MINIMO
            i = texto.index(patron, texto.index(patron) + 1)
            texto = texto[:i] + texto[texto.index("\n", i) + 1:]
            tarea.write_text(texto, encoding="utf-8")
            p = revisar(raiz)
            check("detecta subtarea sin %s propio" % nombre,
                  any("`**%s:**` en 1 de las 2 capas" % nombre in x for x in p))

        raiz = _armar_arbol_ok(base / "subtarea_huerfana")
        tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
        tarea.write_text(PROMPT_MINIMO.replace("#### H1.S1 —", "#### H9.S1 —"),
                         encoding="utf-8")
        check("detecta subtarea que cuelga de un hito inexistente",
              any("H9" in x for x in revisar(raiz)))

        raiz = _armar_arbol_ok(base / "estado_inventado")
        tarea = raiz / "PromptNoche" / "MacBook" / "Dia1-Algo.Backend" / "Tarea.md"
        tarea.write_text(PROMPT_MINIMO.replace("**Estado:** TODO", "**Estado:** CASI LISTO", 1),
                         encoding="utf-8")
        check("detecta un estado inventado fuera de los seis de la regla 20",
              any("estados inventados" in x and "CASI LISTO" in x for x in revisar(raiz)))

    fallos = [n for n, ok in casos if not ok]
    for nombre, ok in casos:
        print(f"  [{'PASS' if ok else 'FAIL'}] {nombre}")
    print(f"check_reparto self-test: {len(casos) - len(fallos)} PASS, {len(fallos)} FAIL")
    return 1 if fallos else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rutas", nargs="*", help="una o varias carpetas de fecha del reparto")
    ap.add_argument("--self-test", action="store_true", help="corre las pruebas internas")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.rutas:
        ap.error("falta la carpeta de fecha del reparto (o usá --self-test)")

    fallo = False
    for ruta in args.rutas:
        raiz = Path(ruta).resolve()
        problemas = revisar(raiz)
        if problemas:
            fallo = True
            print(f"check_reparto: ESTRUCTURA INCOMPLETA en {raiz.name}")
            for p in problemas:
                print(f"  - {p}")
        else:
            print(f"check_reparto: OK, {raiz.name} cumple la estructura obligatoria")

    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
