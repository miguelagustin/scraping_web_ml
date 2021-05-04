# Cosas a agregar
# 3) Frontend mas bonito (icono, fuentes, colores)
# 4) Centrado de las ventanas

# Modulos

import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
import requests
import os
import sys
import threading
import csv

# Clase Interfaz scraping
class scraping_ml_gui:
    def __init__(self):
        # Root
        self.root = tkinter.Tk()
        self.root.title("Interfaz de Scraping Web MercadoLibre")
        self.root.geometry("700x250")
        self.root.resizable(0, 0)
        self.root.configure(background="#222222")
        self.root.iconphoto(True, tkinter.PhotoImage(file=os.path.join(os.path.dirname(sys.argv[0]), "static", "icon.png")))

        # Variables de inputs
        self.producto_busqueda = tkinter.StringVar()
        self.cant_paginas = tkinter.StringVar()

        # Otras variables
        self.scraping_process = 0

        # Labels
        self.label_info_scraping = tkinter.Label(self.root,text="Scraping Web no iniciado", font=("Times New Roman", 15))
        self.label_info_scraping.configure(background="#222222", foreground="white")

        self.label_info_productos = tkinter.Label(self.root,text="", font=("Times New Roman", 15))
        self.label_info_productos.configure(background="#222222", foreground="white")

        self.label_titulo = tkinter.Label(self.root,text="Interfaz de scrapping de mercado libre", font=("Times New Roman", 15))
        self.label_titulo.configure(background="#222222", foreground="white")

        self.label_info_ingreso_busqueda = tkinter.Label(self.root,text="Ingresa el producto a buscar: ", font=("Times New Roman", 15))
        self.label_info_ingreso_busqueda.configure(background="#222222", foreground="white")

        self.label_info_cant_paginas = tkinter.Label(self.root,text="Ingresa la cantidad de paginas: ", font=("Times New Roman", 15))
        self.label_info_cant_paginas.configure(background="#222222", foreground="white")

        # Entries
        self.entry_product_ml = tkinter.Entry(self.root,textvariable=self.producto_busqueda, font=("Times New Roman", 15))
        self.entry_product_ml.configure(background="#222222", foreground="white")

        self.entry_cant_paginas = tkinter.Entry(self.root,textvariable=self.cant_paginas, font=("Times New Roman", 15))
        self.entry_cant_paginas.configure(background="#222222", foreground="white")

        # Botones
        self.boton_start_scraping = tkinter.Button(self.root,text="Comenzar",command=self.start_scraping, font=("Times New Roman", 15))
        self.boton_start_scraping.configure(background="#222222", foreground="white")

        # Boton de testing
        self.boton_view_file = tkinter.Button(self.root,text="Ver archivo",command=lambda : self.select_file_output(), font=("Times New Roman", 15))
        self.boton_view_file.configure(background="#222222", foreground="white")

        # Grid
        self.label_titulo.grid(row=0,column=0, columnspan=2, pady=10, padx=100)
        self.label_info_ingreso_busqueda.grid(row=1,column=0, pady=10, padx=50, sticky=tkinter.W)
        self.entry_product_ml.grid(row=1,column=1, pady=10, padx=50, sticky=tkinter.W)
        self.label_info_cant_paginas.grid(row=2,column=0, pady=10, padx=50, sticky=tkinter.W)
        self.entry_cant_paginas.grid(row=2,column=1, pady=10, padx=50, sticky=tkinter.W)
        self.boton_start_scraping.grid(row=3,column=0, sticky=tkinter.S)
        self.boton_view_file.grid(row=3,column=1, sticky=tkinter.S)
        self.label_info_scraping.grid(row=4, column=0, columnspan=2)
        self.label_info_productos.grid(row=5, column=0, columnspan=2)

        # Protocolos
        self.root.protocol("WM_DELETE_WINDOW", self.salida_question)
        # Start
        self.root.mainloop()

    # Salida del programa
    def salida_question(self):
        valor = tkinter.messagebox.askokcancel("Salir", "¿Desea salir de la aplicacion?")
        if(valor):
            self.root.destroy()
            os._exit(0)

    # Seleccionar archivo para observar
    def select_file_output(self):
        filename = askopenfilename(initialdir=os.path.join(os.path.dirname(sys.argv[0]), "output"))
        if filename:
            with open(filename, "rt") as f_csv:
                header = next(f_csv).split("|")
                if len(header) == 6:
                    view_file_ml(self.root, filename)
                else:
                    tkinter.messagebox.showerror("Error al abrir archivo",f"Error al abrir el archivo:\n{filename}.\nNo coincide la cabezera con las armadas por el proceso")

    # Informacion scraping completado
    def scraping_completed(self, filename):
        valor = tkinter.messagebox.askokcancel("Ver productos", "¿Desea abrir el visualizador de productos scrapeados?")
        if(valor):
            view_file_ml(self.root, filename)

    # Scraping a ml
    def scraping_ml(self, url, scraping_product, pages, filename):
        count_products = 0
        self.scraping_process += 1
        self.boton_view_file["state"] = "disabled"
        # Header
        file = open(filename, "w", encoding="utf-8-sig")
        file.write("producto|precio|url_producto|reviews|estado|cantidad_vendidos\n")
        file.close()
        for i in range (0, int(pages)):
            try:
                pag_web = requests.get(url)
            except requests.RequestException as e:
                self.label_info_scraping.config(text="Error en la URL")
                tkinter.messagebox.showerror("ERROR", f"Error al intentar buscar la siguiente pagina({i}), la pagina no responde a la peticion")
                self.salida_question()
                print("Error al realizar la peticion de la pagina, posiblemente esta caida o no exista " + e)
                error_code = 1
                self.boton_view_file["state"] = "normal"
                self.scraping_process -= 1
                return 1
            soup = BeautifulSoup(pag_web.text,'html.parser')
            titulo_url = soup.title.string
            self.label_info_scraping.config(text=titulo_url + " | Pagina " + str(i+1))
            file = open(filename, "a+", encoding="utf-8-sig")
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
                    file.write("0")
                # Fin de registro
                file.write("\n")
                count_products += 1
                self.label_info_productos.config(text=f"Cantidad de productos: {count_products}")
            file.close()
            try:
                link_sig = (soup.find('li','andes-pagination__button andes-pagination__button--next')).find('a','andes-pagination__link')
            except Exception as e:
                print("Error al encontrar el siguiente link. " + str(e))
                self.label_info_scraping.config(text="Fin de busqueda")
                tkinter.messagebox.showerror("Error url",f"Error al intentar buscar la siguiente pagina ({i}), se acabaron las busquedas")
                error_code = 1
                self.boton_view_file["state"] = "normal"
                self.scraping_process -= 1
                return 1
            url = link_sig.get('href')
        error_code = 0
        self.boton_view_file["state"] = "normal"
        self.scraping_process -= 1
        self.end_scraping(error_code, scraping_product, filename)
        return 0

    def start_scraping(self):
        # Scraping a MercadoLibre
        url = "https://listado.mercadolibre.com.ar/"
        self.label_info_scraping.config(text="Ejecutando Scraping web en MercadoLibre")
        if self.producto_busqueda.get() == "":
            self.label_info_scraping.config(text="Error en el producto a buscar")
            tkinter.messagebox.showerror("Error campo producto", "La cantidad de paginas ingresada no es un numero")
            return 1
        url += self.producto_busqueda.get().strip().replace(" ", "-") + "_DisplayType_G"
        if self.cant_paginas.get() == "":
            self.cant_paginas.set(1)
        try:
            pag = int(self.cant_paginas.get())
        except BaseException as err:
            tkinter.messagebox.showerror("Error paginas", "El parametro ingresado no es un numero")
            return 1
        t1 = threading.Thread(target=self.scraping_ml, args=(url, self.producto_busqueda.get(), int(self.cant_paginas.get()), os.path.join(os.path.dirname(sys.argv[0]), "output", "busqueda_" + self.producto_busqueda.get().strip().replace(" ", "-") + "_ml.csv")))
        t1.start()
        return 0

    def end_scraping(self, error_code, scraping_product, filename):
        if error_code == 0:
            self.label_info_scraping.config(text=f"Fin de busqueda exitosa para {self.producto_busqueda.get()}")
            tkinter.messagebox.showinfo("Scraping completado", f"El scraping del producto {scraping_product} se ha completado.")
            self.scraping_completed(filename)
        else:
            self.label_info_scraping.config(text=f"Error en la busqueda para {self.producto_busqueda.get()}")
        return 0

