# Laboratorio 3

**Universidad del Valle de Guatemala**  
**Facultad de Ingeniería**  
**Teoría de la Computación**  
**Catedrático:** Pablo Koch  
**Sección:** 20  
**Estudiante:** Juan Francisco Orozco Mijangos (24647)

## Problema 1

Se desarrolló un programa en Python que lee expresiones regulares desde un archivo de texto y utiliza el algoritmo Shunting Yard para convertirlas de formato infix a postfix. A partir de la expresión postfix, el programa construye un árbol sintáctico mediante una pila de objetos `Nodo` y utiliza la librería `matplotlib` para dibujarlo en pantalla y guardarlo como una imagen PNG.

El programa agrega explícitamente el operador de concatenación `.` y aplica las simplificaciones `r+ = r.r*` y `r? = r|ε`. Durante la ejecución muestra cada paso de Shunting Yard, la salida postfix, la pila de operadores y la ubicación de cada árbol generado.

Para instalar la libreria graficadora:

```bash
python3 -m pip install -r requirements.txt
```

Para mostrar la ejecución completa y abrir los árboles en pantalla:

```bash
python3 laboratorio3.py --mostrar
```

[Video de demostración del Problema 1](https://youtu.be/0yyOZQpkOGw)

## Problema 2

Se utilizó el Lema de Arden para encontrar la expresión regular representada por el autómata proporcionado. Se plantearon y simplificaron las ecuaciones correspondientes a sus estados hasta obtener `(ε|0)(ε|1)0*`. El procedimiento completo se encuentra entregado en problema2.pdf (branch 2).
