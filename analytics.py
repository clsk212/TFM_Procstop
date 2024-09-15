from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from datetime import datetime
from bson import ObjectId
import io
import matplotlib
import tempfile
import shutil
import os
import numpy as np
import matplotlib.colors as mcolors

matplotlib.use('Agg')

def clean_emotions(df):
    """
    Limpia y prepara el DataFrame de emociones para su análisis.
    """
    # Convertir 'probability' a numérico
    df['probability'] = pd.to_numeric(df['probability'], errors='coerce')

    # Eliminar filas con valores nulos en 'emotion' o 'probability'
    df = df.dropna(subset=['emotion', 'probability'])

    # Limpiar y normalizar la columna 'emotion'
    df['emotion'] = df['emotion'].astype(str).str.strip().str.lower()

    return df

def limpiar_conversaciones_vacias(analyzer):
    """
    Elimina conversaciones que no tienen registros de emociones, entidades, sentimientos o hate speech.
    """
    # Revisamos si los DataFrames están vacíos
    if analyzer.emotion_df.empty and analyzer.entity_df.empty and analyzer.sentiment_df.empty and analyzer.hate_df.empty:
        print("No useful data found in the current conversation. Skipping.")
        return False  # Si todo está vacío, no seguimos procesando

    print("Conversations with valid data found.")
    return True  # Si hay datos relevantes, continuamos el procesamiento

