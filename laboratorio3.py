# librerias
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


OPERADORES = {"|", ".", "*", "+", "?"}
UNARIOS = {"*", "+", "?"}
PRECEDENCIA = {"|": 1, ".": 2}
ARCHIVO_PREDETERMINADO = Path(__file__).with_name("expresiones.txt")
DIRECTORIO_SALIDA = Path(__file__).with_name("arboles")


@dataclass
class Nodo:
    valor: str
    izquierdo: Nodo | None = None
    derecho: Nodo | None = None

    # Indica si el nodo no tiene hijos.
    @property
    def es_hoja(self) -> bool:
        return self.izquierdo is None and self.derecho is None


# Separa la expresion regular en tokens.
def tokenizar(expresion: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(expresion):
        caracter = expresion[i]
        if caracter.isspace():
            i += 1
        elif caracter == "\\":
            if i + 1 == len(expresion):
                raise ValueError("Escape incompleto al final de la expresion")
            tokens.append(expresion[i : i + 2])
            i += 2
        elif caracter == "[":
            inicio = i
            i += 1
            escapado = False
            while i < len(expresion):
                actual = expresion[i]
                if actual == "]" and not escapado:
                    i += 1
                    tokens.append(expresion[inicio:i])
                    break
                escapado = actual == "\\" and not escapado
                if actual != "\\":
                    escapado = False
                i += 1
            else:
                raise ValueError("Clase de caracteres sin cerrar")
        else:
            tokens.append(caracter)
            i += 1
    if not tokens:
        raise ValueError("La expresion esta vacia")
    return tokens


# Determina si un token es un operando.
def es_operando(token: str) -> bool:
    return token not in OPERADORES and token not in {"(", ")"}


# Agrega el operador de concatenacion explicita.
def agregar_concatenacion(tokens: Iterable[str]) -> list[str]:
    resultado: list[str] = []
    anterior: str | None = None
    for token in tokens:
        termina = anterior is not None and (es_operando(anterior) or anterior == ")" or anterior in UNARIOS)
        comienza = es_operando(token) or token == "("
        if termina and comienza:
            resultado.append(".")
        resultado.append(token)
        anterior = token
    return resultado


# Convierte los tokens de infix a postfix con Shunting Yard.
def infix_a_postfix(tokens: Iterable[str]) -> tuple[list[str], list[tuple[str, str, str]]]:
    salida: list[str] = []
    pila: list[str] = []
    pasos: list[tuple[str, str, str]] = []
    espera_operando = True

    for token in tokens:
        if es_operando(token):
            if not espera_operando:
                raise ValueError(f"Falta un operador antes de '{token}'")
            salida.append(token)
            espera_operando = False
        elif token == "(":
            if not espera_operando:
                raise ValueError("Falta concatenacion antes de '('")
            pila.append(token)
        elif token == ")":
            if espera_operando:
                raise ValueError("Parentesis vacio u operador sin operando")
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if not pila:
                raise ValueError("Parentesis ')' sin apertura")
            pila.pop()
            espera_operando = False
        elif token in UNARIOS:
            if espera_operando:
                raise ValueError(f"El operador '{token}' no tiene operando")
            salida.append(token)
        else:
            if espera_operando:
                raise ValueError(f"El operador '{token}' no tiene operando izquierdo")
            while pila and pila[-1] != "(" and PRECEDENCIA[pila[-1]] >= PRECEDENCIA[token]:
                salida.append(pila.pop())
            pila.append(token)
            espera_operando = True
        pasos.append((token, " ".join(salida) or "∅", " ".join(pila) or "∅"))

    if espera_operando:
        raise ValueError("La expresion termina con un operador")
    while pila:
        operador = pila.pop()
        if operador == "(":
            raise ValueError("Parentesis '(' sin cierre")
        salida.append(operador)
        pasos.append(("FIN", " ".join(salida), " ".join(pila) or "∅"))
    return salida, pasos


# Construye el arbol sintactico a partir de postfix.
def postfix_a_arbol(postfix: Iterable[str]) -> Nodo:
    pila: list[Nodo] = []
    for token in postfix:
        if es_operando(token):
            pila.append(Nodo(token))
        elif token in {"|", "."}:
            if len(pila) < 2:
                raise ValueError(f"Postfix invalido: faltan operandos para '{token}'")
            derecho = pila.pop()
            izquierdo = pila.pop()
            pila.append(Nodo(token, izquierdo, derecho))
        elif token == "*":
            if not pila:
                raise ValueError("Postfix invalido: falta operando para '*'")
            pila.append(Nodo("*", pila.pop()))
        elif token == "+":
            if not pila:
                raise ValueError("Postfix invalido: falta operando para '+'")
            operando = pila.pop()
            pila.append(Nodo(".", operando, Nodo("*", copy.deepcopy(operando))))
        elif token == "?":
            if not pila:
                raise ValueError("Postfix invalido: falta operando para '?'")
            pila.append(Nodo("|", pila.pop(), Nodo("ε")))
    if len(pila) != 1:
        raise ValueError("Postfix invalido: quedaron operandos sin conectar")
    return pila[0]


# Dibuja el arbol sintactico y lo guarda como una imagen.
def dibujar_arbol(raiz: Nodo, destino: Path, mostrar: bool = False) -> None:
    import matplotlib

    if not mostrar:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    posiciones: dict[int, tuple[float, float]] = {}
    contador_hojas = 0

    # Calcula la posicion de cada nodo en la imagen.
    def ubicar(nodo: Nodo, profundidad: int = 0) -> float:
        nonlocal contador_hojas
        hijos = [h for h in (nodo.izquierdo, nodo.derecho) if h is not None]
        if not hijos:
            x = float(contador_hojas)
            contador_hojas += 1
        else:
            x_hijos = [ubicar(hijo, profundidad + 1) for hijo in hijos]
            x = sum(x_hijos) / len(x_hijos)
        posiciones[id(nodo)] = (x, -float(profundidad))
        return x

    ubicar(raiz)
    ancho = max(7.0, contador_hojas * 0.75)
    profundidad_maxima = int(max(-y for _, y in posiciones.values()))
    figura, eje = plt.subplots(figsize=(ancho, max(4.5, profundidad_maxima * 1.15)))

    # Dibuja cada nodo y sus conexiones.
    def pintar(nodo: Nodo) -> None:
        x, y = posiciones[id(nodo)]
        for hijo in (nodo.izquierdo, nodo.derecho):
            if hijo is not None:
                hx, hy = posiciones[id(hijo)]
                eje.plot([x, hx], [y, hy], color="#64748b", linewidth=1.5, zorder=1)
                pintar(hijo)
        eje.text(x, y, nodo.valor, ha="center", va="center", fontsize=11,
                 bbox={"boxstyle": "circle,pad=0.35", "fc": "#dbeafe", "ec": "#1d4ed8", "lw": 1.5},
                 zorder=2)

    pintar(raiz)
    eje.set_title("Arbol sintactico (con + y ? simplificados)", fontsize=14)
    eje.axis("off")
    figura.tight_layout()
    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=180, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(figura)


# Procesa una expresion desde infix hasta su arbol sintactico.
def procesar(expresion: str, numero: int, salida: Path, mostrar: bool, verbose: bool) -> Path:
    tokens = tokenizar(expresion)
    infix_explicit = agregar_concatenacion(tokens)
    postfix, pasos = infix_a_postfix(infix_explicit)
    arbol = postfix_a_arbol(postfix)
    destino = salida / f"arbol_{numero}.png"

    print(f"\n{'=' * 72}\nEXPRESION {numero}: {expresion}")
    print(f"Infix explicita : {' '.join(infix_explicit)}")
    if verbose:
        print("\nPaso | Token | Salida postfix | Pila")
        for indice, (token, actual, pila) in enumerate(pasos, 1):
            print(f"{indice:>4} | {token:^5} | {actual:<30} | {pila}")
    print(f"Postfix         : {' '.join(postfix)}")
    print("Simplificaciones: r+ = r.r*    r? = r|ε")
    dibujar_arbol(arbol, destino, mostrar)
    print(f"Arbol guardado  : {destino}")
    return destino


# Lee las expresiones regulares del archivo de texto.
def leer_expresiones(ruta: Path) -> list[str]:
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta}")
    return [linea.strip() for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]


# Configura y ejecuta el programa principal.
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", nargs="?", type=Path, default=ARCHIVO_PREDETERMINADO)
    parser.add_argument("--salida", type=Path, default=DIRECTORIO_SALIDA)
    parser.add_argument("--mostrar", action="store_true", help="abre cada arbol en una ventana")
    parser.add_argument("--sin-pasos", action="store_true", help="oculta la traza Shunting Yard")
    args = parser.parse_args()

    try:
        expresiones = leer_expresiones(args.archivo)
        if not expresiones:
            raise ValueError("El archivo no contiene expresiones")
        for numero, expresion in enumerate(expresiones, 1):
            procesar(expresion, numero, args.salida, args.mostrar, not args.sin_pasos)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
