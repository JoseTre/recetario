import os
from PIL import Image

def procesar_recetas():
    # 1. Definir rutas de carpetas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fichas_dir = os.path.join(base_dir, "Fichas_Prueba")
    salida_dir = os.path.join(base_dir, "Resultado_Prueba")
    
    # Crear carpeta de resultados si no existe
    if not os.path.exists(salida_dir):
        os.makedirs(salida_dir)

    # 2. Cargar las piezas fijas del encabezado
    ruta_foto_vita = os.path.join(base_dir, "recetadeviola.jpg")
    ruta_banner = os.path.join(base_dir, "banner_titulo.png")

    if not os.path.exists(ruta_foto_vita) or not os.path.exists(ruta_banner):
        print("❌ Error: No se encontró 'recetadeviola.jpg' o 'banner_titulo.png' en Automatizacion_Recetas.")
        return

    img_vita = Image.open(ruta_foto_vita)
    img_banner = Image.open(ruta_banner)

    # 3. Forzar que el banner tenga la misma altura que la foto de Vita
    alto_encabezado = img_vita.height
    ancho_banner_ajustado = int(img_banner.width * (alto_encabezado / img_banner.height))
    img_banner = img_banner.resize((ancho_banner_ajustado, alto_encabezado), Image.Resampling.LANCZOS)

    # 4. Crear el bloque del Encabezado (Foto + Banner)
    ancho_encabezado = img_vita.width + img_banner.width
    encabezado = Image.new("RGB", (ancho_encabezado, alto_encabezado), (255, 255, 255))
    encabezado.paste(img_vita, (0, 0))
    encabezado.paste(img_banner, (img_vita.width, 0))

    # 5. Procesar cada ficha manuscrita
    archivos = [f for f in os.listdir(fichas_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not archivos:
        print("⚠️ No hay imágenes dentro de la carpeta 'Fichas_Prueba'.")
        return

    for archivo in archivos:
        ruta_ficha = os.path.join(fichas_dir, archivo)
        ficha = Image.open(ruta_ficha)

        # Ancho total del lienzo será el mayor entre el encabezado y la ficha
        ancho_final = max(encabezado.width, ficha.width)
        alto_final = encabezado.height + ficha.height

        # Crear lienzo blanco final
        lienzo = Image.new("RGB", (ancho_final, alto_final), (255, 255, 255))

        # Centrar el encabezado en la parte superior
        pos_x_encabezado = (ancho_final - encabezado.width) // 2
        lienzo.paste(encabezado, (pos_x_encabezado, 0))

        # Centrar la ficha manuscrita justo debajo del encabezado
        pos_x_ficha = (ancho_final - ficha.width) // 2
        lienzo.paste(ficha, (pos_x_ficha, encabezado.height))

        # Guardar en la carpeta Resultado_Prueba
        ruta_salida = os.path.join(salida_dir, f"procesada_{archivo}")
        lienzo.save(ruta_salida, quality=95)
        print(f"✅ Procesada: {archivo} ➔ Resultado_Prueba/procesada_{archivo}")

    print("\n🎉 ¡Listo! Todas las fichas de prueba fueron ensambladas con éxito.")

if __name__ == "__main__":
    procesar_recetas()