class DataAnalyzer():
    def __init__(self, db, conversation_id, image_dir : str) -> None:
        self.user_id = None
        self.username = None
        self.db = db
        
        # DataFrames inicializados para emociones, ironía, hate speech y sentimiento
        self.emotion_df = pd.DataFrame()
        self.irony_df = pd.DataFrame()
        self.hate_df = pd.DataFrame()
        self.sentiment_df = pd.DataFrame()
        self.entity_df = pd.DataFrame()
        self.image_dir = image_dir
        self.conversation_id = conversation_id
    
    def get_history(self):
        conversations = list(self.db.conversations.find({'user_id': self.user_id}))
        if not conversations:
            print(f"No conversations found for user with ObjectId: {self.user_id}")
            return False

        print(f"Found {len(conversations)} conversations for user {self.username}")
        entities_list = []
        emotions_list = []
        irony_list = []
        hate_list = []
        sentiment_list = []

        for conversation in conversations:
            conversation_id = conversation['_id']  # Capture the conversation ID
            messages = conversation.get('messages', [])
            entities = conversation.get('entities', {})
            for message in messages:
                timestamp = message.get('timestamp', conversation.get('start_time'))

                if 'emotions' in message:
                    for emotion, probability in message['emotions'].items():
                        emotions_list.append({
                            'emotion': emotion,
                            'probability': probability,
                            'timestamp': timestamp,
                            'conversation_id': str(conversation_id)  # Add conversation ID
                        })

                hate_data = message.get('hate', {})
                if hate_data:  # Only append if hate data is present
                    hate_list.append({
                        'hateful': hate_data.get('hateful', 0),
                        'targeted': hate_data.get('targeted', 0),
                        'aggressive': hate_data.get('aggressive', 0),
                        'timestamp': timestamp,
                        'conversation_id': str(conversation_id)
                    })

                irony_data = message.get('irony', {})
                if irony_data:  # Similarly for irony data
                    irony_list.append({
                        'ironic': irony_data.get('ironic', 0),
                        'not_ironic': irony_data.get('not ironic', 0),
                        'timestamp': timestamp,
                        'conversation_id': str(conversation_id)
                    })

                if 'sentiment' in message:
                    sentiment_list.append({
                        'Positive': message['sentiment'].get('POS', 0),
                        'Neutral': message['sentiment'].get('NEU', 0),
                        'Negative': message['sentiment'].get('NEG', 0),
                        'timestamp': timestamp,
                        'conversation_id': str(conversation_id)
                    })


            for category, entities_in_category in entities.items():
                for entity_info in entities_in_category:
                    if len(entity_info) == 2 and isinstance(entity_info[1], dict):  # Validate structure and type
                        entity_name, sentiment_data = entity_info
                        entities_list.append({
                            'category': category,
                            'entity': entity_name,
                            'sentiment_neg': sentiment_data.get('NEG', 0),
                            'sentiment_neu': sentiment_data.get('NEU', 0),
                            'sentiment_pos': sentiment_data.get('POS', 0),
                            'timestamp': timestamp,
                            'conversation_id': str(conversation_id)
                        })
        # Converting lists to DataFrames
        self.emotion_df = pd.DataFrame(emotions_list)
        self.hate_df = pd.DataFrame(hate_list)
        self.irony_df = pd.DataFrame(irony_list)
        self.sentiment_df = pd.DataFrame(sentiment_list)
        self.entity_df = pd.DataFrame(entities_list)
        # Assume entities are extracted elsewhere and appended similarly

        print(f"DataFrames created with entries: Emotion({len(self.emotion_df)}), Hate({len(self.hate_df)}), Irony({len(self.irony_df)}), Sentiment({len(self.sentiment_df)})")
        return limpiar_conversaciones_vacias(self)




    def plot_sentiments_over_time(self):
        """
        Genera un gráfico de líneas que muestra la evolución de los sentimientos (Positive, Negative, Neutral) a lo largo del tiempo.
        """
        if self.sentiment_df.empty:
            print("No sentiment data to plot.")
            return None

        # Definir la ruta del archivo temporal
        filename = 'sentiment_plot.png'
        temp_file_path = os.path.join(self.image_dir, filename)

        # Asegurarse de que la columna 'timestamp' es de tipo datetime
        self.sentiment_df['timestamp'] = pd.to_datetime(self.sentiment_df['timestamp'], errors='coerce')

        # Eliminar filas con 'timestamp' NaT
        self.sentiment_df.dropna(subset=['timestamp'], inplace=True)

        # Verificar si después de la conversión hay suficientes datos
        if self.sentiment_df.empty:
            print("No valid sentiment data after cleaning.")
            return None

        # Crear una nueva figura y ejes explícitamente
        fig, ax = plt.subplots(figsize=(10, 6))

        # Graficar las probabilidades de los sentimientos: Positive, Negative, Neutral
        ax.plot(self.sentiment_df['timestamp'], self.sentiment_df['Positive'], label='Positive', color='green')
        ax.plot(self.sentiment_df['timestamp'], self.sentiment_df['Negative'], label='Negative', color='red')
        ax.plot(self.sentiment_df['timestamp'], self.sentiment_df['Neutral'], label='Neutral', color='gray')

        # Etiquetas y leyenda
        ax.set_xlabel('Time')
        ax.set_ylabel('Probability')
        ax.set_title('Evolution of Sentiments Over Time')
        ax.legend(loc='upper right')

        # Rotar las etiquetas del eje x para una mejor legibilidad
        plt.xticks(rotation=45)

        # Guardar la figura en un archivo
        fig.savefig(temp_file_path, format='png')

        # Cerrar la figura después de guardarla para liberar memoria
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename


    def plot_emotion_pie_chart(self):
        """
        Genera un gráfico circular que muestra las emociones del usuario por categoría.
        """
        if self.emotion_df.empty:
            print("No emotion data to plot.")
            return None

        # Definir la ruta del archivo temporal
        filename = 'emotion_pie.png'
        temp_file_path = os.path.join(self.image_dir, filename)

        # Limpiar el DataFrame antes de usarlo
        self.emotion_df = clean_emotions(self.emotion_df)

        # Verificar si el DataFrame sigue teniendo datos después de la limpieza
        if self.emotion_df.empty:
            print("No emotion data to plot after cleaning.")
            return None

        # Sumar las probabilidades de cada emoción para mostrar la distribución
        emotion_totals = self.emotion_df.groupby('emotion')['probability'].sum()

        # Verificar si 'emotion_totals' no está vacío
        if emotion_totals.empty:
            print("No emotion totals to plot.")
            return None

        # Crear una nueva figura explícitamente
        fig, ax = plt.subplots(figsize=(10,6))

        # Generar el gráfico circular
        ax.pie(
            emotion_totals,
            labels=emotion_totals.index,
            autopct='%1.1f%%',
            colors=plt.cm.Paired.colors
        )

        # Guardar la figura
        fig.savefig(temp_file_path, format='png')

        # Cerrar la figura después de guardarla
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename



    def plot_emotion_evolution_over_time(self):
        """
        Genera un gráfico de líneas que muestra la evolución de las emociones a lo largo del tiempo.
        """
        if self.emotion_df.empty:
            print("No emotion data to plot.")
            return None
        
        # Verificar el tipo de datos en la columna 'timestamp'
        print(self.emotion_df['timestamp'].dtype)

        # Convertir a datetime y eliminar valores NaT
        self.emotion_df['timestamp'] = pd.to_datetime(self.emotion_df['timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        print(self.emotion_df['timestamp'].dtype)

        # Eliminar filas con NaT en 'timestamp'
        self.emotion_df.dropna(subset=['timestamp'], inplace=True)

        # Agrupar los datos por emoción y fecha (diariamente) y calcular la media de 'probability'
        daily_emotions = self.emotion_df.groupby(['emotion', pd.Grouper(key='timestamp', freq='D')])['probability'].mean().unstack(0)
        
        # Rellenar valores NaN con 0
        daily_emotions.fillna(0, inplace=True)

        # Verificar que hay datos para graficar
        if daily_emotions.empty:
            print("No data available for plotting.")
            return None

        # Definir la ruta del archivo
        filename = 'emotion_time.png'
        temp_file_path = os.path.join(self.image_dir, filename)

        # Crear una nueva figura y eje explícitamente
        fig, ax = plt.subplots(figsize=(10, 6))

        # Graficar cada emoción con etiquetas para la leyenda
        for emotion in daily_emotions.columns:
            if not daily_emotions[emotion].empty:
                ax.plot(daily_emotions.index, daily_emotions[emotion], label=emotion)

        # Etiquetas y título
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Probability')
        ax.set_title('Evolution of Emotions Over Time')

        # Agregar leyenda
        ax.legend(loc='upper right')

        # Guardar la figura en un archivo
        fig.savefig(temp_file_path, format='png')

        # Cerrar la figura después de guardarla
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename



    def plot_most_positive_entities(self):
        """
        Generates a bar plot with the entities that have the most positivity associated with them.
        """
        if self.entity_df.empty:
            print("No entity data to plot.")
            return None

        # Ordenar por sentimiento y tomar las 10 entidades más positivas
        most_positive_entities = self.entity_df.sort_values(by='sentiment_pos', ascending=False).head(10)

        # Verificar si hay suficientes datos para graficar
        if most_positive_entities.empty:
            print("No data to plot after filtering.")
            return None

        # Definir la ruta del archivo temporal
        filename = 'most_positive_entities.png'
        temp_file_path = os.path.join(self.image_dir, filename)
        
        # Crear una nueva figura y ejes explícitamente
        fig, ax = plt.subplots(figsize=(10, 6))

        # Generar el gráfico de barras horizontales
        ax.barh(most_positive_entities['entity'], most_positive_entities['sentiment_pos'], color='green')
        ax.set_xlabel('Positivity Score')
        ax.set_ylabel('Entity')
        ax.set_title('Top 10 Most Positive Entities')

        # Guardar la figura en un archivo
        fig.savefig(temp_file_path, format='png')

        # Cerrar la figura después de guardarla para liberar memoria
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename

    def plot_least_positive_entities(self):
        """
        Genera un barplot con las entidades con menos positividad asociada.
        """
        if self.entity_df.empty:
            print("No entity data to plot.")
            return None

        # Ordenar por sentimiento positivo y tomar las 10 entidades menos positivas
        least_positive_entities = self.entity_df.sort_values(by='sentiment_pos', ascending=True).head(10)

        # Verificar si hay suficientes datos para graficar
        if least_positive_entities.empty:
            print("No data to plot after filtering.")
            return None

        # Definir la ruta del archivo temporal
        filename = 'least_positive_entities.png'
        temp_file_path = os.path.join(self.image_dir, filename)
        
        # Crear una nueva figura y ejes explícitamente
        fig, ax = plt.subplots(figsize=(10, 6))

        # Generar el gráfico de barras horizontales
        ax.barh(least_positive_entities['entity'], least_positive_entities['sentiment_pos'], color='red')
        ax.set_xlabel('Positivity Score')
        ax.set_ylabel('Entity')
        ax.set_title('Top 10 Least Positive Entities')

        # Invertir el eje Y para que la entidad con menor positividad esté arriba
        ax.invert_yaxis()

        # Guardar la figura en un archivo
        fig.savefig(temp_file_path, format='png')

        # Cerrar la figura después de guardarla para liberar memoria
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename


    def plot_hate_speech_evolution(self):
        """
        Genera un gráfico de líneas que muestra la evolución del hate speech en el tiempo,
        agrupado por conversation_id, con la media de hateful, targeted y aggressive
        y tomando el timestamp más reciente para cada conversation_id.
        """
        if self.hate_df.empty:
            print("No hate speech data to plot.")
            return None

        # Agrupar por conversation_id, calcular la media y obtener el timestamp más reciente
        grouped_df = self.hate_df.groupby('conversation_id').agg({
            'hateful': 'mean',
            'targeted': 'mean',
            'aggressive': 'mean',
            'timestamp': 'max'  # Seleccionamos el timestamp más reciente
        }).reset_index()

        # Definir la ruta del archivo temporal
        filename = 'hate_evolution.png'
        temp_file_path = os.path.join(self.image_dir, filename)
        # Verificar si hay alguna variabilidad en los datos
        print(grouped_df[['hateful', 'targeted', 'aggressive']].describe())

        # Crear el gráfico
        img = io.BytesIO()
        plt.figure(figsize=(10, 6))

        # Graficar las tres series: Hate Speech, Targeted Speech y Aggressive Speech
        plt.plot(grouped_df['timestamp'], grouped_df['hateful'], label='Hate Speech', color='blue', marker='o')
        plt.plot(grouped_df['timestamp'], grouped_df['targeted'], label='Targeted Speech', color='green', marker='o')
        plt.plot(grouped_df['timestamp'], grouped_df['aggressive'], label='Aggressive Speech', color='red', marker='o')

        # Etiquetas de los ejes y título
        plt.xlabel('Time')
        plt.ylabel('Probability')
        plt.title(f"Hate Speech Evolution Over Time for User {self.user_id}")

        # Añadir rotación de las etiquetas del eje X
        plt.xticks(rotation=45, ha='right')

        # Añadir leyenda y cuadrícula
        plt.legend(['Hateful', 'Targeted', 'Aggressive'],loc='upper right')
        plt.grid(True)

        # Ajustar el diseño y guardar la imagen
        plt.tight_layout()
        plt.savefig(temp_file_path, format='png')  # Guardar en la carpeta temporal
        plt.savefig(img, format='png')
        plt.clf()
        plt.close()

        img.seek(0)
        return filename


    def plot_irony_evolution(self):
        """
        Genera un gráfico de barras que muestra la evolución de la ironía en el tiempo.
        """
        if self.irony_df.empty:
            print("No irony data to plot.")
            return None

        # Asegurarse de que la columna 'timestamp' es de tipo datetime
        self.irony_df['timestamp'] = pd.to_datetime(self.irony_df['timestamp'], errors='coerce')

        # Eliminar filas con 'timestamp' NaT
        self.irony_df.dropna(subset=['timestamp'], inplace=True)

        # Verificar si hay suficientes datos después de la limpieza
        if self.irony_df.empty:
            print("No valid irony data after cleaning.")
            return None

        # Agrupar los datos por conversation_id, obteniendo el max timestamp y los valores de ironía
        grouped_irony_df = self.irony_df.groupby('conversation_id').agg({
            'ironic': 'mean',
            'not_ironic': 'mean',
            'timestamp': 'max'
        }).reset_index()

        # Verificar si el DataFrame agrupado está vacío
        if grouped_irony_df.empty:
            print("No data to plot after grouping.")
            return None

        # Crear una nueva figura y ejes explícitamente
        fig, ax = plt.subplots(figsize=(10, 6))

        # Definir el ancho de las barras
        width = 0.35  
        x = np.arange(len(grouped_irony_df['conversation_id']))

        # Graficar barras
        ax.bar(x - width/2, grouped_irony_df['ironic'], width=width, label='Ironic', color='green')
        ax.bar(x + width/2, grouped_irony_df['not_ironic'], width=width, label='Not Ironic', color='orange')

        # Etiquetas y leyenda
        ax.set_xlabel('Conversation ID')
        ax.set_ylabel('Probability')
        ax.set_xticks(x)
        ax.set_xticklabels(grouped_irony_df['timestamp'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')
        ax.legend(loc='upper right')

        # Definir la ruta del archivo
        filename = 'irony_evolution.png'
        temp_file_path = os.path.join(self.image_dir, filename)

        # Guardar la figura en un archivo
        try:
            fig.savefig(temp_file_path, format='png')
        except Exception as e:
            print(f"Error saving the figure: {e}")

        # Cerrar la figura para liberar memoria
        plt.close(fig)

        # Devolver el nombre del archivo
        return filename


    
    def save_all_dfs_to_excel(self, base_path):
        """
        Guarda todos los DataFrames relevantes en archivos Excel.

        Args:
        base_path (str): Ruta base donde se guardarán los archivos.
        """
        # Usamos un diccionario para mapear nombres de archivos a DataFrames
        dataframes = {
            'emotion_data.xlsx': self.emotion_df,
            'irony_data.xlsx': self.irony_df,
            'hate_speech_data.xlsx': self.hate_df,
            'sentiment_data.xlsx': self.sentiment_df,
            'entity_data.xlsx': self.entity_df
        }

        for filename, df in dataframes.items():
            file_path = f"{base_path}/{filename}"
            if not df.empty:
                df.to_excel(file_path, index=False, engine='openpyxl')
                print(f"Saved {filename} successfully.")
            else:
                print(f"No data to save for {filename}.")