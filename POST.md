# HyperLogLog y Count-Min Sketch desde cero

## 1. Qué problema resuelven y por qué implementarlas desde cero

Ambas estructuras responden a la misma pregunta de fondo: ¿cómo contestar algo sobre un flujo de datos enorme sin guardar el flujo entero? HyperLogLog estima **cuántos elementos distintos** hay en un stream (cardinalidad). Count-Min Sketch estima **cuántas veces ha aparecido cada elemento** (frecuencia). Las dos sacrifican exactitud a cambio de memoria sublineal: en vez de un set o un diccionario que crece con los datos, usan una estructura de tamaño fijo y aceptan un margen de error acotado y conocido de antemano.

Implementarlas desde cero (en vez de usar una librería) tenía un objetivo concreto: entender de dónde sale ese margen de error, no solo usarlo. Eso obligó a tocar hashing determinista, corrección de sesgo estadístico y, más adelante, la demostración formal de la cota de error — no solo el código que "funciona".

## 2. HyperLogLog

La idea: hashear cada elemento a un número pseudoaleatorio de 160 bits (con `hashlib.sha1`, con padding explícito vía f-string para asegurar los 160 bits siempre). De ese hash se usan unos bits para elegir un "cubo" (de los `m` disponibles) y el resto para medir la racha de ceros a la izquierda. Cuantos más elementos distintos hay, más probable es ver rachas largas de ceros en algún cubo — esa es la señal que se está midiendo. El estimador final combina las rachas de todos los cubos con una corrección de sesgo (`alpha_m`) que depende de `m`.

Para cardinalidades bajas, el estimador básico se desvía, así que se añade *linear counting*: si el número estimado cae por debajo de un umbral (`2.5·m`), se usa en su lugar una fórmula basada en cuántos cubos siguen sin ningún elemento asignado (`V`, el número de registros a cero).

**El bug de `zero_streak+1`.** Para calcular `V` había dos opciones: mantener un contador aparte que se actualiza cada vez que un cubo pasa de "nunca tocado" a "tocado", o simplemente contar cuántos registros valen `0` al final. Se eligió la segunda por simplicidad. El problema: un cubo que **sí** ha sido tocado pero cuya racha de ceros medida es `0` (el caso normal cuando el primer bit relevante del hash ya es un `1`) es indistinguible, mirando solo el registro, de un cubo que nunca se tocó — los dos guardan un `0`. Eso sesgaba `V` y, con él, la fórmula de linear counting.

La corrección fue guardar `racha+1` en cada registro en vez de `racha`. Así, "nunca tocado" sigue siendo `0`, y un cubo tocado con racha real `0` pasa a guardar `1` — dejan de colisionar. El coste es un sesgo sistemático de `+1` por registro, despreciable frente al error normal del estimador en datasets grandes. La alternativa "correcta" — una lista aparte de booleanos tocado/no tocado — se descartó por añadir una estructura extra que solo aporta algo en el caso raro de datasets tan pequeños que no llegan a tocar todos los cubos; en la mayoría de usos reales, todos los cubos acaban tocados igualmente.

Verificación: tabla de error paramétrica con `K` de 100 a 200.000 elementos distintos, error real entre 0.12% y 1.58%, dentro de 3σ de la cota teórica `1.04/√m`.

## 3. Count-Min Sketch

La estructura es una tabla de `d` filas por `w` columnas. Cada fila tiene su propia función hash (implementada con un salt distinto por fila más módulo `w` en `get_columns`). Al añadir un elemento, se incrementa la celda correspondiente en cada una de las `d` filas. Al consultar la frecuencia de un elemento, se toma el **mínimo** de esas `d` celdas — el mínimo importa porque cualquier colisión solo puede sumar de más, nunca de menos, así que la fila con menos "ruido" acumulado da la mejor estimación.

Esto da una garantía dura, verificada empíricamente sobre 1000 valores de prueba: la estimación **nunca** es menor que el conteo real (`estimado ≥ real`, sin excepciones), aunque sí puede sobrestimar por colisiones.

**El bug de nombres duplicados.** Al integrar los dos módulos, `add_element` existía en ambos con significados distintos: en HyperLogLog añade un elemento a los registros; en Count-Min Sketch lo añade a la tabla de frecuencias. Al importar los dos módulos juntos, uno pisaba al otro. La solución fue renombrar solo el de HyperLogLog a `add_element_to_counters`, dejando el de Count-Min Sketch como estaba — se descartó la alternativa simétrica (renombrar también el otro a `add_element_to_table`) para mantener los nombres cortos donde no hacía falta tocarlos.

Otro detalle de implementación: `create_table` tuvo que evitar el error clásico de Python de inicializar una tabla 2D con listas compartidas por referencia (`[[0]*w]*d` comparte la misma fila `d` veces).

## 4. El contraste w=100 vs w=2000

Con `w=100`, cada fila tiene bastantes colisiones — con `N≈99.900` conteos repartidos en 100 celdas por fila, es raro que una fila quede completamente limpia para un elemento dado, así que el mínimo de las `d=10` filas sigue arrastrando algo de error (`avg_error≈6.46`).

Con `w=2000`, la probabilidad de colisión por celda cae a 1/2000, y con `d=10` filas independientes, en la práctica **casi todos los elementos acaban teniendo al menos una fila sin ninguna colisión** — basta con que una sola de las diez sea limpia para que el mínimo devuelva el conteo real exacto. Por eso el `avg_error` baja a 1.0: no es que el error medio por fila se haya reducido gradualmente, es que la probabilidad de que las diez fallen a la vez se ha vuelto casi nula, y el mínimo "encuentra" la fila buena.

La cota teórica formal de este comportamiento (de dónde salen `ε = e/w` y `δ = e^(-d)`, deducida vía la desigualdad de Markov) está en `TEORIA.md`, junto con el contraste numérico contra estos mismos datos.

## 5. Limitaciones conocidas

- No hay merge de sketches entre sí (combinar dos HyperLogLog o dos Count-Min Sketch generados por separado).
- El tamaño de `w` y `d` es fijo desde la creación; no hay redimensionado dinámico.
- La cota teórica en `TEORIA.md` es de peor caso (vía Markov) y por tanto floja — los errores reales observados quedan muy por debajo de lo que la cota permite en ambos casos probados.