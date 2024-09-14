from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from datetime import datetime
from bson import ObjectId
import io
import matplotlib

matplotlib.use('Agg')

class DataAnalyzer():
    def __init__(self, db, conversation_id) -> None:
        self.user_id = None
        self.username = None
        self.db = db
        self.entity_df = pd.DataFrame(columns=['category', 'entity', 'frequency', 'sentiment', 'since', 'last'])
        self.conversation_id = conversation_id
    
    def get_history(self):
        """
        Extract all entities and emotions from all conversations associated with a specific user.
        """

        print(f"ObjectId for username {self.username}: {self.user_id}")

        # 2. Buscar todas las conversaciones asociadas a este usuario
        conversations = list(self.db.conversations.find({'user_id': self.user_id}))

        # Verificar que se encontraron conversaciones
        if not conversations:
            print(f"No conversations found for user with ObjectId: {self.user_id}")
            return False

        print(f"Found {len(conversations)} conversations for user {self.username}")

        # Resto del código para procesar todas las entidades en todas las conversaciones
        categories = ['places', 'people', 'orgs', 'others']
        entities_list = []
        emotions_list = []

        # Recorrer todas las conversaciones
        for conversation in conversations:
            print(f"Processing conversation {conversation.get('_id')} for user_id: {self.user_id}, username: {self.username}")
            timestamp = conversation.get('start_time', None)
    
            if not timestamp:
                print("No timestamp found, skipping conversation.")
                continue

            # Obtener todas las entidades de la conversación
            entities_in_conversation = conversation.get('entities', {})
            print(f"Entities in conversation: {entities_in_conversation}")
            emotions_in_conversation = conversation.get('emotions', [])
            
            # Recopilar entidades de cada categoría
            for category in categories:
                category_entities = entities_in_conversation.get(category, [])
                print(f"Entities in category '{category}': {category_entities}")

                # Iterar sobre las entidades, ahora asumimos que son listas con dos elementos
                for entity_data in category_entities:
                    if len(entity_data) == 2:
                        entity, sentiment = entity_data
                        print(f"Adding entity: {entity}, Sentiment: {sentiment}")
                        # Añadir todas las entidades a la lista general
                        entities_list.append({
                            'category': category,
                            'entity': entity,
                            'frequency': 1,  # Inicialmente se cuenta como 1
                            'sentiment': sentiment,
                            'since': timestamp,
                            'last': timestamp
                        })

            for emotion_data in emotions_in_conversation:
                emotion, intensity = emotion_data
                if emotion != 'neutral':  # Filter out neutral emotions
                    print(f"Adding emotion: {emotion}, Intensity: {intensity}")
                    emotions_list.append({
                        'emotion': emotion,
                        'intensity': intensity,
                        'timestamp': timestamp
                    })
        # Imprimir el contenido de `entities_list`
        print(f"Entities list: {entities_list}")

        if not entities_list:
            print("No entities found for this user.")
            return False

        # Convertir la lista de entidades a un DataFrame
        self.entity_df = pd.DataFrame(entities_list)

        # Imprimir las columnas del DataFrame antes de continuar
        print(f"DataFrame columns: {self.entity_df.columns}")

        if set(['category', 'entity']).issubset(self.entity_df.columns):
            # Agrupar por categoría y entidad para combinar múltiples menciones de la misma entidad
            self.entity_df = self.entity_df.groupby(['category', 'entity']).agg({
                'frequency': 'sum',  # Sumar frecuencias si la entidad aparece en múltiples conversaciones
                'sentiment': 'first',  # Tomar el primer sentimiento detectado
                'since': 'min',  # Fecha de la primera mención
                'last': 'max'  # Fecha de la última mención
            }).reset_index()
            print("Processed Entities DataFrame:", self.entity_df)
            return True
        else:
            print("Required columns 'category' or 'entity' are missing from the DataFrame.")
            raise KeyError("Missing 'category' or 'entity' column in the DataFrame.")

    def plot_wordcloud(self):
        """
        Genera un wordcloud y devuelve la imagen.
        """
        if self.entity_df.empty:
            print("No data to plot.")
            return None

        # Crear el diccionario de frecuencias para la nube de palabras
        entity_counts = dict(zip(self.entity_df['entity'], self.entity_df['frequency']))
        
        # Generar el WordCloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(entity_counts)

        # Guardar la gráfica en un objeto de memoria en formato PNG
        img = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"WordCloud for User {self.user_id}")
        plt.savefig(img, format='png')
        plt.close()  # Cerrar la figura para evitar sobrecargar la memoria
        img.seek(0)  # Mover el cursor al principio del objeto BytesIO
        return img  # Retornar la imagen como objeto BytesIO

    def plot_barplot(self):
        """
        Genera un bar plot y devuelve la imagen.
        """
        if self.entity_df.empty:
            print("No data to plot.")
            return None

        # Ordenar por frecuencia y tomar las 10 entidades más frecuentes
        top_entities = self.entity_df.sort_values(by='frequency', ascending=False).head(10)
        
        img = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.barh(top_entities['entity'], top_entities['frequency'], color='skyblue')
        plt.xlabel('Frequency')
        plt.ylabel('Entity')
        plt.title(f"Top 10 Entities for User {self.user_id}")
        plt.gca().invert_yaxis()  # Invertir el eje y para que la entidad más frecuente esté arriba
        plt.savefig(img, format='png')
        plt.close()  # Cerrar la figura

        img.seek(0)
        return img
    # def plot_wordcloud(self):
    #     """
    #     Plot a word cloud with all the entities related to a user.
    #     """
    #     if self.entity_df.empty:
    #         print("No data to plot.")
    #         return
        
    #     # Create a frequency dictionary for the word cloud
    #     entity_counts = dict(zip(self.entity_df['entity'], self.entity_df['frequency']))
        
    #     wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(entity_counts)
        
    #     plt.figure(figsize=(10, 5))
    #     plt.imshow(wordcloud, interpolation='bilinear')
    #     plt.axis('off')
    #     plt.title(f"WordCloud for User {self.user_id}")
    #     plt.show()

    # def plot_barplot(self):
    #     """
    #     Plot a bar plot showing the most frequent entities.
    #     """
    #     if self.entity_df.empty:
    #         print("No data to plot.")
    #         return
        
    #     # Sort by frequency and take the top 10 most frequent entities
    #     top_entities = self.entity_df.sort_values(by='frequency', ascending=False).head(10)
        
    #     plt.figure(figsize=(10, 5))
    #     plt.barh(top_entities['entity'], top_entities['frequency'], color='skyblue')
    #     plt.xlabel('Frequency')
    #     plt.ylabel('Entity')
    #     plt.title(f"Top 10 Entities for User {self.user_id}")
    #     plt.gca().invert_yaxis()  # To have the highest frequency at the top
    #     plt.show()
