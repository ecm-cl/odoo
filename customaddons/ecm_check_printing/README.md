# Valsegur Check Printing

Impresión de cheques propios sobre el formulario preimpreso de cada banco.

## Por que este addon y no `account_check_printing`

Valsegur gestiona los cheques con `l10n_latam_check` (método de pago `own_checks`,
número en `l10n_latam_check_number`, fecha de cobro diferida). En Odoo 19 ese modulo
esta desacoplado de `account_check_printing` y su impresión esta deshabilitada a
propósito, porque no existe un formato estándar: Odoo espera un reporte por banco.
`account_check_printing` además no trae ninguna plantilla QWeb, y no hay modulo
`l10n_cl_check_printing` ni en Community, ni en Enterprise, ni en el App Store.

Este addon imprime directamente sobre `l10n_latam.check`, sin instalar
`account_check_printing` y sin alterar el flujo de cheques existente.

## Como funciona

El reporte dibuja cada dato en una posición absoluta en milímetros. Las posiciones
se guardan **en el diario bancario**, de modo que cada banco se calibra desde la
interfaz, sin tocar código:

Contabilidad / Configuración / Diarios / <banco> / pestaña **Cheques**

- `Imprimir cheques desde Odoo`: habilita el boton en ese diario.
- Formulario del banco: ancho, alto, tamaño de letra, ciudad, mayúsculas,
  fecha en una línea o en casilleros separados.
- Posición de los campos: coordenadas X/Y de ciudad, fecha, monto en números,
  monto en letras y beneficiario.
- Calibración de la impresora: `ajuste horizontal` y `ajuste vertical` corren
  todos los campos a la vez para corregir la deriva del equipo.

## Calibrar un banco nuevo

1. En el diario, marcar `Imprimir cheques desde Odoo` y cargar ancho y alto reales
   del cheque.
2. Pulsar **Imprimir grilla de calibración** e imprimirla sobre un cheque anulado
   del banco.
3. Leer en la grilla la coordenada de cada campo y cargarla en el diario.
4. Imprimir un cheque real anulado y ajustar con los dos campos de calibración.

La hoja por defecto es `Hoja de cheque (98 x 190 mm)`, la misma que usa Flex. Si
un banco necesita otra, duplicar el formato en Ajustes tecnicos, asignarlo al
reporte y cargar las medidas en el diario.

## Opciones al imprimir

El boton **Imprimir cheque** abre un dialogo antes de generar el PDF:

- **Tipo de cheque**: `Nominativo` tacha con asteriscos las leyendas
  *a la orden de* y *o al portador*; `A la orden` tacha solo *o al portador*;
  `Al portador` no tacha nada. El valor inicial lo pone el diario.
- **Cruzado**: dibuja las dos rayas paralelas, de modo que el cheque solo se
  pueda depositar en cuenta.
- **Imprimir el '20' del año**: apagarlo cuando el formulario del banco ya
  trae impreso el `20` y solo quedan libres los dos últimos casilleros. El
  aplicativo Flex lo deja apagado.
- **Hoja**: la del cheque, o una hoja carta para calibrar a contraluz contra
  un cheque real.

El boton **Imprimir** abre el dialogo de impresión del sistema con el cheque ya
cargado. Desde ese dialogo el propio navegador permite guardar en PDF si hace
falta, de modo que no hay un segundo boton de descarga.

## La hoja

El cheque no se imprime solo: va dentro de una hoja cuyo tamaño es el que
queda configurado en la impresora. La hoja son 76,2 x 160 mm y el cheque
70 x 160, de modo que solo sobran 6,2 mm, a lo ancho y repartidos a los dos
lados. Dónde se apoya lo dice el diario en `Hoja: posición X / Y`.

El PDF se compagina horizontal -que es como están medidas las coordenadas- y la
página se gira un cuarto de vuelta al generarse, en lugar de rotar el HTML:
wkhtmltopdf dibuja mal las transformaciones CSS. El resultado es que la hoja
entra por el lado corto, igual que con Flex.

El tamaño de hoja de Odoo es un entero en milímetros y 76,2 no lo es, así que
el formato declara 161 x 77 y el código recorta el `MediaBox` a la medida
exacta al girar la página, anclando el recorte en la esquina superior
izquierda para no mover ningún campo.

## Valores por banco

Los cuatro bancos usan el mismo trazado de formulario; lo unico que cambia es
donde imprimio cada uno las leyendas *a la orden de* y *o al portador*, un par
de milimetros. Medido sobre los escaneos a 600 dpi de `06_Cheques`, en
coordenadas de la HOJA (el cheque se apoya adentro, con margen de 3,35 x 13,58 mm):

