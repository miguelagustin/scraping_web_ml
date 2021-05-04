# Modulos
from bs4 import BeautifulSoup
import requests
import sys
import os
import time
import argparse

# Scraping de mercadolibre

# Argumentos

parser = argparse.ArgumentParser()
parser.add_argument("--busqueda", help="Producto a buscar en ML")
parser.add_argument("--paginas", help="Cantidad de paginas a buscar (Default: 1)")

args = parser.parse_args()

if args.busqueda:
	busqueda = args.busqueda.replace(" ", "-")
else:
	print("Error: No se ingreso un producto a buscar")
	sys.exit(1)

if args.paginas:
	if int(args.paginas) < 1:
		print("Error: Las paginas no pueden ser menor a 1")
		sys.exit(1)
	else:
		count_pages = int(args.paginas)
		print(f"Se ingresaron {count_pages} paginas")
else:
	print(f"No se ingreso cantidad de paginas, por defecto sera 1")
	count_pages = 1

# Armado del url mercado libre 
url = "https://listado.mercadolibre.com.ar/"
url += busqueda + "_DisplayType_G"

#Cabecera
file = open(os.path.join("output", "busqueda_" + busqueda + "_ml.csv"),"w", encoding="utf-8-sig")
file.write("producto|precio|url_producto|reviews|estado|cantidad_vendidos\n")
file.close()

print("Url: ", url)

#Scraping
for i in range (0, count_pages):
	try:
		pag_web = requests.get(url)
	except requests.RequestException as e:
		print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
		sys.exit(1)
	soup = BeautifulSoup(pag_web.text,'html.parser')
	titulo_url = soup.title.string
	print (titulo_url + " | Pagina " + str(i+1))
	file = open(os.path.join("output", "busqueda_" + busqueda + "_ml.csv"),"a+", encoding="utf-8-sig")
	for parte in soup.find_all('a','ui-search-result__content ui-search-link'):
		# Titulo
		titulo_ml = parte.find('h2','ui-search-item__title ui-search-item__group__element').string
		file.write(titulo_ml + "|")
		# Precio
		try:
			precio_ml = (parte.find('div','ui-search-price ui-search-price--size-medium ui-search-item__group__element')).find('span','price-tag-fraction').string.replace(".", "")
			file.write(precio_ml + "|")
		except:
			file.write("|")
		# Url
		url_prod = parte.get('href')
		file.write(url_prod + "|")
		# Reviews
		try:
			reviews = parte.find('span','ui-search-reviews__amount').string
			file.write(reviews + "|")
		except:
			file.write("|")
		# Unidades Vendidas / Estado
		soup_prod = BeautifulSoup(requests.get(url_prod).text,'html.parser')
		try:
			subtexto = soup_prod.find("span", "ui-pdp-subtitle").string.split("|")
			estado = subtexto[0].strip()
			if len(subtexto) == 2:
				cant_vendidos = subtexto[1].replace("vendido", "").replace("s", "").strip()
			else:
				cant_vendidos = "0"
			file.write(estado + "|")
			file.write(cant_vendidos)
		except:
			file.write("|")
		# Fin de registro
		file.write("\n")
	file.close()
	try:
		link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
	except Exception as e:
		print("Error al encontrar el siguiente link. " + str(e))
		sys.exit(1)
	url = link_sig.get('href')

print("Fin del proceso")

sys.exit(0)