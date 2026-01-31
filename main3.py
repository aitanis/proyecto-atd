# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 18:48:16 2026

@author: 06ait
"""



import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import csv
import re
import urllib.parse
import random

class LibroComparador:
    def __init__(self):
        self.resultados = []
        self.libros_buscados = []
        # Sesión con cookies para mejor persistencia
        self.session = requests.Session()
        # Lista de User-Agents para rotar
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        
    def _get_random_headers(self):
        """Genera headers aleatorios para evitar detección"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
        
    def buscar_en_openlibrary(self, titulo):
        """
        Fuente 1: Open Library API
        Obtiene información básica del libro (ISBN, autor, año)
        """
        print(f"\n Buscando '{titulo}' en Open Library API...")
        try:
            url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(titulo)}&limit=3"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()  # Lanza excepción si hay error HTTP
            
            data = response.json()
            
            libros = []
            if 'docs' in data and len(data['docs']) > 0:
                for doc in data['docs'][:3]:
                    libro = {
                        'fuente': 'Open Library',
                        'titulo': doc.get('title', 'N/A'),
                        'autor': doc.get('author_name', ['N/A'])[0] if doc.get('author_name') else 'N/A',
                        'año': doc.get('first_publish_year', 'N/A'),
                        'isbn': doc.get('isbn', ['N/A'])[0] if doc.get('isbn') else 'N/A'
                    }
                    libros.append(libro)
                    print(f"  ✓ Encontrado: {libro['titulo']} - {libro['autor']}")
            else:
                print("   No se encontraron resultados en Open Library")
            return libros
        except requests.exceptions.HTTPError as e:
            print(f"  ✗ Error HTTP en Open Library: {e.response.status_code}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error de conexión en Open Library: {e}")
            return []
        except Exception as e:
            print(f"  ✗ Error inesperado en Open Library: {e}")
            return []
    
    def buscar_en_google_books(self, titulo):
        """
        Fuente 2: Google Books API
        Obtiene información adicional (descripción, categorías)
        """
        print(f"\n Buscando '{titulo}' en Google Books API...")
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(titulo)}&maxResults=3"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            libros = []
            if 'items' in data and len(data['items']) > 0:
                for item in data['items'][:3]:
                    info = item.get('volumeInfo', {})
                    libro = {
                        'fuente': 'Google Books',
                        'titulo': info.get('title', 'N/A'),
                        'autor': info.get('authors', ['N/A'])[0] if info.get('authors') else 'N/A',
                        'categoria': info.get('categories', ['N/A'])[0] if info.get('categories') else 'N/A',
                        'paginas': info.get('pageCount', 'N/A'),
                        'idioma': info.get('language', 'N/A')
                    }
                    libros.append(libro)
                    print(f"  ✓ Encontrado: {libro['titulo']} - {libro['autor']}")
            else:
                print("   No se encontraron resultados en Google Books")
            return libros
        except requests.exceptions.HTTPError as e:
            print(f"  ✗ Error HTTP en Google Books: {e.response.status_code}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error de conexión en Google Books: {e}")
            return []
        except Exception as e:
            print(f"  ✗ Error inesperado en Google Books: {e}")
            return []
    
    def buscar_precios_amazon_real(self, titulo):
        """
        Fuente 3: Web scraping mejorado de Amazon España
        Incluye rotación de User-Agent y mejor manejo de errores
        """
        print(f"\n Buscando precios de '{titulo}' en Amazon...")
        
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                # Usar headers aleatorios
                headers = self._get_random_headers()
                
                # Construir URL de búsqueda
                busqueda_encoded = urllib.parse.quote_plus(titulo)
                url = f"https://www.amazon.es/s?k={busqueda_encoded}&__mk_es_ES=%C3%85M%C3%85%C5%BD%C3%95%C3%91"
                
                print(f"   Intento {intento + 1}/{max_intentos}")
                print(f"   URL: {url[:80]}...")
                
                # Delay aleatorio para parecer más humano
                if intento > 0:
                    delay = random.uniform(3, 7)
                    print(f"   Esperando {delay:.1f} segundos...")
                    time.sleep(delay)
                
                # Realizar petición con timeout más largo
                response = self.session.get(url, headers=headers, timeout=20)
                
                # Verificar código de estado
                if response.status_code == 503:
                    print(f"  ⚠️ Error 503 (Service Unavailable) - Amazon bloqueó la petición")
                    if intento < max_intentos - 1:
                        print(f"   Reintentando en 5 segundos...")
                        time.sleep(5)
                        continue
                    else:
                        print(f"   Todos los intentos fallaron. Usando datos simulados.")
                        return self._fallback_amazon_simulado(titulo)
                
                if response.status_code != 200:
                    print(f"   Error HTTP {response.status_code}")
                    if intento < max_intentos - 1:
                        continue
                    return self._fallback_amazon_simulado(titulo)
                
                # Parsear HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                libros = []
                
                # Buscar productos con múltiples estrategias
                productos = []
                
                # Estrategia 1: Por data-component-type
                productos = soup.find_all('div', {'data-component-type': 's-search-result'})
                
                # Estrategia 2: Por clases comunes
                if not productos:
                    productos = soup.find_all('div', class_=re.compile(r's-result-item'))
                
                # Estrategia 3: Por estructura de celda
                if not productos:
                    productos = soup.find_all('div', {'data-asin': re.compile(r'.+')})
                
                print(f"   Productos encontrados: {len(productos)}")
                
                for idx, producto in enumerate(productos[:5]):  # Limitar a 5 productos
                    try:
                        # Extraer título con múltiples estrategias
                        titulo_producto = None
                        
                        # Estrategia 1: h2 con clase estándar
                        titulo_elem = producto.find('h2', class_=re.compile(r'a-size.*'))
                        if titulo_elem:
                            titulo_span = titulo_elem.find('span')
                            if titulo_span:
                                titulo_producto = titulo_span.text.strip()
                        
                        # Estrategia 2: span directo
                        if not titulo_producto:
                            titulo_elem = producto.find('span', {'class': 'a-text-normal'})
                            if titulo_elem:
                                titulo_producto = titulo_elem.text.strip()
                        
                        # Estrategia 3: cualquier h2
                        if not titulo_producto:
                            titulo_elem = producto.find('h2')
                            if titulo_elem:
                                titulo_producto = titulo_elem.get_text(strip=True)
                        
                        # Fallback: nombre genérico
                        if not titulo_producto:
                            titulo_producto = f"{titulo} - Producto {idx+1}"
                        
                        # Limitar longitud
                        titulo_producto = titulo_producto[:150]
                        
                        # Extraer precio (múltiples formatos)
                        precio = "No disponible"
                        precio_num = None
                        
                        # Formato 1: Precio completo con whole y fraction
                        precio_span = producto.find('span', {'class': 'a-price-whole'})
                        precio_fraccion = producto.find('span', {'class': 'a-price-fraction'})
                        
                        if precio_span:
                            try:
                                precio_texto = precio_span.text.strip().replace('.', '').replace(',', '.')
                                if precio_fraccion:
                                    precio_texto += precio_fraccion.text.strip()
                                precio_num = float(precio_texto)
                                precio = f"{precio_num:.2f}€"
                            except ValueError:
                                pass
                        
                        # Formato 2: Precio en span a-offscreen
                        if precio == "No disponible":
                            precio_elem = producto.find('span', {'class': 'a-offscreen'})
                            if precio_elem:
                                precio_texto = precio_elem.text.strip()
                                # Extraer número del texto (ej: "15,99 €" -> 15.99)
                                match = re.search(r'(\d+)[,.]?(\d*)', precio_texto)
                                if match:
                                    precio_num_str = f"{match.group(1)}.{match.group(2)}" if match.group(2) else match.group(1)
                                    try:
                                        precio_num = float(precio_num_str)
                                        precio = f"{precio_num:.2f}€"
                                    except ValueError:
                                        precio = precio_texto
                        
                        # Extraer enlace
                        enlace = None
                        enlace_elem = producto.find('a', href=re.compile(r'/dp/|/gp/product/'))
                        if enlace_elem and 'href' in enlace_elem.attrs:
                            href = enlace_elem['href']
                            if href.startswith('http'):
                                enlace = href
                            else:
                                enlace = f"https://www.amazon.es{href}"
                        
                        # Extraer rating
                        rating = "Sin valoraciones"
                        rating_elem = producto.find('span', {'class': 'a-icon-alt'})
                        if rating_elem:
                            rating = rating_elem.text.strip()
                        
                        # Determinar disponibilidad
                        disponibilidad = "Disponible"
                        # Buscar indicadores de stock
                        stock_elem = producto.find('span', string=re.compile(r'(sólo|quedan|stock|agotado|no disponible)', re.I))
                        if stock_elem:
                            disponibilidad = stock_elem.text.strip()
                        
                        libro = {
                            'fuente': 'Amazon',
                            'titulo': titulo_producto,
                            'precio': precio,
                            'disponibilidad': disponibilidad,
                            'rating': rating,
                            'enlace': enlace,
                            'fecha_busqueda': datetime.now().strftime("%H:%M:%S")
                        }
                        
                        libros.append(libro)
                        print(f"  ✓ {libro['titulo'][:60]}... - {libro['precio']}")
                        
                    except Exception as e:
                        print(f"   Error procesando producto {idx}: {str(e)[:80]}")
                        continue
                
                # Si encontramos productos, retornar
                if libros:
                    print(f"   Scraping exitoso: {len(libros)} productos extraídos")
                    return libros
                
                # Si no hay resultados, intentar de nuevo
                if intento < max_intentos - 1:
                    print("   No se encontraron productos. Reintentando...")
                    continue
                else:
                    print("   No se encontraron precios en Amazon.")
                    return self._fallback_amazon_simulado(titulo)
                
            except requests.exceptions.Timeout:
                print(f"   Timeout al conectar con Amazon (intento {intento + 1})")
                if intento < max_intentos - 1:
                    time.sleep(3)
                    continue
                return self._fallback_amazon_simulado(titulo)
            except requests.exceptions.RequestException as e:
                print(f"   Error de conexión (intento {intento + 1}): {str(e)[:80]}")
                if intento < max_intentos - 1:
                    time.sleep(3)
                    continue
                return self._fallback_amazon_simulado(titulo)
            except Exception as e:
                print(f"   Error inesperado (intento {intento + 1}): {str(e)[:80]}")
                if intento < max_intentos - 1:
                    time.sleep(3)
                    continue
                return self._fallback_amazon_simulado(titulo)
        
        # Si llegamos aquí, todos los intentos fallaron
        return self._fallback_amazon_simulado(titulo)
    
    def _fallback_amazon_simulado(self, titulo):
        """Fallback con datos simulados si falla el scraping real"""
        print("   Usando datos simulados como fallback...")
        libros = []
        for i in range(2):
            precio = round(random.uniform(10, 35), 2)
            libro = {
                'fuente': 'Amazon (simulado - fallback)',
                'titulo': f"{titulo} - Edición {i+1}",
                'precio': f"{precio}€",
                'disponibilidad': 'En stock' if random.random() > 0.3 else 'Pocas unidades',
                'rating': f"{random.uniform(3.5, 5.0):.1f}/5.0",
                'enlace': None,
                'fecha_busqueda': datetime.now().strftime("%H:%M:%S")
            }
            libros.append(libro)
            print(f"   Precio simulado: {precio}€")
        return libros
    
    def buscar_en_gutenberg(self):
        """
        Fuente 4: Project Gutenberg (libros gratuitos)
        Obtiene lista de libros populares gratis
        CORRECCIÓN: Uso de 'string' en lugar de 'text' (deprecado)
        """
        print(f"\n Obteniendo libros gratuitos de Project Gutenberg...")
        try:
            url = "https://www.gutenberg.org/browse/scores/top"
            headers = self._get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            libros = []
            # CORRECCIÓN: Usar 'string' en lugar de 'text' (deprecado en BeautifulSoup 4.9+)
            top_section = soup.find('h2', string=re.compile(r'Top\s+100\s+EBooks', re.I))
            
            if top_section:
                list_container = top_section.find_next('ol')
                if list_container:
                    items = list_container.find_all('a', limit=5)
                    for item in items:
                        titulo_libro = item.text.strip()
                        href = item.get('href', '')
                        
                        libro = {
                            'fuente': 'Project Gutenberg',
                            'titulo': titulo_libro,
                            'precio': 'GRATIS',
                            'formato': 'Digital (varios formatos)',
                            'enlace': f"https://www.gutenberg.org{href}" if href else None
                        }
                        libros.append(libro)
                        print(f"  ✓ Libro gratis: {libro['titulo'][:60]}...")
            
            if not libros:
                print("   No se encontraron libros en Gutenberg")
            
            return libros
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error de conexión en Gutenberg: {e}")
            return []
        except Exception as e:
            print(f"  ✗ Error inesperado en Gutenberg: {e}")
            return []
    
    def relacionar_datos(self, titulo_busqueda):
        """
        Relaciona los datos de las diferentes fuentes
        """
        print(f"\n{'='*60}")
        print(f"BUSCANDO: {titulo_busqueda}")
        print(f"{'='*60}")
        
        # Recolectar datos de todas las fuentes con delays más largos
        datos_openlibrary = self.buscar_en_openlibrary(titulo_busqueda)
        time.sleep(5)  # Aumentado de 1 a 2 segundos
        
        datos_google = self.buscar_en_google_books(titulo_busqueda)
        time.sleep(5)  # Aumentado de 1 a 2 segundos
        
        datos_amazon = self.buscar_precios_amazon_real(titulo_busqueda)
        time.sleep(3)  # Aumentado de 1 a 3 segundos para Amazon
        
        # Crear resultado combinado
        resultado = {
            'busqueda': titulo_busqueda,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'open_library': datos_openlibrary,
            'google_books': datos_google,
            'precios': datos_amazon
        }
        
        self.resultados.append(resultado)
        return resultado
    
    def obtener_libros_gratis(self):
        """
        Obtiene libros gratuitos de Gutenberg
        """
        print(f"\n{'='*60}")
        print(f"LIBROS GRATUITOS DISPONIBLES")
        print(f"{'='*60}")
        
        libros_gratis = self.buscar_en_gutenberg()
        return libros_gratis
    
    def generar_informe(self, libros_gratis):
        """
        Genera un informe final y guarda los resultados en varios archivos CSV
        """
        print(f"\n{'='*60}")
        print(f"INFORME DE RESULTADOS")
        print(f"{'='*60}")
        
        # Resumen por pantalla
        for resultado in self.resultados:
            print(f"\n Búsqueda: {resultado['busqueda']}")
            print(f"   Fecha: {resultado['fecha']}")
            print(f"   Resultados Open Library: {len(resultado['open_library'])}")
            print(f"   Resultados Google Books: {len(resultado['google_books'])}")
            print(f"   Precios encontrados: {len(resultado['precios'])}")
            
            # Mostrar precios de Amazon
            if resultado['precios']:
                print("    Precios en Amazon:")
                for precio in resultado['precios'][:3]:
                    fuente = precio.get('fuente', 'Amazon')
                    print(f"     • {precio['titulo'][:40]}... - {precio['precio']} ({precio.get('disponibilidad', 'N/A')})")
        
        # 1. CSV principal de libros buscados
        with open('libros_busquedas.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Busqueda', 'Fecha',
                'Titulo_OpenLibrary', 'Autor', 'Año', 'ISBN',
                'Categoria', 'Paginas', 'Idioma'
            ])
            
            for resultado in self.resultados:
                openlib = resultado['open_library'][0] if resultado['open_library'] else {}
                google = resultado['google_books'][0] if resultado['google_books'] else {}
                
                writer.writerow([
                    resultado['busqueda'],
                    resultado['fecha'],
                    openlib.get('titulo', 'N/A'),
                    openlib.get('autor', 'N/A'),
                    openlib.get('año', 'N/A'),
                    openlib.get('isbn', 'N/A'),
                    google.get('categoria', 'N/A'),
                    google.get('paginas', 'N/A'),
                    google.get('idioma', 'N/A')
                ])
        
        print("\n✓ Guardado: libros_busquedas.csv")
        
        # 2. CSV de precios detallados
        with open('precios_detallados.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Busqueda', 'Tienda', 'Titulo', 'Precio', 'Disponibilidad', 'Rating', 'Enlace', 'Hora_Busqueda'])
            
            for resultado in self.resultados:
                for precio in resultado['precios']:
                    writer.writerow([
                        resultado['busqueda'],
                        precio['fuente'],
                        precio['titulo'],
                        precio['precio'],
                        precio.get('disponibilidad', 'N/A'),
                        precio.get('rating', 'N/A'),
                        precio.get('enlace', 'N/A'),
                        precio.get('fecha_busqueda', 'N/A')
                    ])
        
        print("✓ Guardado: precios_detallados.csv")
        
        # 3. CSV de libros gratuitos
        with open('libros_gratuitos.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Titulo', 'Precio', 'Formato', 'Fuente', 'Enlace'])
            
            for libro in libros_gratis:
                writer.writerow([
                    libro['titulo'],
                    libro['precio'],
                    libro.get('formato', 'N/A'),
                    libro['fuente'],
                    libro.get('enlace', 'N/A')
                ])
        
        print("✓ Guardado: libros_gratuitos.csv")
        
        # 4. CSV de fuentes de datos
        with open('fuentes_datos.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Numero', 'Nombre', 'Tecnica', 'Tipo_Datos', 'Notas'])
            
            fuentes = [
                [1, 'Open Library API', 'API REST', 'Información bibliográfica', 'Datos confiables'],
                [2, 'Google Books API', 'API REST', 'Detalles del libro', 'Datos estructurados'],
                [3, 'Amazon España', 'Web Scraping', 'Precios y disponibilidad', 'Requiere headers de navegador y rotación'],
                [4, 'Project Gutenberg', 'Web Scraping', 'Libros gratuitos', 'Dominio público']
            ]
            
            for fuente in fuentes:
                writer.writerow(fuente)
        
        print("✓ Guardado: fuentes_datos.csv")


