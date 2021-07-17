# Modulos
from bs4 import BeautifulSoup
import requests
import sys
import os
from time import sleep
import re
import pickle
import sqlite3
from pprint import pprint
import winsound
class Publicacion:
	id_regex = re.compile(r'[0-9]{6,}')
	def __init__(self, titulo, precio, url, search_term):
		self.titulo = titulo
		self.precio = precio
		self.url = url
		self.search_term = search_term
		try:
			self.id = self.id_regex.findall(self.url)[0]
		except IndexError:
			self.id = None
	def __str__(self):
		return '{} | {}'.format(self.titulo, self.precio)
	def __repr__(self):
		return '{} | {}'.format(self.titulo, self.precio)
	def __hash__(self):
		return hash(self.id)
	def __eq__(self, other):
		return self.id == other.id



def get_publicaciones(busqueda, count_pages):
	publicaciones = []
	url = "https://listado.mercadolibre.com.ar/"
	url += busqueda + "_DisplayType_G"
	for i in range (0, count_pages):
		try:
			pag_web = requests.get(url)
		except requests.RequestException as e:
			print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
			sys.exit(1)
		soup = BeautifulSoup(pag_web.text,'html.parser')
		# titulo_url = soup.title.string
		# print (titulo_url + " | Pagina " + str(i+1))
		for parte in soup.find_all('a','ui-search-result__content ui-search-link'):
			# Titulo
			titulo_ml = parte.find('h2','ui-search-item__title ui-search-item__group__element').string
			# file.write(titulo_ml + "|")
			# Precio
			try:
				precio_ml = (parte.find('div','ui-search-price ui-search-price--size-medium ui-search-item__group__element')).find('span','price-tag-fraction').string.replace(".", "")
				# file.write(precio_ml + "|")
			except:
				continue
			# Url
			url_prod = parte.get('href')
			if url_prod.startswith("https://click1"):
				continue
			publicaciones.append(Publicacion(titulo_ml, precio_ml, url_prod, busqueda))
		try:
			link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
		except AttributeError:
			break
		url = link_sig.get('href')
	return publicaciones

#function to create sqlite database of publicaciones with a foreign key to another table called 'query'
def create_database():
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE query
		(search_term varchar(255) PRIMARY KEY,
		tracked INTEGER)''')
	conn.commit()
	c.execute('''CREATE TABLE publicaciones
		(id INTEGER PRIMARY KEY,
		titulo varchar(255),
		precio INTEGER,
		url varchar(255),
		search_term varchar(255),
		FOREIGN KEY(search_term) REFERENCES query(search_term))''')
	conn.commit()
	conn.close()


#function to save publicaciones to the database
def save_publicaciones(publicaciones):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	try:
		c.execute("INSERT INTO query VALUES(?,?)", (publicaciones[0].search_term, 1))
	except sqlite3.IntegrityError:
		pass
	for publicacion in publicaciones:
		c.execute("INSERT or REPLACE INTO publicaciones VALUES(?,?,?,?,?)", (publicacion.id, publicacion.titulo, publicacion.precio, publicacion.url, publicacion.search_term))
		conn.commit()
	conn.close()


#function to retrieve publicaciones from database with a given query
def load_publicaciones(query):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute("SELECT * FROM publicaciones WHERE search_term = ?", (query,))
	publicaciones = c.fetchall()
	publicaciones = [Publicacion(x[1], x[2], x[3], x[4]) for x in publicaciones]
	conn.commit()
	conn.close()
	return publicaciones

def load_tracked_queries():
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute("SELECT * FROM query WHERE tracked = 1")
	queries = [x[0] for x in c.fetchall()]
	conn.commit()
	conn.close()
	return queries

def change_tracked_status(query, status):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute("UPDATE query SET tracked = ? WHERE search_term = ?", (status, query))
	conn.commit()
	conn.close()

def save_query(query):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	try:
		c.execute("INSERT INTO query VALUES(?,?)", (query, 1))
	except sqlite3.IntegrityError:
		pass
	conn.commit()
	conn.close()


if __name__ == '__main__':
	if not os.path.isfile('publicaciones.db'):
		create_database()
	queries_to_watch = load_tracked_queries()
	while True:
		for query in queries_to_watch:
			publicaciones = get_publicaciones(query, 100)
			old_publicaciones = load_publicaciones(query)
			new_publicaciones = set(publicaciones) - set(old_publicaciones)
			save_publicaciones(publicaciones)
			if new_publicaciones:
				pprint(new_publicaciones)
				winsound.PlaySound('notification_sound.wav', winsound.SND_FILENAME)
			sleep(60)