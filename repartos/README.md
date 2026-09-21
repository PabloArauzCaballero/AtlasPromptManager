# Repartos

Acá vive el encargo de cada turno, ya repartido. La estructura no es decorativa: la verifica
`tools/check_reparto.py` en cada PR, y un reparto al que le falta una pieza se ve igual de bien a
simple vista que uno completo.

```
repartos/<AAAA-MM-DD>/<PromptDia|PromptNoche>/Daily-<Dia|Noche>-<AAAA-MM-DD>.md
repartos/<AAAA-MM-DD>/<PromptDia|PromptNoche>/<Maquina>/<Maquina>-Daily-<Dia|Noche>-<AAAA-MM-DD>.md
repartos/<AAAA-MM-DD>/<PromptDia|PromptNoche>/<Maquina>/<NombreCorreccion.Modulo>/<NombreTarea>.md
```

## La unidad de reparto es la máquina

En Atlas el trabajo se reparte por **estación de trabajo**, no por persona. Cada una corre su propia
sesión sobre su propio clon, y el daily queda archivado por máquina para poder cruzar un resultado
con el entorno donde se produjo.

| Carpeta | Estación | Sistema | Qué implica |
|---|---|---|---|
| `MacBook` | MacBook | macOS | La única que puede compilar y firmar la app de iOS |
| `Legion` | Legion | Windows 11 | Ver `windows-dev-environment` antes de escribir un script que corra acá |
| `DellInspiron1` | Dell Inspiron 1 | Windows 11 | ídem |
| `DellInspiron2` | Dell Inspiron 2 | Windows 11 | ídem |

Los nombres de carpeta van **sin espacios** (`DellInspiron1`, no `Dell Inspiron 1`): una ruta con
espacios se parte sola en la terminal y en la mitad de los scripts. `tools/check_reparto.py` rechaza
cualquier otro nombre, justamente para que no se cuelen variantes.

Un script que se escribe en la MacBook y se corre en una Legion es el caso normal, no la excepción:
`python` (no `python3`), rutas con `\`, CRLF y puertos ocupados son los cuatro que más muerden.

## Cómo se emite un reparto

1. Copiá las plantillas de [`docs/plantillas/reparto/`](../docs/plantillas/reparto/).
2. Llenalas. El prompt de tarea **debe** traer la sección 1 de instalación del estándar, el
   kill-test, el alcance OUT, la tabla de ambigüedades, el Definition of Done del hito y las tres
   capas (`H1` → `H1.S1` → `H1.S1.M1`) con CA, DoD y Estado.
3. Verificá antes de subir:

```bash
python tools/check_reparto.py repartos/<AAAA-MM-DD>
python tools/check_skills_citadas.py
```

El primero valida la estructura y el contenido mínimo; el segundo, que ninguna skill citada en la
tabla de skills del prompt falte en `.claude/skills/`. **Ninguno de los dos juzga si el encargo está
bien escrito** — eso lo revisa una persona.