def main():
    """
    Función principal del programa
    """
    print("="*60)
    print("COMPARADOR DE PRECIOS DE LIBROS - VERSIÓN MEJORADA")
    print("Web Scraping con BeautifulSoup + Mejoras anti-bloqueo")
    print("="*60)
    
    comparador = LibroComparador()
    
    # Lista de libros para buscar
    libros_a_buscar = [
        "Harry Potter",
        "1984",
        "Don Quijote"
    ]
    
    print("\n Libros a buscar:")
    for libro in libros_a_buscar:
        print(f"  • {libro}")
    
    print("\n Iniciando búsqueda...")
    print(" NOTA: El scraping de Amazon puede tardar debido a delays anti-bloqueo")
    
    # Buscar cada libro en las diferentes fuentes
    for libro in libros_a_buscar:
        comparador.relacionar_datos(libro)
        time.sleep(3)  # Pausa más larga entre búsquedas (de 2 a 3 segundos)
    
    # Obtener libros gratuitos (4ª fuente)
    libros_gratis = comparador.obtener_libros_gratis()
    
    # Generar informe final (CSV)
    comparador.generar_informe(libros_gratis)
    
    print("\n" + "="*60)
    print(" PROCESO COMPLETADO EXITOSAMENTE!")
    print("="*60)
    print("\n Archivos CSV generados:")
    print("   1. libros_busquedas.csv - Información bibliográfica")
    print("   2. precios_detallados.csv - Precios de Amazon")
    print("   3. libros_gratuitos.csv - Libros gratis de Gutenberg")
    print("   4. fuentes_datos.csv - Metadatos de las fuentes")
    print("\n MEJORAS IMPLEMENTADAS:")
    print("   ✓ Rotación de User-Agents")
    print("   ✓ Delays adaptativos entre peticiones")
    print("   ✓ Reintentos automáticos (hasta 3 intentos)")
    print("   ✓ Mejor extracción de títulos de Amazon")
    print("   ✓ Corrección del deprecation warning")
    print("   ✓ Manejo robusto de errores HTTP")
    print("   ✓ Fallback con datos simulados")

if __name__ == "__main__":
    main()