# Proyecto ATD – Comparador de libros y precios
Integrantes:
- Aitana Alberola Camarasa
- María Palacios Requena
- César Martínez Calero
  
Este repositorio contiene el proyecto desarrollado para la asignatura **Análisis y Tratamiento de Datos (ATD)**.  
El objetivo del proyecto es recopilar, relacionar y analizar información sobre libros a partir de **múltiples fuentes de datos**, combinando el uso de APIs y técnicas de web scraping.

---

## Objetivo del proyecto
Desarrollar una aplicación en Python capaz de:
- Obtener información bibliográfica de libros.
- Comparar precios y disponibilidad en tiendas online.
- Incorporar fuentes de libros gratuitos.
- Unificar los datos obtenidos y exportarlos para su posterior análisis.

---

## Fuentes de datos utilizadas
El proyecto trabaja con **cuatro fuentes diferentes**:

1. **Open Library API**  
   - Información básica: título, autor, año de publicación, ISBN.
2. **Google Books API**  
   - Información adicional: categorías, número de páginas, idioma.
3. **Amazon España**  
   - Precios, disponibilidad y valoraciones mediante web scraping.
4. **Project Gutenberg**  
   - Libros gratuitos de dominio público.

---

## Tecnologías empleadas
- Python 3
- Requests
- BeautifulSoup
- APIs REST
- Web Scraping
- CSV para almacenamiento de resultados

---

## Estructura del repositorio
- `main3.py` → Script principal del proyecto.
- `analisis_libros.ipynb` → Notebook de análisis de los datos obtenidos.
- `libros_busquedas.csv` → Información bibliográfica de los libros buscados.
- `precios_detallados.csv` → Precios y disponibilidad en Amazon.
- `libros_gratuitos.csv` → Listado de libros gratuitos.
- `fuentes_datos.csv` → Información sobre las fuentes utilizadas.
- `README.md` → Descripción general del proyecto.

---

## Ejecución del proyecto
1. Asegurarse de tener Python 3 instalado.
2. Instalar las dependencias necesarias:
   ```bash
   pip install requests beautifulsoup4
