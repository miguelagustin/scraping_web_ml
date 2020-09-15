# Modulos

from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
import os
import sys

root = Tk()
root.title("Interfaz de scrapping de mercado libre")
root.geometry("500x250")
root.resizable(0, 0)

# Variables

url_ml = StringVar()
cant_pag = StringVar()
archivo_datos = StringVar()

label_info4 = Label(root,text="Scrapping no iniciado",font=("Courier New","20"))
label_info4.grid(row=5,column=0,columnspan=2,rowspan=2,sticky=S,ipady=10)

# Funciones

def salida_question():
    valor = messagebox.askokcancel("Salir", "¿Desea salir de la aplicacion?")
    if(valor):
        root.destroy()
        os._exit(0)

def scrap_ml():
    label_info4.config(text="Ejecutando scrapping")
    url_mod = url_ml.get()
    if(url_mod.find('_DisplayType_G') == -1 ):
        url_ml.set(url_mod +'_DisplayType_G')
    try:
        pag_web = requests.get(url_ml.get())
    except Exception as e:
        label_info4.config(text="Error en la URL")
        messagebox.showerror("ERROR","Error al intentar buscar la siguiente pagina, la pagina no responde a la peticion")
        salida_question()
    if archivo_datos.get() == "":
        archivo_datos.set("archivo.csv")
    file = open(archivo_datos.get(),"w")
    file.write("Producto|Precio|Link_producto\n")
    file.close()
    # Scraping
    if cant_pag.get() == "":
        cant_pag.set(1)
    for i in range (0,int(cant_pag.get())):
        pag_web = requests.get(url_ml.get())
        soup = BeautifulSoup(pag_web.text,'html.parser')
        file = open(archivo_datos.get(),"a+")
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
        if int(cant_pag.get()) > 1:
            try:
                link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
                url_ml.set(link_sig.get('href'))
                print(url_ml.get())
            except Exception as e:
                label_info4.config(text="Fin de busqueda")
                messagebox.showerror("ERROR","Error al intentar buscar la siguiente pagina, se acabaron las busquedas")
                break
    label_info4.config(text="Fin de busqueda exitosa")
    salida_question()
    label_info4.config(text="Scrapping no iniciado")

# Widgets Tkinter

label_titulo = Label(root,text="Interfaz de scrapping de mercado libre",font=("Times","20"))
label_titulo.grid(row=0,column=0,columnspan=2,sticky=N)

label_info1 = Label(root,text="Ingresa la URL de busqueda:\n (no debe estar vacia)")
label_info1.grid(row=1,column=0)

entry_url_ml = Entry(root,textvariable=url_ml,font=("Courier New",10))
entry_url_ml.grid(row=1,column=1,ipadx=50)

label_info2 = Label(root,text="Ingresa la cantidad de paginas a buscar:\n (default 1)")
label_info2.grid(row=2,column=0,sticky=E)

entry_cant_pag = Entry(root,textvariable=cant_pag,font=("Courier New",10))
entry_cant_pag.grid(row=2,column=1,ipadx=50)

label_info3 = Label(root,text="Ingresa el nombre/path del archivo\n donde se guardaran los datos:\n (default archivo.csv)")
label_info3.grid(row=3,column=0)

entry_archivo = Entry(root,textvariable=archivo_datos,font=("Courier New",10))
entry_archivo.grid(row=3,column=1,ipadx=50)

boton_scrap = Button(root,text="Comenzar",command=scrap_ml,font=("Courier New",10),bg="white")
boton_scrap.grid(row=4,column=0,columnspan=4,ipadx=50)

root.mainloop()