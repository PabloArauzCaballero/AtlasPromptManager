---
name: component-architecture-solid
description: Cómo el diseño de un componente de UI encarna SOLID — una responsabilidad por componente (SRP), extensible por props/slots/composición sin editarlo (OCP), variantes que respetan el contrato base (LSP), props mínimas y cerradas en vez de un mega-componente (ISP) y dependencia de abstracciones en vez de del transporte (DIP). Usar al diseñar un componente, al revisar uno que creció con demasiadas props o un `switch` de negocio, o al decidir si partirlo, extenderlo por composición o pasarle su fuente de datos desde afuera.
---

# Arquitectura de componentes con SOLID

SOLID no es solo para clases de backend: un componente **es** una unidad con un
contrato público (inputs/outputs/slots). Los mismos cinco principios deciden si ese
contrato envejece bien o se pudre. Este es el nivel de diseño; el nivel de nombres y
funciones lo cubre `clean-code`, el catálogo de principios puros `solid-principles`, y la
ubicación por nivel `atomic-design-components`.

## Cada nivel atómico tiene su responsabilidad (mapa SOLID)

| Nivel | Responsabilidad única (SRP) | De qué NO debe saber |
|---|---|---|
| Átomo | Renderizar un elemento con sus estados y accesibilidad | Datos, dominio, otros componentes |
| Molécula | Componer pocos átomos para un propósito | De dónde vienen los datos |
| Organismo | Armar una sección con sentido, recibiendo datos por input | Cómo se obtienen/mutan los datos |
| Contenedor (smart) | Orquestar estado, datos y efectos | Detalles de presentación |

Si un componente sabe de dos filas de esta tabla, tiene dos razones para cambiar → SRP roto.

## 1. SRP — una responsabilidad, una razón para cambiar

Un componente hace **una** cosa. Señales de que hace más de una: mezcla traer datos con
pintarlos; tiene un bloque de presentación y otro de lógica de negocio; el nombre lleva
"y" ("tarjeta-y-editor"); el archivo pasa de ~150 líneas de template sin ser una página.

```tsx
// ❌ el mismo componente trae datos, filtra, pagina y pinta
export function ListaDeClientes() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  useEffect(() => { fetch('/api/clientes').then(/* ... */); }, []);
  // ...filtro, orden, paginado Y markup de la tabla
}
```
```tsx
// ✅ contenedor orquesta; presentacional pinta
export function PaginaDeClientes() {                    // contenedor
  const { data, isLoading } = useClientes();            // la consulta vive acá
  return <TablaDeClientes filas={data ?? []} cargando={isLoading} onOrdenar={...} />;
}

export function TablaDeClientes({ filas, cargando, onOrdenar }: Props) { /* solo pinta */ }
```

## 2. OCP — abierto a extensión, cerrado a modificación

Un componente estable (un átomo del design system, un organismo reusado) se **extiende sin
tocarlo**. Las tres palancas de extensión:

- **Props de variante** (unión cerrada): `tone`, `size`, `layout`.
- **Composición por slots**: `children` y props que reciben nodos (`header`, `footer`); el
  consumidor inyecta contenido sin que el componente sepa qué.
- **Render props**: una función que el consumidor pasa para piezas como la celda custom de una
  tabla (`renderCelda={(fila) => …}`).

```tsx
// ❌ cada caso nuevo edita el componente: crece un switch infinito
type Props = { kind: 'cliente' | 'comercio' | 'banco' | 'proveedor' | ... };
// dentro: switch (kind) { case 'cliente': … case 'comercio': … }
```
```tsx
// ✅ cerrado a modificación: el consumidor compone el cuerpo
export function TarjetaDeEntidad({ titulo, children }: { titulo: ReactNode; children: ReactNode }) {
  return <article><header>{titulo}</header>{children}</article>;
}
```

Regla: si agregar un caso de uso obliga a editar un componente compartido, OCP está roto.
Agregar una **variante nueva a la unión** sí es legítimo; agregar una **rama de negocio**
adentro no.

## 3. LSP — una variante no rompe el contrato

Toda variante de un componente debe ser usable donde se espera el componente, sin
sorpresas. Un `size="sm"` no puede dejar de emitir el output que emite `size="md"`; un
`variant="ghost"` de botón sigue siendo enfocable y activable por teclado.

