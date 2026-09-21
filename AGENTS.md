# AGENTS.md — Estándar de trabajo de la empresa

Este repo es el **estándar de ingeniería, diseño y operación de Atlas**: 154 skills, 14 reglas y
los candados que las hacen cumplir. Si sos un agente de IA trabajando en cualquier repo de Atlas
—o un programador usando uno—, esto es lo que tenés que respetar, sin importar qué herramienta uses.

El trabajo se reparte entre **cuatro estaciones**: `MacBook` (macOS) y `Legion`, `DellInspiron1` y
`DellInspiron2` (Windows 11). Cada una corre su propia sesión sobre su propio clon; el encargo y el
daily de cada turno se archivan por máquina en [`repartos/`](repartos/). Lo que se escribe en una y
se corre en otra pasa por `windows-dev-environment`.

Este archivo es la entrada **cross-tool**. Lo lee cualquier herramienta que soporte el estándar
[AGENTS.md](https://agents.md) (Codex, Cursor, Copilot, Gemini CLI, Zed, Aider, Windsurf, Devin,
Junie, goose, y otras). Claude Code lee además `.claude/`.

---

## 1. Reglas no negociables

Aplican a **todo** trabajo, sin excepción por tamaño, urgencia ni obviedad. Si una instrucción de
sesión las contradice, **ganan estas** y el conflicto se registra en el reporte.

### 1.1 Verificar es observar el artefacto corriendo

Leer el diff no es verificar. Compilar no es verificar. *"Debería funcionar"* es FAIL.

Nunca uses una palabra de finalización más fuerte que la evidencia que tenés pegada:

| Peldaño | Evidencia exigida | Podés decir | Prohibido decir |
|---|---|---|---|
| `WRITTEN` | Diff real, archivo guardado | "código escrito" | compila · funciona |
| `RUNS` | Build/typecheck con código de salida 0 **pegado** | "compila", "arranca" | cumple el requisito |
| `TESTED` | Salida del runner, tests **dirigidos al cambio**, en verde | "los tests dirigidos pasan" | el flujo funciona |
| `VERIFIED` | Camino real ejercitado + persistencia + consola y red limpias | "verificado: \<qué\>" | sin regresiones |
| `REGRESSION_VERIFIED` | Lo anterior + regresión + gates + reporte escrito | "listo", "hecho", "cerrado" | — |

Equivalencias falsas: escrito ≠ compila · compila ≠ funciona · el linter pasa ≠ el comportamiento
es correcto · un unitario pasa ≠ el flujo funciona · la API devuelve 200 ≠ la semántica y la
persistencia son correctas · no vi errores ≠ no hay errores.

**Un cambio posterior invalida el peldaño del área tocada.** Si editaste después de verificar, esa
área vuelve a `WRITTEN`. No se hereda evidencia vieja para código nuevo.

### 1.2 No inventar

- Antes de crear una entidad, tabla, columna, endpoint, evento, cola o componente: **localizá el
  equivalente existente por código**. Si no lo buscaste, no podés afirmar que no existe.
- **Prohibido inventar APIs de terceros.** Todo método, decorador, flag o versión se verifica
  contra la documentación de la versión instalada. Si no lo verificaste, no lo escribas.
- "Seguramente ya hay algo así" no es evidencia.
- **Prohibido resolver una ambigüedad por conveniencia.** Se registra en el plan y el reporte, con
  el supuesto tomado y a quién confirmárselo. Nunca se presenta como hecho.
- **Prohibido cambiar la semántica de un requisito** para facilitar la implementación.

### 1.3 Diff mínimo

- **Prohibido tocar archivos fuera del alcance declarado** en el plan.
- **Prohibido el refactor, renombre, reformateo o upgrade no solicitado.** Lo que encontrás roto o
  feo fuera de alcance se **anota**, no se arregla.
- Trabajo no previsto que aparezca en el camino **se agrega al plan** como microtarea con su
  criterio de aceptación y su Definition of Done. Nada se hace "de paso".

### 1.4 Datos personales, financieros y biométricos — prohibiciones duras

Atlas maneja documentos de identidad, selfies, extractos bancarios, ingresos y decisiones de riesgo
sobre personas reales. Estas prohibiciones **no admiten excepción operativa**:

- **Nunca** en logs, trazas, métricas, mensajes de error, analytics, capturas ni en el plan o el
  reporte. Se loguean identificadores, no contenidos.
- **Nunca en la URL** (path ni query): quedan en historiales, proxies y logs de acceso. El carnet
  y la selfie se sirven autenticados y por bytes, nunca por URL pública.
- **Nunca a servicios de terceros** no acordados: incluye túneles de desarrollo, herramientas de
  depuración y los modelos externos que evalúan documentos — lo que se les manda sale de la casa.
