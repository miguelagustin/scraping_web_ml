# scraping_web_ml

Simple script para obtener alertas de nuevas publicaciones en Mercado Libre en base a terminos de busqueda. Utiliza una base de datos sqlite para guardarlas.

Adicionalmente, si el titulo de la publicacion contiene unidades como kilos o gigabytes, se realiza un parsing y se intenta calcular el precio/unidad de la publicacion. Esto es util para comparar publicaciones.

Forkeado de https://github.com/SantiMenendez19/scraping_web_ml

## Dependencias

    pip install pint bs4 quantulum3 requests pprint