- No condiciones el contrato a una prop: `onPick` se llama en **todas** las variantes o en
  ninguna. Un callback que aparece y desaparece según otra prop es una trampa.
- Nada de "esta prop solo funciona si esa otra vale X" sin que el tipo lo exprese. Si dos
  props son mutuamente excluyentes, modelalas como una sola unión discriminada.
- Preferí **composición a envoltorios que reimplementan**: envolver un componente para cambiarle
  el comportamiento por dentro suele violar LSP. Componé átomos, no reescribas organismos
  (`solid-principles` desarrolla composición sobre herencia).

## 4. ISP — props mínimas y cohesivas

Nadie debería depender de props que no usa. Un componente con 20 props opcionales obliga
a cada consumidor a entender las 20 y multiplica los estados imposibles.

```tsx
// ❌ mega-props: banderas sueltas, combinaciones inválidas posibles
type Props = { showHeader?: boolean; showFooter?: boolean; compact?: boolean;
               bordered?: boolean; elevated?: boolean; danger?: boolean; /* ... */ };
```
```tsx
// ✅ agrupá lo que viaja junto; cerrá las variantes
type Props = {
  variant?: 'flat' | 'bordered' | 'elevated';
  tone?: 'neutral' | 'danger';
  header?: ReactNode;      // slot, en vez de una bandera showHeader
  children: ReactNode;
};
```

Síntoma de ISP roto: más de ~6 props, banderas booleanas que eligen apariencia (eso es una
variante), o combinaciones de props que no tienen sentido juntas. Partí el componente o
agrupá las props relacionadas en un objeto/variante.

## 5. DIP — depender de abstracciones, no de concretos

Cuando un componente **necesita** una dependencia (un contenedor que trae datos), que dependa de
una **abstracción**, no de una implementación concreta. Así se testea con un doble y se cambia la
fuente sin tocar el componente.

```tsx
// ❌ acoplado al transporte: URL, headers y forma de la respuesta adentro del componente
export function PaginaDeSolicitudes() {
  useEffect(() => { fetch('/api/solicitudes').then(r => r.json()).then(setDatos); }, []);
}
```
```tsx
// ✅ depende de un puerto: un hook o un cliente tipado que se puede sustituir en el test
export function PaginaDeSolicitudes({ useSolicitudes = useSolicitudesDelServidor }: Props) {
  const { data } = useSolicitudes();
}
```

Los componentes **presentacionales** llevan DIP al extremo: no inyectan nada de datos;
reciben todo por props. DIP aplica sobre todo a los contenedores.

## Tabla de decisión: síntoma → principio → movida

| Síntoma | Principio | Movida |
|---|---|---|
| Trae datos y además pinta | SRP | Partir en contenedor (smart) + presentacional (dumb) |
| Un `switch` por caso de negocio crece con cada feature | OCP | Composición por slots / render prop |
| Un callback existe solo con cierta prop | LSP | Contrato uniforme o unión discriminada |
| Más de ~6 props, banderas de apariencia | ISP | Variantes cerradas, agrupar, partir |
| Hace `fetch` o usa un cliente concreto en algo reusable | DIP | Puerto inyectado, o subir la dependencia al contenedor |
| Se hereda una clase de componente para variar | LSP/OCP | Composición de átomos |

## Anti-patrones

- Un componente "hace todo" de una feature (God component).
- Herencia de componentes para compartir markup (usá composición y projection).
- Inputs que activan/desactivan otros inputs sin que el tipo lo modele.
- Servicio de datos o `Router` dentro de un átomo/molécula/organismo compartido.
- Agregar una rama `@if`/`@switch` de negocio a un componente del design system.

## Checklist

- [ ] El componente tiene una sola responsabilidad y una sola razón para cambiar (SRP).
- [ ] Se extiende por inputs/slots/plantillas, sin editar el componente estable (OCP).
- [ ] Toda variante respeta el mismo contrato de inputs/outputs (LSP).
- [ ] Inputs mínimos, cohesivos y con variantes cerradas; nada de banderas de apariencia (ISP).
- [ ] Las dependencias reales entran por abstracción inyectada; lo presentacional no inyecta datos (DIP).
- [ ] La responsabilidad vive en el nivel atómico correcto (`atomic-design-components`).
- [ ] La división estado/presentación es explícita: el contenedor trae datos y orquesta; el
      presentacional solo recibe props y emite eventos.
