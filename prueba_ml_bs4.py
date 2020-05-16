#Modulos
from bs4 import BeautifulSoup
import requests
import sys

#Url mercado libre 
#url = 'https://computacion.mercadolibre.com.ar/componentes-pc/placas-de-video/pci-express-30/nvidia/_ItemTypeID_N'
url = 'https://computacion.mercadolibre.com.ar/discos-rigidos-removibles-internos/_DisplayType_G_ItemTypeID_N'

#Cabecera
file = open("placas_video_ml.csv","w")
file.write("Producto|Precio|Link_producto\n")
file.close()

#Scrapping
for i in range (0,5):
	try:
		pag_web = requests.get(url)
	except requests.RequestException as e:
		print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
		sys.exit(1)
	soup = BeautifulSoup(pag_web.text,'html.parser')
	titulo_url = soup.title.string
	print (titulo_url + "Pagina " + str(i+1))
	file = open("placas_video_ml.csv","a+")
	for parte in soup.find_all('a','item__info-link'):
		titulo_ml = (parte.find('h2','item__title')).find('span','main-title').string
		#print(titulo_ml)
		file.write(titulo_ml + "|")
		precio_ml = (parte.find('div','item__price')).find('span','price__fraction').string
		#print(precio_ml)
		file.write(precio_ml + "|")
		url_prod = parte.get('href')
		file.write(url_prod + "\n")
	file.close()
	try:
		link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
	except Exception as e:
		print("Error al encontrar el siguiente link. " + str(e))
		sys.exit(1)
	url = link_sig.get('href')
	print(url)