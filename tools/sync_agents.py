#!/usr/bin/env python
"""Sincroniza `.claude/` -> `.agents/` para que otras herramientas de IA lean el mismo estándar.

FUENTE ÚNICA DE VERDAD: `.claude/skills/` y `.claude/rules/`.
`.agents/` es un ESPEJO GENERADO. Nunca se edita a mano: lo que se edite ahí se pierde
en la próxima corrida.

Por qué un espejo y no un enlace simbólico: en Windows los symlinks requieren privilegios
y git los maneja de forma inconsistente entre plataformas. Un espejo verificable es más
portable que un enlace frágil.

Por qué NO se copian los hooks: `.claude/hooks/` implementa candados con la API de hooks de
Claude Code. Otras herramientas no la tienen, así que copiarlos daría falsa sensación de
protección. La obligación se documenta en AGENTS.md; el candado automático solo existe en
Claude Code.

Uso:
    python tools/sync_agents.py            # sincroniza
    python tools/sync_agents.py --check    # NO escribe; sale 1 si hay deriva (para CI)
    python tools/sync_agents.py --self-test
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / ".claude"
DESTINO = RAIZ / ".agents"
CARPETAS = ("skills", "rules")
IGNORAR = {"__pycache__", ".pytest_cache", "runtime", ".DS_Store"}

AVISO = """<!-- GENERADO POR tools/sync_agents.py - NO EDITAR A MANO -->
<!-- La fuente es ../../.claude/{carpeta}/. Lo que edites aca se pierde en la proxima sync. -->
"""


def _mismo_contenido(a: Path, b: Path) -> bool:
    """Compara dos archivos por contenido, normalizando los finales de linea.

    Por que no `filecmp.cmp`: en Windows, git reescribe con CRLF el archivo que cambia al saltar
    de rama y deja el otro como estaba. Una comparacion byte a byte reporta entonces una deriva
    que NO existe, y quien la ve pierde el tiempo buscando un cambio que nadie hizo. Paso de
    verdad el 2026-09-20: `--check` canto deriva sobre un archivo identico salvo 100 CR.

    En Linux no se nota porque todo el arbol queda uniforme, asi que CI no lo habria atrapado.

    Lo que se espeja es texto. Lo que importa es el contenido, no como termina cada linea.
    """
    try:
        return (a.read_bytes().replace(b"\r\n", b"\n")
                == b.read_bytes().replace(b"\r\n", b"\n"))
    except OSError:
        return False


def _relevantes(base: Path) -> dict[str, Path]:
    """Mapa {ruta relativa posix: Path absoluto} de los archivos a espejar."""
    encontrados: dict[str, Path] = {}
    if not base.is_dir():
        return encontrados
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if any(parte in IGNORAR for parte in p.parts):
            continue
        rel = p.relative_to(base).as_posix()
        if rel == "LEEME-GENERADO.md":
            continue
        encontrados[rel] = p
    return encontrados


def comparar() -> tuple[list[str], list[str], list[str]]:
    """Devuelve (faltantes_en_destino, distintos, sobrantes_en_destino)."""
    faltan: list[str] = []
    distintos: list[str] = []
    sobran: list[str] = []
    for carpeta in CARPETAS:
        src = _relevantes(ORIGEN / carpeta)
        dst = _relevantes(DESTINO / carpeta)
        for rel, ruta in src.items():
            destino = DESTINO / carpeta / rel
            if rel not in dst:
                faltan.append(f"{carpeta}/{rel}")
            elif not _mismo_contenido(ruta, destino):
                distintos.append(f"{carpeta}/{rel}")
        for rel in dst:
            if rel not in src:
                sobran.append(f"{carpeta}/{rel}")
    return sorted(faltan), sorted(distintos), sorted(sobran)


def sincronizar() -> int:
    copiados = borrados = 0
    for carpeta in CARPETAS:
        src_base = ORIGEN / carpeta
        dst_base = DESTINO / carpeta
        src = _relevantes(src_base)
        dst = _relevantes(dst_base)

        for rel, ruta in src.items():
            destino = dst_base / rel
            if rel in dst and _mismo_contenido(ruta, destino):
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ruta, destino)
            copiados += 1

        for rel in dst:
            if rel not in src:
                (dst_base / rel).unlink()
                borrados += 1

        if dst_base.is_dir():
            for p in sorted(dst_base.rglob("*"), key=lambda x: len(x.parts), reverse=True):
                if p.is_dir() and not any(p.iterdir()):
                    p.rmdir()

        if src:
            dst_base.mkdir(parents=True, exist_ok=True)
            (dst_base / "LEEME-GENERADO.md").write_text(
                AVISO.format(carpeta=carpeta), encoding="utf-8"
            )

    print(f"sync: {copiados} archivo(s) copiado(s), {borrados} huerfano(s) borrado(s)")
    return 0


def revisar() -> int:
    faltan, distintos, sobran = comparar()
    if not (faltan or distintos or sobran):
        total = sum(len(_relevantes(ORIGEN / c)) for c in CARPETAS)
        print(f"sync --check: OK, {total} archivo(s) en espejo, sin deriva")
        return 0
    print("sync --check: DERIVA DETECTADA entre .claude/ y .agents/")
    for etiqueta, lista in (("falta en .agents", faltan),
                            ("difiere", distintos),
                            ("sobra en .agents", sobran)):
        for rel in lista:
            print(f"  [{etiqueta}] {rel}")
    print("\nCorregi con: python tools/sync_agents.py")
    return 1


def self_test() -> int:
    """Ejercita el contrato real sobre un arbol temporal, no solo las funciones puras."""
    global RAIZ, ORIGEN, DESTINO
    orig = (RAIZ, ORIGEN, DESTINO)
    fallos = 0
    total = 0

    def check(nombre: str, ok: bool) -> None:
        nonlocal fallos, total
        total += 1
        print(f"{'PASS' if ok else 'FAIL'}  {nombre}")
        if not ok:
            fallos += 1

    with tempfile.TemporaryDirectory() as tmp:
        RAIZ = Path(tmp)
        ORIGEN = RAIZ / ".claude"
        DESTINO = RAIZ / ".agents"
        (ORIGEN / "skills" / "una").mkdir(parents=True)
        (ORIGEN / "skills" / "una" / "SKILL.md").write_text("uno", encoding="utf-8")
        (ORIGEN / "rules").mkdir(parents=True)
        (ORIGEN / "rules" / "00.md").write_text("regla", encoding="utf-8")
        (ORIGEN / "skills" / "__pycache__").mkdir()
        (ORIGEN / "skills" / "__pycache__" / "x.pyc").write_bytes(b"\x00")

        check("check detecta deriva con destino vacio", revisar() == 1)
        sincronizar()
        check("tras sync, check queda limpio", revisar() == 0)
        check("copio el SKILL.md", (DESTINO / "skills" / "una" / "SKILL.md").is_file())
        check("copio la regla", (DESTINO / "rules" / "00.md").is_file())
        check("ignoro __pycache__", not (DESTINO / "skills" / "__pycache__").exists())
        check("dejo el aviso de generado", (DESTINO / "skills" / "LEEME-GENERADO.md").is_file())

        (ORIGEN / "skills" / "una" / "SKILL.md").write_text("dos", encoding="utf-8")
        check("detecta contenido cambiado", revisar() == 1)
        sincronizar()
        check("propaga el cambio",
              (DESTINO / "skills" / "una" / "SKILL.md").read_text(encoding="utf-8") == "dos")

        (DESTINO / "skills" / "huerfana").mkdir(parents=True)
        (DESTINO / "skills" / "huerfana" / "SKILL.md").write_text("sobra", encoding="utf-8")
        check("detecta huerfano en destino", revisar() == 1)
        sincronizar()
        check("borra el huerfano", not (DESTINO / "skills" / "huerfana").exists())

        (ORIGEN / "skills" / "una" / "SKILL.md").unlink()
        sincronizar()
        check("borrar en origen borra en espejo",
              not (DESTINO / "skills" / "una" / "SKILL.md").exists())
        check("el aviso no se cuenta como huerfano", revisar() == 0)

        # Mismo contenido, distinto final de linea. En Windows git reescribe con CRLF el archivo
        # que cambia al saltar de rama y deja el otro como estaba, asi que esto pasa de verdad:
        # se vio una "DERIVA DETECTADA" sobre un archivo identico salvo 100 CR.
        (ORIGEN / "rules" / "00.md").write_bytes(b"linea uno\nlinea dos\n")
        sincronizar()
        (DESTINO / "rules" / "00.md").write_bytes(b"linea uno\r\nlinea dos\r\n")
        check("mismo contenido con CRLF vs LF no es deriva", revisar() == 0)

        (DESTINO / "rules" / "00.md").write_bytes(b"linea uno\r\nOTRA COSA\r\n")
        check("una diferencia real sigue siendo deriva", revisar() == 1)

    RAIZ, ORIGEN, DESTINO = orig
    print(f"\nsync_agents self-test: {total - fallos} PASS, {fallos} FAIL")
    return 1 if fallos else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="no escribe; sale 1 si hay deriva")
    ap.add_argument("--self-test", action="store_true", help="corre las pruebas del propio script")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return revisar() if args.check else sincronizar()


if __name__ == "__main__":
    sys.exit(main())
