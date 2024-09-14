from pysentimiento import create_analyzer

# Crear un analizador de emociones usando Robertuito
analyzer = create_analyzer(task="emotion", lang="es")

# Analizar emociones en un texto
result = analyzer.predict("Estoy muy feliz con mi nuevo trabajo, pero también un poco nervioso.")

print(result.output)  # Te da la emoción principal detectada
print(result.probas)   # Muestra las probabilidades de cada emoción
