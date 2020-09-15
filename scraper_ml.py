# Modulos
from bs4 import BeautifulSoup
import requests
import sys

# Url mercado libre 

#url = 'https://computacion.mercadolibre.com.ar/componentes-pc/placas-de-video/pci-express-30/nvidia/_ItemTypeID_N'
url = 'https://computacion.mercadolibre.com.ar/discos-rigidos-removibles-internos/_DisplayType_G_ItemTypeID_N'

# Cabezera

file = open("output.csv","w")
file.write("Producto|Precio|Link_producto\n")
file.close()

# Scraping

for i in range (0,5):
	try:
		pag_web = requests.get(url)
	except requests.RequestException as e:
		print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
		sys.exit(1)
	soup = BeautifulSoup(pag_web.text,'html.parser')
	titulo_url = soup.title.string
	print (titulo_url + " Pagina " + str(i+1))
	file = open("output.csv","a+")
	for i, content in enumerate(soup.find_all('div','ui-search-result__content-wrapper')):
		#print(content)
		titulo_ml = content.find('h2','ui-search-item__title ui-search-item__group__element').string
		#print(titulo_ml)
		file.write(titulo_ml + "|")
		precio_ml = content.find('span','price-tag-fraction').string
		#print(precio_ml)
		file.write(precio_ml + "|")
		url_soup = soup.find_all("div","ui-search-result__image")[i]
		url_prod = url_soup.find("a").get("href")
		#print(url_prod)
		file.write(url_prod + "\n")
	file.close()
	try:
		link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
	except Exception as e:
		print("Error al encontrar el siguiente link. " + str(e))
		print("Se acabaron las busquedas")
		sys.exit(1)
	url = link_sig.get('href')
	print(url)