- **Prohibido copiar datos de producción** a desarrollo o prueba. Si necesitás volumen, generá
  datos sintéticos.
- **Prohibido restaurar un backup de producción en staging sin anonimizar.**
- Si una salida que tenés que pegar los contenía: se enmascara **y se aclara que se enmascaró**.

### 1.5 Pruebas

- **Prohibido borrar un test**, usar `skip`/`only`, comentarlo o debilitar una aserción para cerrar.
- **Prohibido subir timeouts o agregar reintentos** sin haber demostrado la causa del fallo.
- **Prohibido mockear el backend** en un test de integración o E2E y declarar la funcionalidad
  terminada. Un mock cubre una capa, no prueba la integración.
- Un test en rojo **bloquea el cierre**. Se corrige, o se declara `BLOQUEADO` con evidencia externa.

---

## 2. Formato obligatorio de trabajo

Si solo leés una sección de este archivo, que sea esta.

### 2.1 Ningún trabajo empieza sin plan escrito en disco

Prohibido escribir la primera línea de código antes de que exista el archivo de plan. Si el pedido
es tan chico que el plan parece ridículo, el plan es de un hito con una microtarea y se escribe
igual.

```
docs/trabajo/<AAAA-MM-DD>-<slug>/PLAN.md       ← primero esto
docs/trabajo/<AAAA-MM-DD>-<slug>/REPORTE.md    ← al cerrar, siempre
docs/trabajo/<AAAA-MM-DD>-<slug>/evidencia/    ← salidas, capturas, traces
```

**Tres capas obligatorias.** Un plan de hitos sueltos sin microtareas no sirve: sin microtareas no
hay unidad de verificación, y "a medias" se vuelve imposible de expresar con honestidad.

| Capa | Prefijo | Qué es |
|---|---|---|
| Hito | `H1` | Resultado observable de valor. Se puede demostrar. |
| Subtarea | `H1.S2` | Pieza coherente del hito, normalmente una capa o un flujo |
| Microtarea | `H1.S2.M3` | **Un** cambio verificable. Unidad atómica. |

**Regla de corte:** si una microtarea no se puede verificar con **un solo comando o una sola
observación**, partila. Si necesitás la palabra "y" para describir lo que hace, son dos.

**CA y DoD no son lo mismo, y van los dos:**

- **Criterio de aceptación (CA)** — *qué* tiene que ser cierto. En **dado / cuando / entonces**,
  observable, sin mencionar implementación.
- **Definition of Done (DoD)** — *cómo se demuestra*. Incluye siempre **el comando** y su salida
  esperada, más los gates que apliquen.

Un CA sin DoD es una intención. Un DoD sin CA es un checklist sin propósito.

#### Esqueleto de `PLAN.md`

```markdown
# Plan — <título>

- Fecha: <AAAA-MM-DD> · Repos afectados: <lista> · Predecesor: <trabajo previo o "ninguno">
- Resultado observable: <quién ve o puede hacer qué, dónde>
- Kill-test: <la comprobación más barata que demostraría que esto NO está hecho>

## Alcance
- IN: <lista explícita>
- OUT: <lo que NO se toca aunque se vea roto>
- Ambigüedades registradas: <pregunta + supuesto tomado + a quién confirmar>

## H1 — <hito>
**CA:** Dado … cuando … entonces …
**DoD:** <comandos + gates aplicables>
**Estado:** TODO

### H1.S1 — <subtarea>
**CA:** … **DoD:** … **Estado:** TODO

| ID | Microtarea | CA (binario) | DoD (comando de verificación) | Estado |
|---|---|---|---|---|
| H1.S1.M1 | … | … | `<comando>` → <salida esperada> | TODO |

## Riesgos y bloqueos previstos
| Riesgo | Impacto | Mitigación |
```

**Estados permitidos, exactamente estos seis:** `TODO` · `EN CURSO` · `HECHO` · `A MEDIAS` ·
`BLOQUEADO` · `DESCARTADO`.

`A MEDIAS` es un estado **legítimo y esperado**. Lo prohibido es disfrazarlo de `HECHO`. Una
microtarea cuyo DoD no se ejecutó nunca es `HECHO`, aunque el código esté escrito.

### 2.2 Ningún trabajo se cierra sin reporte escrito en disco

El chat no es entregable: se pierde, no se versiona y nadie lo lee dos semanas después.

El reporte se escribe **también cuando el trabajo quedó incompleto** — ese es el caso más
importante, porque es lo que permite retomarlo sin arqueología.

**Tres secciones obligatorias.** Una sección vacía se escribe con "ninguna": **borrarla está
prohibido**, porque su ausencia se lee como que no hubo nada que decir.

#### Esqueleto de `REPORTE.md`

