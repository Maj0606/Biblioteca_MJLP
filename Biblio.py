from isbnlib import meta, canonical, is_isbn10, is_isbn13
from datetime import date, timedelta

# Listas principales del sistema
libros = []
prestamos = []
historial_prestamos = []

# Configuracion del sistema
DIAS_PRESTAMO = 7
SANCION_POR_DIA = 5.0

# MODULO 1: REGISTRO Y BUSQUEDA DE LIBROS
def registrar_libro():
    print("\n--- REGISTRO DE LIBRO ---")
    isbn = input("Ingrese el ISBN: ").strip()
    if isbn == "":
        print("El ISBN no puede estar vacio.")
        return
    # Verificar que el ISBN no este registrado
    for libro in libros:
        if libro["ISBN"] == isbn:
            print("Este ISBN ya esta registrado.")
            return
    titulo = input("Ingrese el titulo: ").strip()
    autor = input("Ingrese el autor: ").strip()
    if titulo == "" or autor == "":
        print("El titulo y el autor son obligatorios.")
        return
    # Crear el diccionario del libro
    libro = {
        "ISBN": isbn,
        "titulo": titulo,
        "autor": autor,
        "disponible": True
    }
    libros.append(libro)
    print("Libro registrado correctamente.")
def buscar_libro():
    print("\n--- BUSCAR LIBRO ---")
    print("1. Buscar por ISBN")
    print("2. Buscar por autor")
    opcion = input("Seleccione una opcion: ")
    if opcion == "1":
        isbn_ingresado = input("Ingrese el ISBN: ").strip()
        # Limpiar el ISBN para facilitar su validacion
        isbn = canonical(isbn_ingresado)
        # Validar que sea un ISBN correcto
        if not (is_isbn10(isbn) or is_isbn13(isbn)):
            print("El ISBN ingresado no es valido.")
            return
        # Buscar primero en los libros registrados localmente
        for libro in libros:
            if canonical(libro["ISBN"]) == isbn:
                print("\nLibro encontrado en la biblioteca:")
                mostrar_libro(libro)
                return
        # Consultar informacion externa con isbnlib
        print("\nConsultando informacion del libro...")
        try:
            datos = meta(isbn)
            if not datos:
                print("No se encontro informacion para ese ISBN.")
                return
            print("\n--- INFORMACION DEL LIBRO ---")
            print("ISBN:", isbn)
            print("Titulo:", datos.get("Title", "No disponible"))
            autores = datos.get("Authors", [])
            if isinstance(autores, list):
                autores = ", ".join(autores)
            print("Autor(es):", autores or "No disponible")
            print("Editorial:", datos.get("Publisher", "No disponible"))
            print("Anio:", datos.get("Year", "No disponible"))
            print("\nEste libro aun no esta registrado")
            print("en la biblioteca local.")
        except Exception as error:
            print("No se pudo consultar el servicio externo.")
            print("Verifica tu conexion a Internet.")
            print("Detalle:", error)
    elif opcion == "2":
        autor = input("Ingrese el nombre del autor: ").strip().lower()
        encontrado = False
        for libro in libros:
            if autor in libro["autor"].lower():
                mostrar_libro(libro)
                encontrado = True
        if not encontrado:
            print("No se encontraron libros de ese autor.")
    else:
        print("Opcion no valida.")
def mostrar_libro(libro):
    print("\nISBN:", libro["ISBN"])
    print("Titulo:", libro["titulo"])
    print("Autor:", libro["autor"])

    if libro["disponible"]:
        print("Estado: Disponible")
    else:
        print("Estado: Prestado")
def listar_libros():
    print("\n--- LISTA DE LIBROS ---")
    if len(libros) == 0:
        print("No hay libros registrados.")
        return
    for libro in libros:
        mostrar_libro(libro)

# MODULO 2: PRESTAMOS Y DEVOLUCIONES
def realizar_prestamo():
    print("\n--- PRESTAMO DE LIBRO ---")
    isbn = input("Ingrese el ISBN del libro: ").strip()
    # Buscar el libro
    for libro in libros:
        if libro["ISBN"] == isbn:
            if not libro["disponible"]:
                print("El libro ya esta prestado.")
                return
            usuario = input("Nombre de quien solicita el libro: ").strip()
            if usuario == "":
                print("El nombre es obligatorio.")
                return
            # Calcular las fechas
            fecha_prestamo = date.today()
            fecha_limite = fecha_prestamo + timedelta(
                days=DIAS_PRESTAMO
            )
            prestamo = {
                "ISBN": isbn,
                "usuario": usuario,
                "fecha_prestamo": fecha_prestamo,
                "fecha_limite": fecha_limite
            }
            prestamos.append(prestamo)
            libro["disponible"] = False
            print("Prestamo registrado correctamente.")
            print("Fecha de prestamo:", fecha_prestamo)
            print("Fecha limite de devolucion:", fecha_limite)
            return
    print("No se encontro un libro con ese ISBN.")