| Banco | orden X / Y / ancho | portador X / Y / ancho | trae el '20' |
|---|---|---|---|
| Banco de Chile | 13,73 / 42,80 / 15,70 | 141,81 / 44,80 / 17,00 | si |
| BCI            | 13,73 / 42,80 / 15,70 | 138,64 / 44,49 / 18,10 | **no** |
| Banco Estado   | 10,71 / 43,50 / 16,49 | 141,81 / 46,40 / 15,80 | si |
| Banco Itau     | 13,73 / 42,80 / 15,70 | 141,81 / 43,98 / 15,80 | si |

El resto de las coordenadas es identico en los cuatro. BCI es el unico cuyo
formulario no trae impreso el `20` del anio, asi que su diario va con
`el '20' del anio viene impreso` apagado.

Estos valores viven en la base, en las columnas `vsg_check_*` de
`account_journal`: una fila por diario. Se cargan desde la pestania Cheques del
diario y viajan dentro del respaldo de la base, de modo que al subir la base a
otro servidor van incluidos. No hay nada que recargar a mano ni migraciones que
los escriban.

Los valores por defecto de los campos son los de Banco de Chile, y solo se
aplican a diarios nuevos.

## Como configurar la impresora

El papel es un tamanio **personalizado** de 76,2 x 160 mm, creado en el driver
con el nombre "Cheque". 160 es el largo exacto del cheque; 76,2 son 3 pulgadas,
el ancho minimo que acepta la LaserJet 1020 y por tanto lo mas estrecho posible.
El cheque mide 70 x 160.

Antes se uso el tamanio estandar Sobre Monarch, 98,42 x 190,5. Se descarto
porque deja 30,5 mm de holgura a lo largo, y el cheque no cae donde uno supone
dentro de esa holgura: de ahi salio un desplazamiento de 27 mm que costo media
tarde encontrar. Con un papel del largo exacto del cheque ese eje deja de poder
equivocarse, y a lo ancho la holgura baja de 28,4 a 6,2 mm.

**El cheque se imprime centrado, no pegado a un lado.** Las guias del
alimentador no bajan de 76 mm y el cheque mide 70, asi que nunca lo sujetan;
pero la impresora lo recentra al tirar de el. Por eso `Hoja: posicion Y` vale
3,1, que es (76,2 - 70) / 2.

### No imprimir desde el dialogo de Chrome

Chrome muestra el tamanio "Cheque" en su lista pero no lo respeta al enviar el
trabajo: manda otro tamanio y centra la pagina dentro de el, con lo que el
cheque sale corrido unos 6 cm. El dialogo del sistema si lo respeta.

La forma fiable:

1. Crear una **segunda cola** de la misma impresora, por ejemplo
   `HP LaserJet 1020 (Cheques)`, sobre el mismo puerto y el mismo driver.
2. En sus Preferencias de impresion, dejar guardado el tamanio "Cheque" y
   orientacion vertical. La otra cola se queda en Carta para todo lo demas.
3. Arrancar Chrome con `--disable-print-preview`, de modo que el boton Imprimir
   lleve directo al dialogo del sistema. Ahi no hay nada que elegir: el tamanio
   y la orientacion los pone el driver.

**No usar `--kiosk-printing`:** imprime por el camino interno de Chrome, que es
justo el que falla.

## Donde queda el boton

- Ficha del cheque propio (`l10n_latam.check`): boton **Imprimir cheque**.
- Formulario del pago: boton **Imprimir cheque**, para los cheques de ese pago.

## Dependencias

- `l10n_latam_check` (Odoo 19 Community)
- Python: `num2words`, ya presente en el entorno, usado para el monto en letras
  en español.

## Limites conocidos

- El monto en letras se corta en tres líneas como maximo; el ancho util se estima
  a partir del tamaño de letra, así que conviene verificarlo al calibrar.
- El addon no numera cheques: el número lo sigue asignando `l10n_latam_check`.
- La posición del cruzado viene con un valor por defecto en la esquina superior
  izquierda; hay que confirmarla en la primera prueba a contraluz.
- El boton **Imprimir** depende de que el navegador acepte imprimir un PDF
  cargado en un marco. Chrome y Edge lo aceptan; si alguno lo bloquea, la
  página deja el boton a la vista para hacerlo a mano.
- No imprime el talon ni la cartola; solo los campos del cheque.
