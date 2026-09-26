# Cota teórica de error — Count-Min Sketch (A.1d)

## 1. Desigualdad de Markov

Para una variable aleatoria `X ≥ 0`: `P(X ≥ k · E[X]) ≤ 1/k`.

Es una cota floja (no da el valor exacto, solo un tope) pero válida sea cual sea la distribución de `X`.

## 2. De Markov a la cota del Count-Min Sketch

`d` funciones hash, cada una sobre una fila de ancho `w`. `estimate(x) = min_j T[j][h_j(x)]`.

Para una fila `j`, el "ruido" que se suma a `count(x)` por colisiones es `X_j = Σ_{y≠x} count(y) · 1[h_j(y)=h_j(x)]`, y con hashing uniforme sobre `w` celdas: `E[X_j] ≤ N/w`, donde `N` es la suma de todos los conteos (excluyendo `x`).

Eligiendo `w = e/ε`, queda `E[X_j] ≤ (ε/e)·N`. Aplicando Markov con `k=e`: `P(X_j ≥ ε·N) ≤ 1/e`.

Como `estimate(x)` toma el mínimo de las `d` filas, el error final solo llega a `ε·N` si fallan las `d` filas a la vez: `P(estimate(x) − count(x) ≥ ε·N) ≤ (1/e)^d = e^(−d) = δ`.

El sketch nunca subestima, así que el resultado formal es:

> **Con probabilidad ≥ 1−δ:** `count(x) ≤ estimate(x) ≤ count(x) + ε·N`, con `ε = e/w`, `δ = e^(−d)`.

## 3. Aplicación a los datos de prueba y contraste con lo observado

Datos: `100.000` elementos, `1.000` claves, `d=10` en ambos casos. `N ≈ 99.900`, conteo medio real por clave `≈ 100`.

| `w`  | `ε=e/w` | Cota absoluta `ε·N` | Cota de `avg_error` = `1+ε·N/100` | Dato observado | ¿Consistente? |
|------|---------|----------------------|--------------------------------------|-----------------|----------------|
| 100  | 0,0272  | ≈ 2.716              | ≈ **28,16**                          | 6,46            | Sí, por debajo de la cota |
| 2000 | 0,00136 | ≈ 135,8              | ≈ **2,36**                           | 1,0 (exacto)    | Sí, por debajo de la cota |

La cota es floja (peor caso con `δ≈4,54×10⁻⁵`), por lo que los valores medidos quedan por debajo de lo que permite la teoría en ambos casos.