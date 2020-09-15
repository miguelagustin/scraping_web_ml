# scraper-ml

Hecho por Santiago Menendez

## Descripcion
Programa con interfaz grafica que realiza scraping de paginas web de busquedas y convierte los resultados en .csv para poder analizarlos.
Utiliza tkinter, beautifulsoup y requests para la busqueda.
Tambien se incluyo parte del codigo para correrlo en consola (tanto linux como windows).

## Utilizacion
Se debe iniciar scraper_ml_gui.pyw para abrir el programa.

Una vez abierto se ingresa el link de busqueda, la cantidad de paginas a revisar y el nombre del archivo csv.

En el caso de iniciar scraper_ml.py se debe reemplazar la variable url por el link que desean buscar.

## Problemas al correrlo
- Necesitan tener el modulo requests y bs4 instalado en Python.
	Para poder instalarlo tienen que abrir su consola cmd/shell y escribir: "pip install requests --user" y "pip install bs4 --user"
