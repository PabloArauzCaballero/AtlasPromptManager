# AtlasPromptManager

Estándar de ingeniería, diseño y operación de Atlas, escrito como skills de Claude Code.

No es una colección de apuntes: es el manual de la casa. Cada skill dice **qué hacer**, **cómo
comprobarlo** y **qué evidencia hace falta** para poder afirmar que está hecho.

## Empezá acá

**[`skills-router`](.claude/skills/skills-router/SKILL.md)** — el índice. Mapea la situación
concreta (arrancar una tarea, tocar un endpoint, diseñar una pantalla, desplegar, cerrar un carril)
a la skill que hay que cargar, y fija la precedencia cuando dos se contradicen.

Con 154 skills, leer el catálogo entero no sirve. El router sí.

## Cómo se usa

Claude Code carga las skills desde el repo **donde se está trabajando**, no desde acá. Un estándar
que vive sólo en este repositorio está escrito y no aplica a nada. Se instala:

```bash
python tools/install_skills.py ../AtlasBackend ../AtlasAdminPortal ../AtlasExternalProvidersMock
python tools/install_skills.py --check ../AtlasBackend   # sale 1 si el destino quedó a la deriva
```

Queda un **espejo generado** —cada archivo lleva su aviso— y un manifiesto
`.claude/estandar-instalado.json` con lo que este repositorio puso ahí. Ese manifiesto es lo que
permite retirar después una skill que acá se elimine **sin tocar lo que el repo tenga de propio**:
`AtlasBackend`, por ejemplo, tiene nueve skills suyas (`graphify`, `backend-hardening`…) que
conviven con estas 154.

Espejo y no symlink por el mismo motivo que documenta `sync_agents.py`: en Windows los enlaces piden
privilegios y git los maneja distinto según la plataforma, y tres de las cuatro estaciones son
Windows. Además el espejo viaja en el commit, así que la estación que clona recibe el estándar sin
un paso manual que alguien pueda olvidar.

El instalador **no toca `settings.json`** del destino —ahí viven los hooks propios de cada repo— ni
arrastra `.claude/hooks/`: los candados de plan y reporte de este repositorio exigen `PLAN.md` y
`REPORTE.md` en la raíz, y encenderlos de arrastre bloquearía cualquier edición en un repo de
producción hasta que alguien los escriba. Eso se enciende a conciencia.

Una vez instaladas, Claude Code las carga sola cuando la `description` matchea la tarea; también se
las puede invocar por nombre. El paso a paso está en la plantilla de
[prompt de tarea](docs/plantillas/reparto/NombreTarea.md), §1.

Los **hechos de cada proyecto** (comandos reales, invariantes del modelo, prohibiciones, rutas)
no viven acá: viven en el `CLAUDE.md` de ese repo, y **mandan sobre cualquier skill**. Cómo
escribir ese archivo está en `claude-md-authoring`.

## Las cuatro estaciones

El trabajo se reparte por **máquina**, no por persona: cada una corre su propia sesión sobre su
propio clon.

| Carpeta en `repartos/` | Estación | Sistema |
|---|---|---|
| `MacBook` | MacBook | macOS — la única que compila y firma la app de iOS |
| `Legion` | Legion | Windows 11 |
| `DellInspiron1` | Dell Inspiron 1 | Windows 11 |
| `DellInspiron2` | Dell Inspiron 2 | Windows 11 |

Tres de cuatro son Windows: un script escrito en la MacBook y corrido en una Legion pasa por
`windows-dev-environment` antes de darse por portable. La convención completa del reparto está en
[`repartos/README.md`](repartos/README.md).

## Qué hay adentro

