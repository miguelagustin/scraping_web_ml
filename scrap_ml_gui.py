from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
import os

root = Tk()
root.title("Interfaz de scrapping ML")
root.geometry("500x250")
root.resizable(0, 0)

#Variables

url_ml = StringVar()
cant_pag = StringVar()
archivo_datos = StringVar()

label_info4 = Label(root,text="Scrapping no iniciado",font=("arial","20"))
label_info4.grid(row=5,column=0,columnspan=2,sticky=N)

#Funciones

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
    pag_web = requests.get(url_ml.get())
    if pag_web.status_code != 200:
        label_info4.config(text="Error en la URL")
        salida_question()
    file = open(archivo_datos.get(),"w")
    file.write("Producto|Precio|Cant_vendidos|Link_producto\n")
    file.close()
    #Scrapping
    for i in range (0,int(cant_pag.get())):
        pag_web = requests.get(url_ml.get())
        soup = BeautifulSoup(pag_web.text,'html.parser')
        file = open(archivo_datos.get(),"a+")
        for parte in soup.find_all('a','item__info-link'):
            titulo_ml = (parte.find('h2','item__title')).find('span','main-title').string
            file.write(titulo_ml + "|")
            precio_ml = (parte.find('div','item__price')).find('span','price__fraction').string
            file.write(precio_ml + "|")
            cant_vendidos = (parte.find('div','item__condition')).string
            file.write(cant_vendidos + "|")
            url_prod = parte.get('href')
            file.write(url_prod + "\n")
        file.close()
        link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
        url_ml.set(link_sig.get('href'))
        print(url_ml.get())
    salida_question()

#Widgets

label_titulo = Label(root,text="Interfaz de scrapping de mercado libre",font=("arial","20"))
label_titulo.grid(row=0,column=0,columnspan=2,sticky=N)

label_info1 = Label(root,text="Ingresa la URL de busqueda:")
label_info1.grid(row=1,column=0)

entry_url_ml = Entry(root,textvariable=url_ml)
entry_url_ml.grid(row=1,column=1)

label_info2 = Label(root,text="Ingresa la cantidad de paginas a buscar")
label_info2.grid(row=2,column=0)

entry_cant_pag = Entry(root,textvariable=cant_pag)
entry_cant_pag.grid(row=2,column=1)

label_info3 = Label(root,text="Ingresa el nombre del archivo donde se guardaran los datos:")
label_info3.grid(row=3,column=0)

entry_archivo = Entry(root,textvariable=archivo_datos)
entry_archivo.grid(row=3,column=1)

boton_scrap = Button(root,text="Comenzar",command=scrap_ml)
boton_scrap.grid(row=4,column=0,columnspan=2)

root.mainloop()