# &lt;Título del encargo: qué queda funcionando cuando esto esté hecho&gt;

> **Máquina:** &lt;MacBook | Legion | DellInspiron1 | DellInspiron2&gt; · **Fecha:** &lt;AAAA-MM-DD&gt; · **Turno:** &lt;día | noche&gt;
> **Fuente del pedido:** &lt;enlace al requisito, con procedencia&gt;
> **&lt;n&gt; hitos · &lt;n&gt; subtareas · &lt;n&gt; microtareas**, todas con criterio de aceptación y Definition of Done.

## 0. Ficha de asignación

| Campo | Valor |
|---|---|
| `REPO` | &lt;p. ej. `atlas/AtlasBackend`&gt; |
| `TARGET_REF` | &lt;rama y sha de corte. **Reconsultalo y fijá el tuyo** en tu `PLAN.md`&gt; |
| `RAMA DE TRABAJO` | Una tuya, saliendo de `origin/dev`. Nada directo sobre `dev`, nada sin PR |
| `ARCHIVOS RESERVADOS PARA VOS` | &lt;rutas&gt; |
| `ARCHIVOS DE OTRAS MÁQUINAS — NO LOS TOQUES` | &lt;rutas + quién las tiene&gt; |
| `CUENTA DE PRUEBA` | &lt;sintética declarada: se puede pegar en el reporte&gt; |
| `DÓNDE SE PRUEBA` | &lt;URL o comando exacto, y qué hace falta para llegar ahí&gt; |
| `LÍMITE DE RECURSOS` | Regla 70: un servidor de desarrollo, un build, un navegador, Playwright `--workers=1` |

## 1. Antes de escribir una línea — instalación OBLIGATORIA del estándar

> **Esta sección no es opcional y no es el final del día: es lo primero.** Un prompt ejecutado sin
> el estándar cargado produce trabajo que después hay que rehacer, porque no va a tener plan, ni
> evidencia, ni reporte. **Si no podés completar este paso, estás `BLOQUEADO`: avisalo y no sigas.**

### 1.1 Instalar el estándar en tu checkout

```bash
# 1. Clonar el estandar al lado del repo de producto
git clone https://github.com/PabloArauzCaballero/AtlasPromptManager.git ../AtlasPromptManager

# 2. Copiarlo DENTRO de tu checkout de trabajo (Claude Code solo carga desde ./.claude/)
cp -r ../AtlasPromptManager/.claude   ./
cp    ../AtlasPromptManager/AGENTS.md ./
cp -r ../AtlasPromptManager/.agents   ./   # solo si tu herramienta no lee .claude/

# 3. Verificar que quedo instalado (pega esta salida en tu daily)
ls .claude/skills | wc -l            # -> 155
ls .claude/rules/[0-9]*.md | wc -l   # -> 14  (mas el README, que no es una regla)
python .claude/hooks/plan_gate.py --self-test    # -> 11 PASS, 0 FAIL
```

En Windows (Legion, Dell Inspiron 1 y 2) el ejecutable es `python`, no `python3`, y las rutas van
con `\`. Ver `windows-dev-environment`.

**Si el `git clone` falla con 404:** pedí acceso y registralo como límite. **Un 404 no demuestra que
el repositorio no exista.**

### 1.2 Qué te instala eso

| Candado | Qué impide |
|---|---|
| `plan_gate.py` | Escribir código sin `PLAN.md` en disco. Nunca bloquea `.md` ni nada bajo `docs/` |
| `report_gate.py` | Cerrar la sesión con trabajo activo y sin `REPORTE.md`, o sin sus tres secciones |
| `blocker_gate.py` | Cerrar con microtareas en `BLOQUEADO` o `EN CURSO` sin declarar la simulación de los tres niveles del contrato (regla 65) |

**En cualquier otra herramienta los candados NO corren.** El plan y el reporte siguen siendo igual de
obligatorios; lo único que cambia es que nadie te va a frenar.

### 1.3 Skills que tenés que CARGAR para este lote

| Skill | Para qué |
|---|---|
| `skills-router` | la entrada al catálogo: mapea la situación concreta a la skill que toca |
| `outcome-first` | saber qué resultado observable se busca antes de leer código |
| `factual-discovery` | confirmar el sistema real antes de planificar |
| `milestone-planning` | descomponer en hitos, subtareas y microtareas con CA y DoD |
| `anti-hallucination-guard` | localizar lo existente antes de crear; no inventar APIs de terceros |
| `scope-discipline` | no tocar nada fuera del alcance declarado |
| `evidence-and-verification` | qué podés afirmar con qué evidencia |
| `rationalization-guard` | las excusas típicas para saltear una verificación, y su contramedida |
| `progress-reporting` | checkpoints visibles en cada apertura y cierre de microtarea |
| `finish-your-turn` | cómo se cierra el turno sin dejar trabajo colgado |
| &lt;+ las propias del tema: `nestjs-development`, `frontend-ux-states`, `e2e-playwright`, … &gt; | &lt;para qué&gt; |

## 2. Alcance

- **IN:** &lt;lista explícita de lo que sí se toca&gt;
- **OUT:** &lt;lo que NO se toca aunque se vea roto. Lo que encuentres roto acá se anota, no se arregla&gt;
- **Kill-test:** &lt;la comprobación más barata que demostraría que esto NO está hecho&gt;

### Ambigüedades registradas

| Duda | Supuesto tomado | A quién confirmar |
|---|---|---|
| &lt;pregunta abierta&gt; | &lt;lo que se asume mientras tanto&gt; | &lt;quién decide&gt; |

## H1 — &lt;hito: resultado observable que se puede demostrar&gt;

**CA:** Dado &lt;estado inicial&gt;, cuando &lt;acción&gt;, entonces &lt;resultado observable&gt;.
**DoD:** &lt;comandos + gates aplicables&gt;
**Estado:** TODO

### Definition of Done del hito

- [ ] &lt;comando&gt; → &lt;salida esperada, pegada literal en el reporte&gt;
- [ ] Gates que aplican: &lt;`visual-proof` si tocó UI · `data-privacy-sensitive` si tocó datos de personas · …&gt;

### H1.S1 — &lt;subtarea: una capa o un flujo coherente&gt;

**CA:** Dado &lt;…&gt;, cuando &lt;…&gt;, entonces &lt;…&gt;.
**DoD:** &lt;comando de verificación de la subtarea&gt;
**Estado:** TODO

| ID | Microtarea | CA (binario) | DoD (comando de verificación) | Estado |
|---|---|---|---|---|
| H1.S1.M1 | &lt;un solo cambio verificable&gt; | &lt;cierto o falso, sin matices&gt; | `<comando>` → &lt;salida esperada&gt; | TODO |
| H1.S1.M2 | &lt;…&gt; | &lt;…&gt; | `<comando>` → &lt;…&gt; | TODO |

> **Regla de corte:** si una microtarea no se puede verificar con un solo comando o una sola
> observación, partila. Si necesitás la palabra "y" para describir lo que hace, son dos.

## Riesgos y bloqueos previstos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| &lt;depende de otra máquina&gt; | &lt;qué se frena&gt; | Regla 65: nombrar el contrato y simular sus tres niveles |

## Cierre

- `docs/trabajo/<AAAA-MM-DD>-<slug>/PLAN.md` escrito **antes** de la primera línea de código.
- `docs/trabajo/<AAAA-MM-DD>-<slug>/REPORTE.md` al cerrar, **también si quedó a medias**, con sus
  tres secciones (Completado · A medias · Pendiente) y "No cubierto".
- Avance calculado (`HECHO / total`), nunca estimado a ojo.
