# Valsegur Check Printing

Impresion de cheques propios sobre el formulario preimpreso de cada banco.

## Por que este addon y no `account_check_printing`

Valsegur gestiona los cheques con `l10n_latam_check` (metodo de pago `own_checks`,
numero en `l10n_latam_check_number`, fecha de cobro diferida). En Odoo 19 ese modulo
esta desacoplado de `account_check_printing` y su impresion esta deshabilitada a
proposito, porque no existe un formato estandar: Odoo espera un reporte por banco.
`account_check_printing` ademas no trae ninguna plantilla QWeb, y no hay modulo
`l10n_cl_check_printing` ni en Community, ni en Enterprise, ni en el App Store.

Este addon imprime directamente sobre `l10n_latam.check`, sin instalar
`account_check_printing` y sin alterar el flujo de cheques existente.

## Como funciona

El reporte dibuja cada dato en una posicion absoluta en milimetros. Las posiciones
se guardan **en el diario bancario**, de modo que cada banco se calibra desde la
interfaz, sin tocar codigo:

Contabilidad / Configuracion / Diarios / <banco> / pestania **Cheques**

- `Imprimir cheques desde Odoo`: habilita el boton en ese diario.
- Formulario del banco: ancho, alto, tamanio de letra, ciudad, mayusculas,
  fecha en una linea o en casilleros separados.
- Posicion de los campos: coordenadas X/Y de ciudad, fecha, monto en numeros,
  monto en letras y beneficiario.
- Calibracion de la impresora: `ajuste horizontal` y `ajuste vertical` corren
  todos los campos a la vez para corregir la deriva del equipo.

## Calibrar un banco nuevo

1. En el diario, marcar `Imprimir cheques desde Odoo` y cargar ancho y alto reales
   del cheque.
2. Pulsar **Imprimir grilla de calibracion** e imprimirla sobre un cheque anulado
   del banco.
3. Leer en la grilla la coordenada de cada campo y cargarla en el diario.
4. Imprimir un cheque real anulado y ajustar con los dos campos de calibracion.

El formato de papel por defecto es `Cheque Valsegur (180 x 85 mm)`. Si un banco usa
otra medida, duplicar el formato en Ajustes tecnicos y asignarlo al reporte.

## Donde queda el boton

- Ficha del cheque propio (`l10n_latam.check`): boton **Imprimir cheque**.
- Lista de cheques propios: accion de impresion en el menu de acciones.
- Formulario del pago: boton **Imprimir cheque**, para los cheques de ese pago.

## Dependencias

- `l10n_latam_check` (Odoo 19 Community)
- Python: `num2words`, ya presente en el entorno, usado para el monto en letras
  en espaniol.

## Limites conocidos

- El monto en letras se corta en tres lineas como maximo; el ancho util se estima
  a partir del tamanio de letra, asi que conviene verificarlo al calibrar.
- El addon no numera cheques: el numero lo sigue asignando `l10n_latam_check`.
- No imprime el talon ni la cartola; solo los campos del cheque.
