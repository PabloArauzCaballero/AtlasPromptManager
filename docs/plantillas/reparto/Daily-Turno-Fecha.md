# Daily — turno &lt;día | noche&gt; — &lt;AAAA-MM-DD&gt;

> **AVANCE DEL TURNO: 0 / &lt;total&gt; — 0 %.** ← se llena al cerrar, con `microtareas HECHO / total`.
> MacBook 0/&lt;n&gt; · Legion 0/&lt;n&gt; · DellInspiron1 0/&lt;n&gt; · DellInspiron2 0/&lt;n&gt;.
> **`A MEDIAS` cuenta como no hecha. `DESCARTADO` no suma: se declara aparte con su motivo.**

> **Estado:** `REPARTIDO` al &lt;AAAA-MM-DD&gt;. Este documento se escribió **al repartir, antes del
> turno**; las filas de resultado se llenan con lo que cada máquina ejecute.

- **Turno:** &lt;día | noche&gt; · **Fecha:** &lt;AAAA-MM-DD&gt; · **Paquete fuente:** &lt;de dónde salen las tareas&gt;
- **Fuente del pedido (verbatim, con procedencia):** &lt;enlace&gt;
- **Verificación contra el código real:** &lt;enlace, o "ninguna" y por qué&gt;

## 0. Los hechos que ordenan el turno

1. &lt;lo que hay que saber sí o sí antes de empezar: corte de rama, entorno, qué está caído&gt;
2. &lt;lo que parece hecho y no lo está, o al revés&gt;
3. &lt;qué recurso es compartido y con quién hay que coordinar antes de tocarlo&gt;

## 1. Qué máquina tiene qué

| Máquina | Encargo | Repos | Hitos | Subtareas | Microtareas | Estado |
|---|---|---|---:|---:|---:|---|
| **MacBook** | [&lt;título&gt;](MacBook/&lt;Lote.Modulo&gt;/&lt;NombreTarea&gt;.md) | &lt;repo&gt; | 0 | 0 | 0 | `TODO` |
| **Legion** | [&lt;título&gt;](Legion/&lt;Lote.Modulo&gt;/&lt;NombreTarea&gt;.md) | &lt;repo&gt; | 0 | 0 | 0 | `TODO` |
| **DellInspiron1** | [&lt;título&gt;](DellInspiron1/&lt;Lote.Modulo&gt;/&lt;NombreTarea&gt;.md) | &lt;repo&gt; | 0 | 0 | 0 | `TODO` |
| **DellInspiron2** | [&lt;título&gt;](DellInspiron2/&lt;Lote.Modulo&gt;/&lt;NombreTarea&gt;.md) | &lt;repo&gt; | 0 | 0 | 0 | `TODO` |

## 2. Fronteras — quién toca qué

| Ruta | Dueña del turno | Nadie más la toca |
|---|---|---|
| &lt;ruta&gt; | &lt;máquina&gt; | sí |

Un cambio necesario en ruta ajena **se pide por acá**, no se hace "de paso" (regla 00 §3).

## 3. Recursos compartidos

Antes de tocar cualquiera de estos, avisá en este daily: base de datos de pruebas, cola de
despliegues, variables de entorno del servidor, túneles. Lo que sea configuración del host lo
decide una persona, no una sesión.

## 4. Cierre del turno

Cada máquina cierra con su `REPORTE.md` en `docs/trabajo/<fecha>-<slug>/` y **pega acá su avance
calculado**. Un turno sin reporte escrito es un turno que no se puede retomar.