def devolver_libro():
    print("\n--- DEVOLUCION DE LIBRO ---")
    isbn = input("Ingrese el ISBN del libro: ").strip()
    # Buscar el prestamo activo
    for prestamo in prestamos:
        if prestamo["ISBN"] == isbn:
            fecha_devolucion = date.today()
            fecha_limite = prestamo["fecha_limite"]
            # Calcular los dias de retraso
            retraso = (fecha_devolucion - fecha_limite).days
            if retraso < 0:
                retraso = 0
            # Calcular la sancion
            sancion = retraso * SANCION_POR_DIA
            # Guardar los datos del prestamo finalizado
            prestamo["fecha_devolucion"] = fecha_devolucion
            prestamo["dias_retraso"] = retraso
            prestamo["sancion"] = sancion
            historial_prestamos.append(prestamo.copy())
            prestamos.remove(prestamo)
            # Volver a dejar disponible el libro
            for libro in libros:
                if libro["ISBN"] == isbn:
                    libro["disponible"] = True
                    break
            print("Devolucion registrada correctamente.")
            print("Fecha de devolucion:", fecha_devolucion)
            # Mostrar el resultado de la sancion
            calcular_sancion(retraso, sancion)
            return
    print("No existe un prestamo activo para ese ISBN.")

# MODULO 3: SANCIONES POR ENTREGA TARDIA
def calcular_sancion(retraso, sancion):
    print("\n--- RESULTADO DE LA DEVOLUCION ---")
    if retraso == 0:
        print("El libro se devolvio a tiempo.")
        print("No hay sanciones.")
    else:
        print("Dias de retraso:", retraso)
        print("Sancion por dia: $", SANCION_POR_DIA)
        print("Total de la sancion: $", round(sancion, 2))
def consultar_prestamos():
    print("\n--- PRESTAMOS ACTIVOS ---")
    if len(prestamos) == 0:
        print("No hay prestamos activos.")
        return
    for prestamo in prestamos:
        print("\nLibro ISBN:", prestamo["ISBN"])
        print("Usuario:", prestamo["usuario"])
        print("Fecha de prestamo:", prestamo["fecha_prestamo"])
        print("Fecha limite:", prestamo["fecha_limite"])
def consultar_historial():
    print("\n--- HISTORIAL DE DEVOLUCIONES ---")
    if len(historial_prestamos) == 0:
        print("Todavia no hay devoluciones registradas.")
        return
    for prestamo in historial_prestamos:
        print("\nISBN:", prestamo["ISBN"])
        print("Usuario:", prestamo["usuario"])
        print("Fecha de devolucion:", prestamo["fecha_devolucion"])
        print("Dias de retraso:", prestamo["dias_retraso"])
        print("Sancion: $", round(prestamo["sancion"], 2))

# MENU PRINCIPAL
def menu():
    while True:
        print("\n========== SISTEMA DE BIBLIOTECA ==========")
        print("1. Registrar libro")
        print("2. Buscar libro por ISBN o autor")
        print("3. Mostrar todos los libros")
        print("4. Registrar prestamo")
        print("5. Registrar devolucion")
        print("6. Consultar prestamos activos")
        print("7. Consultar historial de devoluciones")
        print("8. Salir")
        opcion = input("Seleccione una opcion: ")
        try:
            if opcion == "1":
                registrar_libro()
            elif opcion == "2":
                buscar_libro()
            elif opcion == "3":
                listar_libros()
            elif opcion == "4":
                realizar_prestamo()
            elif opcion == "5":
                devolver_libro()
            elif opcion == "6":
                consultar_prestamos()
            elif opcion == "7":
                consultar_historial()
            elif opcion == "8":
                print("Gracias por utilizar el sistema.")
                break
            else:
                print("Opcion no valida. Intente nuevamente.")
        except (ValueError, KeyError) as error:
            print("Ocurrio un error al procesar la operacion:", error)
# Iniciar el programa
if __name__ == "__main__":
    menu()