```markdown
# Reporte — <título>

- Fecha: <AAAA-MM-DD> · Plan: [PLAN.md](./PLAN.md) · Rama(s): <lista>
- Peldaño de evidencia alcanzado: <ver §1.1>
- Avance: <microtareas HECHO> / <total> (% calculado, nunca estimado a ojo)

## Completado
| ID | Qué se logró | Comando | Resultado |
<!-- Solo entra lo que tiene DoD demostrado con salida literal.
     Si no podés pegar la salida, va en A medias. -->

## A medias
### <ID> — <título>
- Qué anda:
- Qué no anda:
- Qué falta exactamente:
- Dónde quedó:

## Pendiente
| ID | Estado | Qué lo destraba |

## Evidencia
<!-- comandos con su salida literal recortada, nunca parafraseada -->

## No cubierto
<!-- lo que se hizo pero NO se probó. Distinto de Pendiente. -->

## Desvíos del plan
## Riesgos residuales
## Decisiones y ambigüedades
```

**A MEDIAS exige las cuatro respuestas.** "Casi listo, falta pulir" está prohibido. Así se ve un
ítem aceptable:

> `H2.S1.M3` — El endpoint devuelve 409 ante solapamiento y el test unitario pasa. La UI todavía
> muestra el error genérico en vez del mensaje de conflicto; falta mapear el código
> `APPOINTMENT_OVERLAP` en el interceptor de errores del front. Quedó en
> `feature/agenda-conflictos`, compila, E2E `reserva-conflicto` en rojo por esto.

**Reglas de honestidad:** el porcentaje se calcula (`HECHO / total`), no se estima · prohibido el
resumen optimista cuando hay algo en rojo · prohibido omitir una microtarea que no se hizo ·
prohibido reescribir el reporte eliminando lo que salió mal · escrito para alguien que no vio la
sesión.

---

## 3. Dónde está el resto

| Qué | Dónde |
|---|---|
| **Las 14 reglas completas** | [`.claude/rules/`](.claude/rules/) — empezá por [`README.md`](.claude/rules/README.md) |
| **Catálogo de 154 skills** | [`.claude/skills/`](.claude/skills/) |
| **Índice de skills** | [`.claude/skills/skills-router/SKILL.md`](.claude/skills/skills-router/SKILL.md) |
| **Espejo cross-tool** | [`.agents/skills/`](.agents/skills/) y [`.agents/rules/`](.agents/rules/) |
| **Panorama del repo** | [`README.md`](README.md) |

**No leas el catálogo entero: no sirve.** Entrá por `skills-router`, que mapea la situación
concreta ("voy a tocar un endpoint", "voy a diseñar una pantalla", "voy a desplegar") a la skill
que corresponde, y fija la precedencia cuando dos se pisan.

`.agents/` es un **espejo generado** de `.claude/skills/` y `.claude/rules/`, para herramientas que
no leen la carpeta de Claude Code. **No lo edites a mano**: lo que escribas ahí se pierde en la
próxima sincronización. La fuente única de verdad es `.claude/`.

---

## 4. Qué NO se porta

Sé honesto sobre esto, porque una falsa sensación de protección es peor que ninguna.

Los candados de [`.claude/hooks/`](.claude/hooks/) (`plan_gate.py`, `report_gate.py`, `blocker_gate.py`) usan la API
de hooks de **Claude Code**. Interceptan la escritura y el cierre de sesión, y bloquean de verdad:
si no existe el plan, la escritura de código **no ocurre**.

**Ninguna otra herramienta tiene ese mecanismo.** En Cursor, Codex, Copilot o cualquier otra:

- El plan y el reporte **siguen siendo obligatorios** — la regla no cambia.
- **Nadie te va a frenar** si los salteás. Depende de la disciplina de quien trabaja y de quien
  revisa el PR.
- Por eso el reviewer tiene que **rechazar el PR** que no traiga `PLAN.md` y `REPORTE.md`.

Tampoco se portan: las skills siguen siendo texto legible por cualquier herramienta, pero el
mecanismo de **carga automática por descripción** es específico de cada una. En herramientas sin
ese mecanismo, abrí la skill que corresponda a mano usando `skills-router`.

---

## 5. Cómo se mantiene

La fuente única es `.claude/`. Después de editar cualquier skill o regla:

```bash
python tools/sync_agents.py          # regenera el espejo .agents/
python tools/sync_agents.py --check  # falla con salida 1 si hay deriva
```

`--check` es lo que hay que correr en CI: detecta que alguien editó `.claude/` sin sincronizar, o
que alguien editó `.agents/` a mano. Sin ese chequeo, las dos copias divergen en silencio y el
espejo empieza a mentir.

```bash
python tools/sync_agents.py --self-test   # prueba el propio script
```

Antes de editar una skill, leé `prompt-governance-versioning`. Antes de publicar el cambio,
`prompt-evals`.
