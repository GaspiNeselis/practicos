"""
Ejercicio 6 - Arreglos de 5 dimensiones representados sobre ARREGLOS LINEALES.

    INSCRIPTOS -> cuantos alumnos hay en cada aula en cada bloque horario
    CAPACIDAD  -> cuantos entran en cada aula

Las dos estructuras son de 5 dimensiones:

    d0: edificio        (4 edificios)
    d1: piso            (5 pisos por edificio)
    d2: ala             (2: norte o sur)
    d3: aula            (25 aulas por ala)
    d4: bloque horario  (85 = 17 bloques por 5 dias)

Pero la memoria es UNA TIRA. Asi que las dos se guardan en un arreglo de
una sola dimension de 4*5*2*25*85 = 85.000 celdas, y se usa la funcion de
direccionamiento h para traducir coordenadas -> posicion en la tira:

    h(i0,...,ik-1) = SUMA sobre j de [ i_j * PRODUCTO de n_w para w = j+1..k-1 ]

O sea: cada coordenada se multiplica por su "salto", que es el producto de
todas las dimensiones que vienen DESPUES de ella.

    salto(edificio) = 5*2*25*85 = 21250
    salto(piso)     =   2*25*85 =  4250
    salto(ala)      =     25*85 =  2125
    salto(aula)     =        85 =    85
    salto(bloque)   =                 1

IMPORTANTE (lo que pide el Tip de la consigna): los algoritmos NO recorren
con indices anidados por dimension. Recorren directamente los indices del
arreglo lineal que corresponden, avanzando de a saltos.
"""

import random

NOMBRES = ["edificio", "piso", "ala", "aula", "bloque"]
ALAS = ["norte", "sur"]