# Clase vista archivo
class view_file_ml:
    def __init__(self, master, filename):
        # Variables
        self.columns = ("Producto", "Precio", "Url_Producto", "Reviews", "Estado", "Cantidad_Vendidos")
        self.filename = filename
        # Root
        #self.root = tkinter.Tk()
        self.root = tkinter.Toplevel(master)
        # Estilos
        self.style_lista_productos = ttk.Style()
        # Treeview
        self.lista_productos = ttk.Treeview(self.root, columns=self.columns, show="headings")
        # Carga configuracion
        self.config_root()
        self.load_treeview()
        self.load_styles()
        self.load_scroll_bars()
        self.load_binds()
        # Ejecucion
        self.root.mainloop()

    # Salida del programa
    def salida_question(self):
        valor = tkinter.messagebox.askokcancel("Salir", "¿Desea salir del view?")
        if(valor):
            self.root.destroy()

    def config_root(self):
        self.root.title("Lista de productos")
        self.root.configure(background="#222222")
        self.root.geometry("1220x600")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
    
    def load_treeview(self):
        self.lista_productos.grid(row=0, column=0, sticky='nsew')
        for col in self.columns:    
            self.lista_productos.heading(col, text=col)
            self.lista_productos.column(col, minwidth=100, stretch=1, anchor=tkinter.W)
        with open(self.filename, "rt") as f_csv:
            csv_reader = csv.reader(f_csv, delimiter="|")
            next(csv_reader)
            for row in csv_reader:
                self.lista_productos.insert("","end",values=tuple(row))

    def load_styles(self):
        self.style_lista_productos.configure("Frame", foreground="#FFFFFF",background="#222222")
        self.style_lista_productos.configure("Treeview", foreground="#FFFFFF",background="#222222")
        self.style_lista_productos.configure("Treeview.Heading")

    # Binds
    def load_binds(self):
        self.lista_productos.bind('<ButtonRelease-1>', self.tree_click_function)

    # ScrollBar
    def load_scroll_bars(self):
        self.scroll_bar_ver = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL, command=self.lista_productos.yview, width=20)
        self.scroll_bar_ver.grid(row=0, column=1, sticky='ns')
        self.lista_productos.config(yscrollcommand=self.scroll_bar_ver.set)
        self.scroll_bar_hor = tkinter.Scrollbar(self.root, orient=tkinter.HORIZONTAL, command=self.lista_productos.xview, width=20)
        self.scroll_bar_hor.grid(row=1, column=0, sticky='we')
        self.lista_productos.config(xscrollcommand=self.scroll_bar_hor.set)

    # Funciones
    def tree_click_function(self, event):
        current_item = self.lista_productos.item(self.lista_productos.focus())
        column = self.lista_productos.identify_column(event.x)
        self.root.clipboard_clear()
        copied_element = current_item['values'][int(column.replace("#", "")) - 1]
        self.root.clipboard_append(copied_element)
        self.root.title(f"Lista de productos | Elemento copiado: {copied_element}")

if __name__ == "__main__":
    scraping_ml_gui()
