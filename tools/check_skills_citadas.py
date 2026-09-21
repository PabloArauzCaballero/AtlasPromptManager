#!/usr/bin/env python
"""Cruza las skills citadas en los prompts del reparto contra las que existen en `.claude/skills/`.

Por qué existe: un prompt que manda cargar una skill que no existe manda a la nada. El programador
la busca, no la encuentra, y termina trabajando sin ella — o peor, inventándose qué diría.

Solo mira las tablas de skills de la sección 1, donde el nombre va entre backticks al principio de
la fila. No intenta adivinar menciones sueltas en prosa.

Uso:
    python tools/check_skills_citadas.py            # sale 1 si alguna no existe
    python tools/check_skills_citadas.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# La tabla de skills es la que encabeza con `| Skill |`. Cualquier otra tabla del
# reparto -modulos tocados, herramientas, candados- tambien lleva un nombre entre
# backticks en su primera celda, y no es una cita de skill.
CABECERA_SKILLS = re.compile(r"^\|\s*Skill\s*\|", re.I)
FILA_SKILL = re.compile(r"^\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|")
SEPARADOR = re.compile(r"^\|[\s:|-]+\|?\s*$")


def skills_de_texto(texto: str) -> list[str]:
    """Los nombres citados en las tablas de skills de un documento.

    El docstring del modulo siempre prometio mirar solo esas tablas; la primera
    implementacion miraba la primera celda de **cualquier** tabla, asi que un
    cuadro de modulos tocados (`clinical`, `messaging`) o de herramientas
    (`jest`, `typescript`) se leia como una skill inventada, y el gate se caia
    por documentos que no citan ninguna skill.
    """
    nombres: list[str] = []
    en_tabla_de_skills = False
    for linea in texto.splitlines():
        if CABECERA_SKILLS.match(linea):
            en_tabla_de_skills = True
            continue
        if not en_tabla_de_skills:
            continue
        if not linea.lstrip().startswith("|"):
            en_tabla_de_skills = False  # la tabla termino
            continue
        if SEPARADOR.match(linea):
            continue
        fila = FILA_SKILL.match(linea)
        if fila is not None:
            nombres.append(fila.group(1))
    return nombres


def skills_en_disco(raiz: Path) -> set[str]:
    base = raiz / ".claude" / "skills"
    if not base.is_dir():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir()}


def citadas(raiz: Path) -> dict[str, list[Path]]:
    """Mapa {skill citada: archivos que la citan}."""
    encontradas: dict[str, list[Path]] = {}
    repartos = raiz / "repartos"
    if not repartos.is_dir():
        return encontradas
    for md in sorted(repartos.rglob("*.md")):
        texto = md.read_text(encoding="utf-8")
        for nombre in skills_de_texto(texto):
            encontradas.setdefault(nombre, []).append(md)
    return encontradas


def revisar(raiz: Path) -> tuple[list[str], int, int]:
    existentes = skills_en_disco(raiz)
    citas = citadas(raiz)
    problemas = [
        f"{nombre}: citada en {len(archivos)} prompt(s) y NO existe en .claude/skills/"
        for nombre, archivos in sorted(citas.items())
        if nombre not in existentes
    ]
    return problemas, len(citas), len(existentes)


# ----------------------------------------------------------------- self-test

def self_test() -> int:
    casos: list[tuple[str, bool]] = []

    def check(nombre: str, cond: bool) -> None:
        casos.append((nombre, cond))

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / ".claude" / "skills" / "existe-esta").mkdir(parents=True)
        (base / ".claude" / "skills" / "y-esta").mkdir(parents=True)
        lote = base / "repartos" / "2026-01-01" / "PromptNoche" / "MacBook" / "A.B"
        lote.mkdir(parents=True)

        (lote / "T.md").write_text(
            "| Skill | Para que |\n|---|---|\n| `existe-esta` | si |\n| `y-esta` | si |\n",
            encoding="utf-8")
        p, n_citadas, n_disco = revisar(base)
        check("todas existentes -> sin problemas", p == [])
        check("cuenta las citadas", n_citadas == 2)
        check("cuenta las de disco", n_disco == 2)

        (lote / "T.md").write_text(
            "| Skill | Para que |\n|---|---|\n| `existe-esta` | si |\n| `no-existe` | no |\n",
            encoding="utf-8")
        p, _, _ = revisar(base)
        check("detecta una inventada", len(p) == 1)
        check("nombra la inventada", bool(p) and p[0].startswith("no-existe"))

        (lote / "T.md").write_text(
            "Texto suelto que menciona `no-existe` en prosa, sin tabla.\n", encoding="utf-8")
        p, n_citadas, _ = revisar(base)
        check("ignora menciones en prosa", p == [] and n_citadas == 0)

        # Una tabla que no es de skills: modulos tocados, herramientas, candados.
        # Es el caso que tenia el gate en rojo por documentos sin una sola skill.
        (lote / "T.md").write_text(
            "| Modulo | Que se toco |\n|---|---|\n| `messaging` | nada |\n",
            encoding="utf-8")
        p, n_citadas, _ = revisar(base)
        check("ignora las tablas que no son de skills", p == [] and n_citadas == 0)

        # Y la tabla de skills se sigue leyendo aunque venga despues de otra tabla.
        (lote / "T.md").write_text(
            "| Modulo | Que |\n|---|---|\n| `messaging` | nada |\n\n"
            "| Skill | Para que |\n|---|---|\n| `no-existe` | no |\n",
            encoding="utf-8")
        p, n_citadas, _ = revisar(base)
        check("lee la tabla de skills que viene despues de otra",
              len(p) == 1 and n_citadas == 1 and p[0].startswith("no-existe"))

        (base / "repartos2").mkdir()
        p, _, _ = revisar(base / "no-hay-nada-aca")
        check("raiz sin repartos ni skills no explota", p == [])

    fallos = [n for n, ok in casos if not ok]
    for nombre, ok in casos:
        print(f"  [{'PASS' if ok else 'FAIL'}] {nombre}")
    print(f"check_skills_citadas self-test: {len(casos) - len(fallos)} PASS, {len(fallos)} FAIL")
    return 1 if fallos else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="corre las pruebas internas")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    problemas, n_citadas, n_disco = revisar(RAIZ)
    if problemas:
        print("check_skills_citadas: HAY SKILLS CITADAS QUE NO EXISTEN")
        for p in problemas:
            print(f"  - {p}")
        return 1

    print(f"check_skills_citadas: OK, {n_citadas} skill(s) distinta(s) citada(s), "
          f"0 inexistentes (de {n_disco} en disco)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