| Área | Cant. | Qué cubre |
|---|---|---|
| **Disciplina del agente** | 15 | Evidencia, anti-alucinación, alcance, causa raíz, plan por hitos, cierre de turno. Los gates que mandan sobre todo lo demás. |
| **Oficio de este repo** | 8 | Escribir skills, prompts, evals, subagentes, hooks, gobernanza. El manual de su propio producto. |
| **Backend** | 20 | Arquitectura, NestJS, PostgreSQL, concurrencia, errores, auth, multi-tenancy, colas, jobs, caché, notificaciones, archivos, búsqueda, tiempo real, mapas, observabilidad. |
| **Datos y modelo** | 9 | Esquema dirigido por modelo, PlantUML, catálogos cerrados, seeds con procedencia, calidad, auditoría, backups, tooling Python. |
| **Frontend y diseño** | 27 | Componentes, CSS, sistema de diseño, color, tipografía, jerarquía visual, calidad UI, UX, estados, formularios, responsive, accesibilidad, performance, i18n, SEO, prueba visual. |
| **Mobile** | 3 | UX táctil, offline y sincronización, seguridad y publicación en tiendas. |
| **QA** | 20 | Estrategia, orquestación, unitarios, API, integridad, E2E, visual, carga, triage, datos sintéticos, casos límite, exploratorio, UAT, evidencia. |
| **Seguridad** | 13 | Guardrails, threat modeling, privacidad de datos personales, cumplimiento, revisión con lente de seguridad, evaluación sobre sistemas propios, reporte y remediación. |
| **Dominio negocio** | 2 | Partida doble y facturación. |
| **Calidad de código** | 11 | Clean code, SOLID, eficiencia, gates, linting, complejidad, deuda, código muerto, auditoría, code review, refactor. |
| **Proceso y GitHub** | 17 | Carriles, requisitos, slicing, bugs, git multi-repo, PRs, issues, rulesets, CI, releases, ADRs, dependencias, incidentes. |
| **Despliegue y entorno** | 9 | Coolify, Docker, verificación post-deploy, release y rollback, secretos, entorno Windows. |

## Las reglas que atraviesan todo

1. **Verificar es observar el artefacto real corriendo.** Leer el código no cuenta. Compilar no
   cuenta. Toda afirmación va con la salida literal pegada, y con la sección "No cubierto".
2. **No inventar.** Antes de crear una entidad, endpoint, catálogo o API, localizar el equivalente
   existente. Las ambigüedades se registran, no se resuelven por conveniencia.
3. **Diff mínimo.** Nada de refactors, renombres ni "aprovechadas" fuera de lo pedido.
4. **Los datos de personas mandan.** Si el cambio toca documentos de identidad, selfies, extractos,
   ingresos o decisiones de riesgo, `data-privacy-sensitive` aplica aunque nadie lo haya pedido.
5. **Datos reales con procedencia, o sintéticos declarados.** Nunca datos ficticios presentados
   como reales, ni datos de producción en entornos de prueba.

## De dónde viene y qué se dejó afuera

El catálogo viene del estándar de otro producto de la casa
([AlovidaPromptManager](https://github.com/PabloArauzCaballero/AlovidaPromptManager), 176 skills) y
se recortó al stack y al dominio de Atlas. **No se portaron 22 skills**, por materia que Atlas no
tiene:

- **Angular y Astro** (8): el frontend de Atlas es Next.js. Las convenciones del framework las fija
  el `CLAUDE.md` de cada repo; no hay skill de framework acá.
- **Flutter** (4): la app es Expo/React Native. Quedaron las tres de mobile que no dependen del
  framework (táctil, offline, publicación), con sus ejemplos de Flutter señalados en el router.
- **MikroORM** (1): Atlas usa Sequelize y Prisma. Los patrones de persistencia portables están en
  `database-design` y `concurrency-and-locking`.
- **Dominio salud** (5) y **dominio Alovida** (4): registro clínico, recetas, FHIR, consentimiento
  clínico, agenda de citas, seguros, feed social y directorios públicos.

`data-privacy-phi` se conservó reescrita como **`data-privacy-sensitive`**: la materia existe en
Atlas —documento de identidad, selfie, extracto bancario, ingresos, score— aunque no sea dato de
salud.

**Lo que sigue teniendo olor a salud:** varias skills conservan ejemplos del producto de origen
(«paciente», «expediente clínico») en su prosa. Se dejaron a propósito: el criterio que enseñan es
el mismo y reescribirlos entero sin verificarlos habría sido peor que dejarlos. Si uno confunde,
corregilo con `prompt-governance-versioning`.

## Estado

Las skills fueron verificadas contra documentación oficial al momento de escribirlas (`docs.nestjs.com`,
PostgreSQL/PostGIS, Playwright, `docs.github.com`, `coolify.io/docs`, OWASP, W3C/WCAG, `web.dev`).
Donde un dato no se pudo confirmar, la skill lo dice explícitamente en vez de afirmarlo.

Esto envejece. Antes de editar una skill, leé `prompt-governance-versioning`; antes de publicar el
cambio, `prompt-evals`.
