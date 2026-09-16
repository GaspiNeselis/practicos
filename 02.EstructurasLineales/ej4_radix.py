"""
Ejercicio 4 - Implementar RADIX SORT y ordenar las palabras de los archivos.

La idea: NO se comparan las palabras entre si. Se reparten en cajitas
(una por cada simbolo del alfabeto) mirando UN solo simbolo, se juntan
las cajitas en orden, y se repite con el simbolo siguiente.

Dos reglas que no se pueden romper:
  1) Se arranca por la posicion MENOS significativa (j=1, la de la derecha)
     y se va subiendo hacia la izquierda.
  2) Las cajitas son COLAS (FIFO). Asi, cuando dos palabras empatan en el
     simbolo que se esta mirando, conservan el orden que traian de la
     vuelta anterior. Eso es lo que hace funcionar todo.

Alfabetos por posicion: cada posicion de la palabra puede tener su propio
alfabeto (lo del < S1, S2, S1, S1 > de la filmina). El ORDEN en que estan
escritos los simbolos en el archivo ES el criterio de que va antes que que.

Archivos:
    alfabetos.txt -> un alfabeto por linea, de la posicion MAS significativa
                     a la MENOS significativa
    palabras.txt  -> una palabra por linea, simbolos separados por coma
"""

from collections import deque


def leer_alfabetos(ruta):
    """Cada linea es el alfabeto de una posicion, en orden de la mas
    significativa a la menos significativa."""
    alfabetos = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            alfabetos.append([s.strip() for s in linea.split(",")])
    return alfabetos


def leer_palabras(ruta):
    """Cada linea es una palabra: sus simbolos separados por coma."""
    palabras = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            palabras.append([s.strip() for s in linea.split(",")])
    return palabras


def mostrar(palabra):
    return "".join(f"{s:>3}" for s in palabra)


def radix_sort(palabras, alfabetos, verbose=True):
    p = len(alfabetos)          # cantidad de posiciones de cada palabra
    Q = deque(palabras)         # cola principal

    if verbose:
        print(f"Palabras de {p} posiciones. Alfabetos por posicion:")
        for i, a in enumerate(alfabetos):
            print(f"   posicion {p - i} (indice {i}):  {len(a):>2} simbolos -> {','.join(a)}")
        print()

    # j = 1 es la posicion MENOS significativa (la ultima de la palabra)
    for j in range(1, p + 1):

        idx = p - j                 # traduzco j a indice de lista (j=1 -> ultimo)
        alfabeto = alfabetos[idx]
        r = len(alfabeto)

        # una cajita (cola) por cada simbolo del alfabeto de esta posicion
        cajitas = {simbolo: deque() for simbolo in alfabeto}

        # --- repartir ---
        while Q:
            X = Q.popleft()                 # dequeue de la cola principal
            s = X[idx]                      # simbolo de X en la posicion j
            if s not in cajitas:
                raise ValueError(
                    f"El simbolo '{s}' no pertenece al alfabeto de la posicion {j}")
            cajitas[s].append(X)            # enqueue en la cajita

        if verbose:
            print(f"--- Vuelta j={j}  (posicion {j}, {r} cajitas) ---")
            for simbolo in alfabeto:
                if cajitas[simbolo]:
                    contenido = "  |  ".join(",".join(w) for w in cajitas[simbolo])
                    print(f"   Q[{simbolo:>2}] : {contenido}")

        # --- concatenar: recorro las cajitas EN EL ORDEN DEL ALFABETO ---
        for simbolo in alfabeto:
            while cajitas[simbolo]:
                Q.append(cajitas[simbolo].popleft())

        if verbose:
            print(f"   => Q = " + "  |  ".join(",".join(w) for w in Q))
            print()

    return list(Q)


def esta_ordenada(palabras, alfabetos):
    """Verifica el resultado usando el orden lexicografico que definen
    los alfabetos (posicion mas significativa primero)."""
    rango = [{s: i for i, s in enumerate(a)} for a in alfabetos]

    def clave(w):
        return tuple(rango[i][s] for i, s in enumerate(w))

    return all(clave(palabras[k]) <= clave(palabras[k + 1])
               for k in range(len(palabras) - 1))


def ejecutar(ruta_alfabetos, ruta_palabras, verbose=True):
    alfabetos = leer_alfabetos(ruta_alfabetos)
    palabras = leer_palabras(ruta_palabras)

    if verbose:
        print("ENTRADA (desordenada):")
        for w in palabras:
            print("   " + ",".join(w))
        print()

    ordenadas = radix_sort(palabras, alfabetos, verbose=verbose)

    print("RESULTADO FINAL (ordenado):")
    for w in ordenadas:
        print("   " + ",".join(w))

    ok = esta_ordenada(ordenadas, alfabetos)
    print(f"\n  Verificacion de orden lexicografico: {'OK' if ok else 'FALLO'}")

    return ordenadas


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    ejecutar(os.path.join(base, "datos", "alfabetos.txt"),
             os.path.join(base, "datos", "palabras.txt"))
