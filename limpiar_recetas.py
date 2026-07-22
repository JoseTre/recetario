import json
import os

# Nombre del archivo JSON
ARCHIVO_JSON = "recetas_completas_database.json"

def cargar_base_datos():
    if not os.path.exists(ARCHIVO_JSON):
        print(f"\n❌ Error: No se encontró el archivo '{ARCHIVO_JSON}' en este folder.")
        return None
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_base_datos(datos):
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    print(f"\n💾 ¡Archivo '{ARCHIVO_JSON}' guardado y actualizado con éxito!")

def obtener_todos_los_ingredientes(datos):
    ingredientes_set = set()
    for receta_id, info in datos.items():
        # Buscamos en la lista de palabras_clave
        if "palabras_clave" in info and isinstance(info["palabras_clave"], list):
            for ingrediente in info["palabras_clave"]:
                # Limpiamos espacios en blanco alrededor por si acaso
                ingredientes_set.add(ingrediente.strip())
    return sorted(list(ingredientes_set))

def mostrar_ingredientes(datos):
    ingredientes = obtener_todos_los_ingredientes(datos)
    print("\n========================================")
    print(f" LISTA DE INGREDIENTES ÚNICOS ({len(ingredientes)} encontrados):")
    print("========================================")
    for i, ing in enumerate(ingredientes, 1):
        print(f"{i}. {ing}")
    print("========================================\n")

def reemplazar_ingrediente(datos):
    buscar = input("Ingresa el nombre EXACTO del ingrediente que quieres corregir: ").strip()
    
    # Verificar si existe antes de continuar
    ingredientes_actuales = obtener_todos_los_ingredientes(datos)
    if buscar not in ingredientes_actuales:
        print(f"\n⚠️ El ingrediente '{buscar}' no se encontró en la lista. Revisa mayúsculas o espacios.")
        return
        
    reemplazar_por = input(f"Ingresa el NUEVO nombre para reemplazar '{buscar}': ").strip()
    
    if not reemplazar_por:
        print("\n⚠️ Operación cancelada. El nombre nuevo no puede estar vacío.")
        return

    contador_modificados = 0
    
    # Recorrer cada receta para actualizar la lista de palabras clave
    for receta_id, info in datos.items():
        if "palabras_clave" in info and isinstance(info["palabras_clave"], list):
            # Si el ingrediente viejo está en la lista de esta receta
            if buscar in info["palabras_clave"]:
                # Reemplazamos el valor en la lista cuidando el orden
                nueva_lista = []
                for x in info["palabras_clave"]:
                    if x.strip() == buscar:
                        # Si el nuevo nombre ya existía en esa receta, evitamos duplicarlo adentro
                        if reemplazar_por not in nueva_lista:
                            nueva_lista.append(reemplazar_por)
                    else:
                        nueva_lista.append(x.strip())
                
                info["palabras_clave"] = nueva_lista
                contador_modificados += 1

    if contador_modificados > 0:
        print(f"\nSe modificó el ingrediente en {contador_modificados} receta(s).")
        guardar_base_datos(datos)
    else:
        print("\nNo se realizaron cambios.")

def menu_principal():
    while True:
        datos = cargar_base_datos()
        if datos is None:
            break
            
        print("--- MONITOR Y LIMPIADOR DE INGREDIENTES ---")
        print("1. Desplegar lista de ingredientes únicos (sin repetir)")
        print("2. Cambiar nombre de un ingrediente (Singular/Plural/Mayúsculas)")
        print("3. Salir")
        
        opcion = input("Selecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            mostrar_ingredientes(datos)
            input("Presiona Enter para volver al menú...")
        elif opcion == "2":
            reemplazar_ingrediente(datos)
            input("Presiona Enter para volver al menú...")
        elif opcion == "3":
            print("\n¡Hasta luego, José! Éxito con la limpieza de tu base de datos.\n")
            break
        else:
            print("\n⚠️ Opción no válida. Intenta de nuevo.\n")

if __name__ == "__main__":
    menu_principal()
