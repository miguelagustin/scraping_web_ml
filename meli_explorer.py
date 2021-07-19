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
from quantulum3 import parser
import pint

ureg = pint.UnitRegistry()

class Query:
	def __init__(self, search_term, entity = None, tracked = False, base_unit= None):
		self.search_term : str = search_term
		self.entity : str = entity
		self.base_unit : str = base_unit
		self.tracked : bool = True if tracked else False
	def __repr__(self):
		return f'Query:{self.search_term}'


class Publicacion:
	id_regex = re.compile(r'[0-9]{6,}')
	def __init__(self, titulo, precio, url, query):
		self.titulo = titulo
		self.precio = float(precio)
		self.url = url
		self.query = query
		self.efficiency = self.get_cost_effectiveness()
		try:
			self.id = self.id_regex.findall(self.url)[0]
		except IndexError:
			self.id = None
	def get_quantities(self):
		return parser.parse(self.titulo)
	def get_cost_effectiveness(self):
		if self.query.entity == None:
			return None
		else:
			quantities = self.get_quantities()
			for quantity in quantities:
				if quantity.unit.entity.name == self.query.entity:
					try:
						base_unit = (quantity.value * ureg.parse_expression(quantity.unit.name.split('-')[0])).to(self.query.base_unit).magnitude
					except pint.errors.UndefinedUnitError:
						return None
					try:
						return self.precio/base_unit
					except ZeroDivisionError:
						return None

	def __str__(self):
		return '{} | {}'.format(self.titulo, self.precio)
	def __repr__(self):
		return '{} | {}'.format(self.titulo, self.precio)
	def __hash__(self):
		return hash(self.id)
	def __eq__(self, other):
		return self.id == other.id

def get_publicaciones(query, count_pages):
	publicaciones = []
	url = "https://listado.mercadolibre.com.ar/"
	url += query.search_term + "_DisplayType_G"
	for _ in range (0, count_pages):
		try:
			pag_web = requests.get(url)
		except requests.RequestException as e:
			print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
			sys.exit(1)
		soup = BeautifulSoup(pag_web.text,'html.parser')
		for parte in soup.find_all('a','ui-search-result__content ui-search-link'):
			titulo_ml = parte.find('h2','ui-search-item__title ui-search-item__group__element').string
			try:
				precio_ml = (parte.find('div','ui-search-price ui-search-price--size-medium ui-search-item__group__element')).find('span','price-tag-fraction').string.replace(".", "")
			except:
				continue
			url_prod = parte.get('href')
			if url_prod.startswith("https://click1"):
				continue
			publicaciones.append(Publicacion(titulo_ml, precio_ml, url_prod, query))
		try:
			link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
		except AttributeError:
			break
		url = link_sig.get('href')
	return publicaciones

def create_database():
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE query
		(search_term varchar(255) PRIMARY KEY,
		tracked INTEGER,
		entity TEXT,
		base_unit TEXT)''')
	conn.commit()
	c.execute('''CREATE TABLE publicaciones
		(id INTEGER PRIMARY KEY,
		titulo varchar(255),
		precio INTEGER,
		url varchar(255),
		search_term varchar(255),
		efficiency NUMERIC,
		FOREIGN KEY(search_term) REFERENCES query(search_term))''')
	conn.commit()
	conn.close()


def save_publicaciones(publicaciones):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	try:
		c.execute("INSERT INTO query VALUES(?,?,?,?)", (publicaciones[0].query.search_term, 1 if publicaciones[0].query.tracked else 0, publicaciones[0].query.entity, publicaciones[0].query.base_unit))
	except sqlite3.IntegrityError:
		pass
	for publicacion in publicaciones:
		c.execute("INSERT or REPLACE INTO publicaciones VALUES(?,?,?,?,?,?)", (publicacion.id, publicacion.titulo, publicacion.precio, publicacion.url, publicacion.query.search_term, publicacion.efficiency))
		conn.commit()
	conn.close()

def load_queries():
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute("SELECT * FROM query")
	queries = [Query(query[0], tracked=query[1], entity=query[2], base_unit=query[3]) for query in c.fetchall()]
	conn.commit()
	conn.close()
	return queries

def load_publicaciones(query):
	conn = sqlite3.connect('publicaciones.db')
	c = conn.cursor()
	c.execute("SELECT * FROM publicaciones WHERE search_term = ?", (query.search_term,))
	publicaciones = c.fetchall()

	publicaciones = [Publicacion(x[1], x[2], x[3], query) for x in publicaciones]
	conn.commit()
	conn.close()
	return publicaciones


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
		c.execute("INSERT INTO query VALUES(?,?)", (query.search_term, 1 if query.tracked else 0, query.entity))
	except sqlite3.IntegrityError:
		pass
	conn.commit()
	conn.close()

def monitor_new_publicaciones(query):
	publicaciones = get_publicaciones(query, 100)
	old_publicaciones = load_publicaciones(query)
	new_publicaciones = set(publicaciones) - set(old_publicaciones)
	save_publicaciones(publicaciones)
	if new_publicaciones:
		pprint(new_publicaciones)
		winsound.PlaySound('notification_sound.wav', winsound.SND_FILENAME)
		

if __name__ == '__main__':
	if not os.path.isfile('publicaciones.db'):
		create_database()
	while True:
		queries_to_watch = load_queries()
		for query in queries_to_watch:
			print(query)
			if query.tracked:
				monitor_new_publicaciones(query)
				sleep(60)
