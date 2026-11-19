# Aula Python

Un asistente para estudiantes que consultan los apuntes de estructuras de datos. Por ejemplo, ante «¿Cómo retiro al primero de una cola?», podemos ver qué párrafo llega al modelo y comprobar si la respuesta explica el uso de `popleft`.

## Demo en Google Colab

1. Abre [Google Colab](https://colab.research.google.com/), selecciona **Subir** y carga `notebooks/Aula_Python.ipynb`. El cuaderno incluye el corpus y el código. Puedes usarlo por separado.
2. Si hay GPU disponible, selecciónala en **Entorno de ejecución → Cambiar tipo de entorno de ejecución**. Ejecuta las celdas en orden. La primera generación necesita Internet y espacio para descargar varios GB de pesos. En CPU puede tardar varios minutos.
3. Observa el párrafo con mayor puntaje, ejecuta la generación y contrasta la cita con el texto original. Cambia la última pregunta por «¿Cuánto cuesta viajar a Marte?» para probar el caso sin evidencia.

## Ejecutar en Windows con Python 3.11 o 3.12

Desde la raíz del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py --indexar
.\.venv\Scripts\python app.py "¿Cómo retiro al primero de una cola?"
```

Para mostrar solo la recuperación basta con la biblioteca estándar:

```powershell
py app.py --solo-fuentes "¿Cómo quito valores duplicados?"
py -m unittest discover -s pruebas -v
```

## Cómo funciona

- **Corpus.** Siete apuntes breves con ejemplos propios, redactados a partir del [tutorial oficial de Python](https://docs.python.org/es/3/tutorial/datastructures.html). Cada registro incluye tema, texto y URL.
- **Indexación.** Cada apunte ya representa una idea completa. El indexador normaliza acentos, descarta palabras frecuentes y calcula TF-IDF. SQLite conserva el vocabulario, los pesos, los vectores dispersos y sus fuentes en `aula.sqlite3`. Al editar el JSON vuelve a ejecutar `--indexar`.
- **Recuperación.** La misma transformación convierte la pregunta en un vector. Una función de SQLite calcula el coseno y devuelve hasta tres fragmentos con puntaje mínimo de 0,20. El umbral se eligió para esta demo. El puntaje expresa similitud y no una probabilidad de acierto.
- **Generación.** El modelo preentrenado [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) recibe la pregunta y los fragmentos numerados. Se revisa que los identificadores citados pertenezcan a la selección. Una cita válida aún necesita revisión de contenido. Si la recuperación queda vacía, el programa responde directamente y evita cargar el modelo.

## Qué revisar en la sustentación

La prueba incluye siete preguntas con un fragmento esperado y una fuera del corpus. También comprueba que al reconstruir la base desaparezcan los documentos retirados. Estos casos sirven para detectar regresiones. El corpus es pequeño y la recuperación depende del vocabulario compartido: una paráfrasis que use sinónimos puede perder su fuente. Para evaluar un corpus nuevo, conviene reservar preguntas distintas de las usadas para ajustar el umbral.

El componente que se ajusta al corpus es TF-IDF. Qwen conserva sus pesos preentrenados. Al cambiar un apunte, la respuesta puede actualizarse con la siguiente indexación, sin reentrenar al generador.

## Archivos

| Ruta | Contenido |
| --- | --- |
| `app.py` | Entrada desde la terminal |
| `datos/python.json` | Corpus editable con las fuentes |
| `rag/indice.py` | Vectores, persistencia y búsqueda |
| `rag/generacion.py` | Preparación del contexto y llamada al modelo |
| `pruebas/` | Preguntas de evaluación y pruebas de regresión |
| `notebooks/Aula_Python.ipynb` | Demo autónoma para Colab |
| `requirements.txt` | Dependencias para generar respuestas localmente |
