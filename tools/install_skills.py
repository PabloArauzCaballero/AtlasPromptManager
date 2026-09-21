#!/usr/bin/env python
"""Instala el estándar (`.claude/skills/` y `.claude/rules/`) dentro de un repo de trabajo.

FUENTE ÚNICA DE VERDAD: este repositorio. En el repo de destino queda un ESPEJO, marcado como
generado. Lo que se edite allá se pierde en la próxima corrida; lo que se quiera cambiar de verdad
se cambia acá y se vuelve a instalar.

Por qué un espejo y no un enlace simbólico: el mismo motivo que ya documenta `sync_agents.py`. En
Windows los symlinks piden privilegios y git los maneja distinto según la plataforma, y tres de las
cuatro estaciones son Windows. Un espejo verificable es más portable que un enlace frágil — y
además viaja en el commit, así que la estación que clona el repo recibe el estándar sin un paso
manual que alguien se puede olvidar.

Qué NO hace, a propósito:

- **No borra lo que el repo tenga de propio.** `AtlasBackend` tiene nueve skills suyas
  (`graphify`, `backend-hardening`, …) que no existen acá. Son del repo, no del estándar: se
  respetan. Sólo se gestiona lo que este repositorio publica, y eso se lleva la cuenta en un
  manifiesto para poder retirar después una skill que acá se elimine.
- **No toca `settings.json` del destino.** Ahí viven los hooks propios del repo (el aviso de
  graphify, por ejemplo). Pisarlos para instalar skills sería romper una cosa para instalar otra.
- **No copia `.claude/hooks/`.** Los candados de plan/reporte de este repo son de ESTE repo: exigen
  `PLAN.md` y `REPORTE.md` en la raíz, y activarlos de golpe en tres repos de producción bloquearía
  cualquier edición hasta que alguien escriba esos archivos. Se instalan a conciencia, no de arrastre.

Uso:
    python tools/install_skills.py <repo> [<repo> ...]   # instala o actualiza
    python tools/install_skills.py --check <repo> ...    # NO escribe; sale 1 si hay deriva
    python tools/install_skills.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / ".claude"
CARPETAS = ("skills", "rules")
IGNORAR = {"__pycache__", ".pytest_cache", "runtime", ".DS_Store"}
MANIFIESTO = "estandar-instalado.json"

AVISO = (
    "<!-- ESPEJO GENERADO por AtlasPromptManager/tools/install_skills.py - NO EDITAR A MANO -->\n"
    "<!-- La fuente es AtlasPromptManager/.claude/{carpeta}/. Lo que edites aca se pierde. -->\n"
)


def _relevantes(base: Path) -> dict[str, Path]:
    """Archivos del árbol, relativos a `base`, saltando ruido de herramientas."""
    if not base.is_dir():
        return {}
    encontrados: dict[str, Path] = {}
    for ruta in base.rglob("*"):
        if not ruta.is_file():
            continue
        if any(parte in IGNORAR for parte in ruta.parts):
            continue
        encontrados[ruta.relative_to(base).as_posix()] = ruta
    return encontrados


def _con_aviso(contenido: bytes, carpeta: str) -> bytes:
    """Antepone el aviso de 'generado' a un Markdown, respetando el frontmatter YAML.

    El aviso va DESPUÉS del bloque `---` de metadatos: Claude Code lee `name` y `description` de
    ahí, y un comentario HTML antes del primer `---` rompe el parseo. Se descubrió probando, no
    suponiendo.
    """
    texto = contenido.decode("utf-8")
    aviso = AVISO.format(carpeta=carpeta)
    if texto.startswith("---"):
        cierre = texto.find("\n---", 3)
        if cierre != -1:
            corte = texto.find("\n", cierre + 1) + 1
            return (texto[:corte] + "\n" + aviso + texto[corte:]).encode("utf-8")
    return (aviso + "\n" + texto).encode("utf-8")


def _contenido_destino(origen: Path, carpeta: str) -> bytes:
    crudo = origen.read_bytes()
    return _con_aviso(crudo, carpeta) if origen.suffix == ".md" else crudo


def _mismo_contenido(esperado: bytes, destino: Path) -> bool:
    """Compara normalizando finales de línea: git reescribe CRLF en Windows y la deriva sería falsa."""
    try:
        return esperado.replace(b"\r\n", b"\n") == destino.read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return False


def _plan(destino_repo: Path) -> tuple[list[tuple[Path, bytes]], list[Path]]:
    """Qué habría que escribir y qué habría que retirar. No toca el disco."""
    escribir: list[tuple[Path, bytes]] = []
    gestionados: set[str] = set()

    for carpeta in CARPETAS:
        origen = ORIGEN / carpeta
        destino = destino_repo / ".claude" / carpeta
        for relativo, ruta in sorted(_relevantes(origen).items()):
            clave = f"{carpeta}/{relativo}"
            gestionados.add(clave)
            contenido = _contenido_destino(ruta, carpeta)
            if not _mismo_contenido(contenido, destino / relativo):
                escribir.append((destino / relativo, contenido))

    # Retirar SÓLO lo que este repositorio instaló antes y ya no publica. Lo que el repo de destino
    # tenga de propio nunca entra acá, porque nunca estuvo en el manifiesto.
    retirar: list[Path] = []
    previo = _leer_manifiesto(destino_repo)
    for clave in sorted(set(previo) - gestionados):
        candidato = destino_repo / ".claude" / clave
        if candidato.is_file():
            retirar.append(candidato)

    return escribir, retirar


def _leer_manifiesto(destino_repo: Path) -> list[str]:
    ruta = destino_repo / ".claude" / MANIFIESTO
    if not ruta.is_file():
        return []
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        return list(datos.get("archivos", []))
    except (OSError, ValueError):
        return []


def _escribir_manifiesto(destino_repo: Path) -> None:
    archivos = sorted(
        f"{carpeta}/{relativo}"
        for carpeta in CARPETAS
        for relativo in _relevantes(ORIGEN / carpeta)
    )
    ruta = destino_repo / ".claude" / MANIFIESTO
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(
            {
                "_comentario": (
                    "Generado por AtlasPromptManager/tools/install_skills.py. Lista lo que ESTE "
                    "estandar instalo en el repo, para poder retirarlo despues sin tocar lo propio "
                    "del repo. No editar a mano."
                ),
                "fuente": "AtlasPromptManager",
                "archivos": archivos,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def instalar(destino_repo: Path, *, solo_comprobar: bool) -> int:
    """Devuelve 0 si el destino quedó (o ya estaba) al día; 1 si hay deriva en modo `--check`."""
    if not destino_repo.is_dir():
        print(f"ERROR: {destino_repo} no existe")
        return 1

    escribir, retirar = _plan(destino_repo)
    manifiesto_al_dia = _mismo_contenido(
        (destino_repo / ".claude" / MANIFIESTO).read_bytes()
        if (destino_repo / ".claude" / MANIFIESTO).is_file()
        else b"",
        destino_repo / ".claude" / MANIFIESTO,
    ) and _leer_manifiesto(destino_repo) == sorted(
        f"{carpeta}/{relativo}" for carpeta in CARPETAS for relativo in _relevantes(ORIGEN / carpeta)
    )

    if solo_comprobar:
        if not escribir and not retirar and manifiesto_al_dia:
            print(f"OK  {destino_repo.name}: el estandar esta al dia")
            return 0
        for ruta, _ in escribir[:10]:
            print(f"DERIVA {destino_repo.name}: falta o difiere {ruta.relative_to(destino_repo)}")
        if len(escribir) > 10:
            print(f"DERIVA {destino_repo.name}: ... y {len(escribir) - 10} archivo(s) mas")
        for ruta in retirar[:10]:
            print(f"DERIVA {destino_repo.name}: sobra {ruta.relative_to(destino_repo)}")
        if not manifiesto_al_dia:
            print(f"DERIVA {destino_repo.name}: {MANIFIESTO} no refleja el estandar actual")
        return 1

    for ruta, contenido in escribir:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(contenido)
    for ruta in retirar:
        ruta.unlink()
        # Una carpeta de skill vacia despues de retirar su SKILL.md es ruido: se limpia.
        if not any(ruta.parent.iterdir()):
            ruta.parent.rmdir()
    _escribir_manifiesto(destino_repo)

    skills = len(_relevantes(ORIGEN / "skills"))
    reglas = len(_relevantes(ORIGEN / "rules"))
    print(
        f"OK  {destino_repo.name}: {skills} archivo(s) de skills y {reglas} de reglas; "
        f"{len(escribir)} escrito(s), {len(retirar)} retirado(s)"
    )
    return 0


def _self_test() -> int:
    """Prueba el propio candado. Si se rompe, deja de proteger sin que nadie se entere."""
    fallos: list[str] = []

    def check(condicion: bool, mensaje: str) -> None:
        if condicion:
            print(f"  ok   {mensaje}")
        else:
            print(f"  FAIL {mensaje}")
            fallos.append(mensaje)

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo-destino"
        (repo / ".claude" / "skills" / "propia-del-repo").mkdir(parents=True)
        (repo / ".claude" / "skills" / "propia-del-repo" / "SKILL.md").write_text(
            "---\nname: propia-del-repo\n---\ncontenido propio\n", encoding="utf-8"
        )
        (repo / ".claude").joinpath("settings.json").write_text('{"hooks":{}}', encoding="utf-8")

        check(instalar(repo, solo_comprobar=True) == 1, "un destino sin instalar reporta deriva")
        check(instalar(repo, solo_comprobar=False) == 0, "la instalacion termina bien")
        check(instalar(repo, solo_comprobar=True) == 0, "instalar dos veces no deja deriva (idempotente)")

        propia = repo / ".claude" / "skills" / "propia-del-repo" / "SKILL.md"
        check(propia.is_file(), "no borra las skills propias del repo")
        check("contenido propio" in propia.read_text(encoding="utf-8"), "no reescribe las skills propias")
        check(
            (repo / ".claude" / "settings.json").read_text(encoding="utf-8") == '{"hooks":{}}',
            "no toca settings.json del destino",
        )
        check(not (repo / ".claude" / "hooks").exists(), "no arrastra los hooks de este repo")

        instalada = repo / ".claude" / "skills" / "backend-development" / "SKILL.md"
        check(instalada.is_file(), "instala las skills del estandar")
        texto = instalada.read_text(encoding="utf-8")
        check(texto.startswith("---\n"), "el frontmatter sigue siendo lo primero del archivo")
        check("ESPEJO GENERADO" in texto, "el archivo instalado queda marcado como generado")
        check(
            texto.index("ESPEJO GENERADO") > texto.index("description:"),
            "el aviso va despues del frontmatter, no antes",
        )

        manifiesto = _leer_manifiesto(repo)
        check(len(manifiesto) > 100, f"el manifiesto lista lo instalado ({len(manifiesto)} archivos)")
        check(
            not any(clave.endswith("propia-del-repo/SKILL.md") for clave in manifiesto),
            "lo propio del repo NO entra en el manifiesto",
        )

        # Una skill que este repositorio deja de publicar se retira del destino; lo propio, no.
        huerfana = repo / ".claude" / "skills" / "ya-no-existe" / "SKILL.md"
        huerfana.parent.mkdir(parents=True)
        huerfana.write_text("---\nname: ya-no-existe\n---\n", encoding="utf-8")
        datos = json.loads((repo / ".claude" / MANIFIESTO).read_text(encoding="utf-8"))
        datos["archivos"].append("skills/ya-no-existe/SKILL.md")
        (repo / ".claude" / MANIFIESTO).write_text(json.dumps(datos), encoding="utf-8")
        instalar(repo, solo_comprobar=False)
        check(not huerfana.exists(), "retira lo que el estandar dejo de publicar")
        check(propia.is_file(), "y aun asi no toca lo propio del repo")

        modificada = repo / ".claude" / "skills" / "backend-development" / "SKILL.md"
        modificada.write_text("editado a mano\n", encoding="utf-8")
        check(instalar(repo, solo_comprobar=True) == 1, "una edicion a mano en el destino es deriva")

    print(f"\n{len(fallos)} fallo(s)." if fallos else "\nCandado sano.")
    return 1 if fallos else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("destinos", nargs="*", type=Path, help="repos donde instalar el estandar")
    parser.add_argument("--check", action="store_true", help="no escribe; sale 1 si hay deriva")
    parser.add_argument("--self-test", action="store_true", help="prueba el propio script")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()
    if not args.destinos:
        parser.error("hace falta al menos un repo de destino")

    salidas = [instalar(destino.resolve(), solo_comprobar=args.check) for destino in args.destinos]
    return max(salidas)


if __name__ == "__main__":
    sys.exit(main())