class ArregloKD:
    """Arreglo de k dimensiones representado sobre un arreglo lineal."""

    def __init__(self, dims, valor_inicial=0):
        self.dims = list(dims)
        self.k = len(dims)

        # saltos[j] = producto de las dimensiones que vienen DESPUES de j
        self.saltos = []
        for j in range(self.k):
            prod = 1
            for w in range(j + 1, self.k):
                prod *= self.dims[w]
            self.saltos.append(prod)

        self.total = self.saltos[0] * self.dims[0]
        self.arr = [valor_inicial] * self.total      # la tira lineal

    # ---------- funcion de direccionamiento ----------

    def h(self, coords):
        """Coordenadas -> posicion en el arreglo lineal."""
        return sum(coords[j] * self.saltos[j] for j in range(self.k))

    def h_inv(self, m):
        """Posicion en el arreglo lineal -> coordenadas.
        Es la misma idea que dar el vuelto: cuantos billetes de cada salto
        entran en m."""
        coords = []
        resto = m
        for j in range(self.k):
            coords.append(resto // self.saltos[j])
            resto = resto % self.saltos[j]
        return coords

    # ---------- acceso ----------

    def get(self, coords):
        return self.arr[self.h(coords)]

    def set(self, coords, valor):
        self.arr[self.h(coords)] = valor

    # ---------- recorrido sobre el arreglo lineal ----------

    def direcciones(self, fijos):
        """Genera las posiciones del ARREGLO LINEAL en las que las
        coordenadas indicadas en 'fijos' valen lo pedido y las demas
        recorren todo su rango.

        fijos es un dict {dimension: valor}, por ejemplo {1: 3, 4: 40}
        significa "piso 3, bloque 40, todo lo demas libre".

        No arma coordenadas ni llama a h en cada paso: arranca de una
        direccion base y va SUMANDO Y RESTANDO SALTOS. Por eso recorre
        exactamente las celdas que hacen falta, sobre la tira.
        """
        base = sum(v * self.saltos[j] for j, v in fijos.items())
        libres = [j for j in range(self.k) if j not in fijos]

        if not libres:
            yield base
            return

        contador = [0] * len(libres)
        m = base
        while True:
            yield m

            # avanzo como un cuentakilometros, desde la dim libre mas a la derecha
            p = len(libres) - 1
            while p >= 0:
                j = libres[p]
                contador[p] += 1
                m += self.saltos[j]                  # avanzo un salto
                if contador[p] < self.dims[j]:
                    break
                m -= self.dims[j] * self.saltos[j]   # me pase: vuelvo al inicio
                contador[p] = 0
                p -= 1
            if p < 0:
                return


# ====================================================================
#  CREACION Y CARGA DE LAS ESTRUCTURAS
# ====================================================================

def crear_estructuras(dims, semilla=42):
    """Crea INSCRIPTOS y CAPACIDAD y les carga datos generados.

    La consigna aclara que no se provee archivo de datos, asi que se
    generan. Se usa semilla fija para que el resultado sea reproducible.

    CAPACIDAD es de las mismas dimensiones, pero el valor depende solo
    del aula: la capacidad de un aula no cambia segun el bloque horario.
    INSCRIPTOS nunca supera la capacidad del aula.
    """
    rnd = random.Random(semilla)

    INSCRIPTOS = ArregloKD(dims)
    CAPACIDAD = ArregloKD(dims)

    n_edif, n_piso, n_ala, n_aula, n_bloque = dims

    for e in range(n_edif):
        for p in range(n_piso):
            for a in range(n_ala):
                for au in range(n_aula):
                    cap = rnd.choice([20, 25, 30, 35, 40, 50, 60, 80, 100, 120])

                    # base lineal del aula: desde aca los 85 bloques son
                    # consecutivos, porque el bloque tiene salto 1
                    base = (e * INSCRIPTOS.saltos[0] + p * INSCRIPTOS.saltos[1] +
                            a * INSCRIPTOS.saltos[2] + au * INSCRIPTOS.saltos[3])

                    for b in range(n_bloque):
                        CAPACIDAD.arr[base + b] = cap
                        # bastantes aulas vacias: no todas tienen clase siempre
                        if rnd.random() < 0.45:
                            INSCRIPTOS.arr[base + b] = 0
                        else:
                            INSCRIPTOS.arr[base + b] = rnd.randint(1, cap)

    return INSCRIPTOS, CAPACIDAD


def describir(coords):
    e, p, a, au, b = coords
    dia = b // 17
    franja = b % 17
    return (f"edificio {e}, piso {p}, ala {ALAS[a]}, aula {au}, "
            f"bloque {b} (dia {dia}, franja {franja})")


# ====================================================================
#  a) AULA/BLOQUE HORARIO CON MAYOR PORCENTAJE DE OCUPACION
# ====================================================================

def punto_a(INSCRIPTOS, CAPACIDAD):
    """Recorre el arreglo lineal de punta a punta UNA sola vez.
    No necesita coordenadas para nada: cada celda de INSCRIPTOS se
    compara contra la misma celda de CAPACIDAD.

    Devuelve (posicion, ocupacion, cuantos_empatan).
    """
    mejor_oc = -1.0
    mejor_m = -1
    empatan = 0

    for m in range(INSCRIPTOS.total):
        cap = CAPACIDAD.arr[m]
        if cap > 0:
            oc = INSCRIPTOS.arr[m] / cap
            if oc > mejor_oc:
                mejor_oc = oc
                mejor_m = m
                empatan = 1
            elif oc == mejor_oc:
                empatan += 1

    return mejor_m, mejor_oc, empatan


# ====================================================================
#  b) PROMEDIO DE ALUMNOS POR PISO EN UN BLOQUE HORARIO
# ====================================================================

def punto_b(INSCRIPTOS, bloque):
    """Un promedio por piso (5 en total), entre todos los edificios.

    Para cada piso, recorre las posiciones del arreglo lineal donde
    la coordenada 'piso' vale p y la coordenada 'bloque' vale el pedido.
    Las demas (edificio, ala, aula) quedan libres: son 4*2*25 = 200 aulas.
    """
    promedios = []

    for p in range(INSCRIPTOS.dims[1]):
        suma = 0
        cant = 0
        for m in INSCRIPTOS.direcciones({1: p, 4: bloque}):
            suma += INSCRIPTOS.arr[m]
            cant += 1
        promedios.append((p, suma, cant, suma / cant if cant else 0.0))

    return promedios


# ====================================================================
#  c) TOTAL DE ALUMNOS POR ALA, DADO EDIFICIO / PISO / BLOQUE
# ====================================================================

def punto_c(INSCRIPTOS, edificio, piso, bloque):
    """Para cada ala devuelve cuantos alumnos hay en total.

    Con edificio, piso, ala y bloque fijos, la unica coordenada libre es
    el aula, cuyo salto es 85. Asi que son 25 posiciones del arreglo
    lineal separadas de a 85: un recorrido de a saltos, nada mas.
    """
    totales = []

    for a in range(INSCRIPTOS.dims[2]):
        suma = 0
        cant = 0
        for m in INSCRIPTOS.direcciones({0: edificio, 1: piso, 2: a, 4: bloque}):
            suma += INSCRIPTOS.arr[m]
            cant += 1
        totales.append((a, suma, cant))

    return totales


# ====================================================================
#  VERIFICACION: compara contra recorrido clasico con indices anidados
# ====================================================================

def verificar(INSCRIPTOS, CAPACIDAD, bloque, edificio, piso):
    n_edif, n_piso, n_ala, n_aula, n_bloque = INSCRIPTOS.dims
    ok = True

    # a) fuerza bruta con 5 indices anidados
    mejor_oc = -1.0
    mejor_coords = None
    for e in range(n_edif):
        for p in range(n_piso):
            for a in range(n_ala):
                for au in range(n_aula):
                    for b in range(n_bloque):
                        c = [e, p, a, au, b]
                        cap = CAPACIDAD.get(c)
                        if cap > 0:
                            oc = INSCRIPTOS.get(c) / cap
                            if oc > mejor_oc:
                                mejor_oc = oc
                                mejor_coords = c
    m_lineal, oc_lineal, _ = punto_a(INSCRIPTOS, CAPACIDAD)
    ok &= abs(oc_lineal - mejor_oc) < 1e-12
    print(f"  [{'OK ' if abs(oc_lineal - mejor_oc) < 1e-12 else 'MAL'}] "
          f"punto a: version lineal y version con indices anidados coinciden "
          f"({oc_lineal:.4f} vs {mejor_oc:.4f})")

    # b)
    esperado_b = []
    for p in range(n_piso):
        s = 0
        n = 0
        for e in range(n_edif):
            for a in range(n_ala):
                for au in range(n_aula):
                    s += INSCRIPTOS.get([e, p, a, au, bloque])
                    n += 1
        esperado_b.append((p, s, n))
    obtenido_b = [(p, s, n) for p, s, n, _ in punto_b(INSCRIPTOS, bloque)]
    igual = obtenido_b == esperado_b
    ok &= igual
    print(f"  [{'OK ' if igual else 'MAL'}] punto b: los 5 promedios coinciden "
          f"(200 aulas por piso: {all(n == 200 for _, _, n in obtenido_b)})")

    # c)
    esperado_c = []
    for a in range(n_ala):
        s = 0
        n = 0
        for au in range(n_aula):
            s += INSCRIPTOS.get([edificio, piso, a, au, bloque])
            n += 1
        esperado_c.append((a, s, n))
    obtenido_c = punto_c(INSCRIPTOS, edificio, piso, bloque)
    igual = obtenido_c == esperado_c
    ok &= igual
    print(f"  [{'OK ' if igual else 'MAL'}] punto c: los totales por ala coinciden "
          f"(25 aulas por ala: {all(n == 25 for _, _, n in obtenido_c)})")

    # h / h^-1
    rnd = random.Random(7)
    consistente = True
    for _ in range(5000):
        c = [rnd.randrange(INSCRIPTOS.dims[j]) for j in range(5)]
        if INSCRIPTOS.h_inv(INSCRIPTOS.h(c)) != c:
            consistente = False
            break
    ok &= consistente
    print(f"  [{'OK ' if consistente else 'MAL'}] h y h^-1 son inversas "
          f"(5000 pruebas al azar)")

    return ok


# ====================================================================
#  PROGRAMA PRINCIPAL
# ====================================================================

def ejecutar(bloque=40, edificio=2, piso=3):
    DIMS = [4, 5, 2, 25, 85]

    print("CREACION DE LAS ESTRUCTURAS")
    INSCRIPTOS, CAPACIDAD = crear_estructuras(DIMS)

    print(f"  Vector de dimensiones d = {tuple(DIMS)}")
    for j in range(5):
        print(f"    d{j}: {NOMBRES[j]:<9} {INSCRIPTOS.dims[j]:>3} valores   "
              f"salto = {INSCRIPTOS.saltos[j]:>6}")
    print(f"  Arreglo lineal de {INSCRIPTOS.total} celdas "
          f"(indices 0 .. {INSCRIPTOS.total - 1})")
    print(f"  Se crearon 2 estructuras: INSCRIPTOS y CAPACIDAD")

    print("\n  Ejemplo de la funcion de direccionamiento:")
    c = [2, 3, 1, 7, 40]
    m = INSCRIPTOS.h(c)
    print(f"    h(2,3,1,7,40) = 2*21250 + 3*4250 + 1*2125 + 7*85 + 40 = {m}")
    print(f"    h^-1({m})   = {tuple(INSCRIPTOS.h_inv(m))}   -> vuelve al mismo lugar")
    print(f"    INSCRIPTOS[{m}] = {INSCRIPTOS.arr[m]} alumnos   "
          f"CAPACIDAD[{m}] = {CAPACIDAD.arr[m]} lugares")

    # ---------- a ----------
    print("\n" + "-" * 74)
    print("a) AULA / BLOQUE HORARIO CON MAYOR PORCENTAJE DE OCUPACION")
    print("-" * 74)
    m, oc, empatan = punto_a(INSCRIPTOS, CAPACIDAD)
    coords = INSCRIPTOS.h_inv(m)
    print(f"  Recorrido: una sola pasada por las {INSCRIPTOS.total} celdas del")
    print(f"             arreglo lineal. No hace falta ninguna coordenada.\n")
    print(f"  Posicion lineal ganadora : {m}")
    print(f"  Coordenadas (via h^-1)   : {describir(coords)}")
    print(f"  Inscriptos / Capacidad   : {INSCRIPTOS.arr[m]} / {CAPACIDAD.arr[m]}")
    print(f"  Ocupacion                : {oc * 100:.2f} %")
    if empatan > 1:
        print(f"  (hay {empatan} aula/bloque con esa misma ocupacion maxima; "
              f"se informa el de menor indice lineal)")

    # ---------- b ----------
    print("\n" + "-" * 74)
    print(f"b) PROMEDIO DE ALUMNOS POR PISO EN EL BLOQUE {bloque} "
          f"(dia {bloque // 17}, franja {bloque % 17})")
    print("-" * 74)
    print(f"  Para cada piso se recorren las posiciones del arreglo lineal con")
    print(f"  piso fijo y bloque fijo: 4 edificios x 2 alas x 25 aulas = 200 aulas.\n")
    print(f"  {'Piso':<8}{'Aulas':<9}{'Total alumnos':<17}{'Promedio'}")
    for p, suma, cant, prom in punto_b(INSCRIPTOS, bloque):
        print(f"  {p:<8}{cant:<9}{suma:<17}{prom:.2f}")

    # ---------- c ----------
    print("\n" + "-" * 74)
    print(f"c) ALUMNOS POR ALA EN edificio {edificio}, piso {piso}, bloque {bloque}")
    print("-" * 74)
    print(f"  Con edificio, piso, ala y bloque fijos, la unica coordenada libre")
    print(f"  es el aula (salto 85): son 25 posiciones separadas de a 85.\n")
    print(f"  {'Ala':<10}{'Aulas':<9}{'Total de alumnos presentes'}")
    total_general = 0
    for a, suma, cant in punto_c(INSCRIPTOS, edificio, piso, bloque):
        total_general += suma
        print(f"  {ALAS[a]:<10}{cant:<9}{suma}")
    print(f"  {'':<10}{'':<9}{'-' * 26}")
    print(f"  {'las dos':<10}{50:<9}{total_general}")

    # ---------- verificacion ----------
    print("\n" + "-" * 74)
    print("VERIFICACION")
    print("-" * 74)
    ok = verificar(INSCRIPTOS, CAPACIDAD, bloque, edificio, piso)
    print(f"\n  {'TODO CORRECTO' if ok else 'HAY ALGO MAL'}")

    return INSCRIPTOS, CAPACIDAD


if __name__ == "__main__":
    ejecutar()
