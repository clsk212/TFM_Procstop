# Local imports
from datetime import datetime

# Third party imports
from openai import OpenAI
from bson.objectid import ObjectId

class Chatbot:
    """
    Chatbot logic including bot response and db management
    """
    def __init__(self, api_key, language="ES", model="gpt-4", db=None, gender='Other'):
        """
        Chatbot object initialization

        Args:
            api_key (str): Key for OpenAI API
            language (str): User's language
            model (str): Selected OpenAI model
            mongo (Object): Mongo DB initialized

        """
        self.conversation_id = ObjectId()
        self.client = OpenAI(api_key = api_key)
        self.model = model
        self.user_id = None
        self.username = None
        self.db = db
        self.language = language
        self.start_time = datetime.now()
        self.gender = gender
        self.context = {
            "emotions": [],
            "people": [],
            "places": [],
            "orgs": [],
            "emotion_trigger": None
        }

    def start_conver(self):
        """
        Initialize conversation register on MongoDB
        """
        # Asegurarse de que user_id esté definido y sea válido
        if not hasattr(self, 'user_id') or not self.user_id:
            raise ValueError("user_id is not set. Please ensure user_id is defined before starting a conversation.")

        # Estructura del documento de conversación
        conversation = {
            "user_id": self.user_id,  # Asegurarse de que sea el ObjectId o identificador adecuado
            "messages": [],
            "entities": {
                "people": [],
                "places": [],
                "orgs": [],
                "others": []
            },
            "emotions": [],
            "hate": [],
            "irony": [],
            "start_time": datetime.now(),
            "duration": 0,
            "last_update": None
        }
            
        # Insertar el documento de conversación en MongoDB y obtener el ID de inserción
        result = self.db.conversations.insert_one(conversation)

        # Almacenar el conversation_id del documento recién insertado
        self.conversation_id = result.inserted_id
        print(f"Conversation started with ID: {self.conversation_id}")


    def is_ready_for_recommendation(self):
        """
        Check if there exist enough entities and emotions detected in the chat to recommend activities
        """
        emotions_list = self.context['emotions']

        # Drop 'neutral' emotion if it exists
        if 'neutral' in emotions_list:
            emotions_list = emotions_list[emotions_list != 'neutral']

        # Check if there are at least 3 distinct emotions excluding 'neutral'
        enough_emotion_info = len(set(emotions_list)) >= 3

        # Check if there are more than 2 entities in any of the 'people', 'places', or 'orgs'
        enough_entity_info = any(len(self.context[entity]) > 2 for entity in ['people', 'places', 'orgs'])

        # Return True if both conditions are satisfied
        result = enough_emotion_info and enough_entity_info
        return result


    # def update_context(self, features_dict):
    #     """
    #     Update conversation context to get a better bot response

    #     Args:
    #         features_dict (dict): Detected features on user's input message
    #     """
    #     self.context['emotions'].extend([f"{features_dict['emotion']} ({features_dict['sentiment']})"])
    #     self.context['places'].extend([f"{place} ({features_dict['sentiment']})" for place in features_dict['entities']['places']])
    #     self.context['people'].extend([f"{person} ({features_dict['sentiment']})" for person in features_dict['entities']['people']])
    #     self.context['orgs'].extend([f"{org} ({features_dict['sentiment']})" for org in features_dict['entities']['orgs']])

    def update_context(self, features_dict):
        """
        Update conversation context to get a better bot response.

        Args:
            features_dict (dict): Detected features from user's input message.
        """
        # Guardar todas las emociones y sus probabilidades en el contexto
        emotions_with_probs = [f"{emotion}: {prob:.2f}" for emotion, prob in features_dict['emotion'].items()]
        self.context['emotions'].extend(emotions_with_probs)

        # Obtener el sentimiento dominante y su probabilidad
        sentiment_dict = features_dict['sentiment']  # Esto es el diccionario con 'POS', 'NEG', 'NEU'
        dominant_sentiment = max(sentiment_dict, key=sentiment_dict.get)  # Obtener el sentimiento con mayor probabilidad
        dominant_prob = sentiment_dict[dominant_sentiment]  # Obtener la probabilidad del sentimiento dominante

        # Guardar el sentimiento dominante como un valor independiente en el contexto
        self.context['sentiment'] = f"{dominant_sentiment.capitalize()}: {dominant_prob:.2f}"

        # Actualizar los lugares, personas y organizaciones, añadiendo el sentimiento dominante
        self.context['places'].extend([f"{place} ({dominant_sentiment.capitalize()}: {dominant_prob:.2f})" for place in features_dict['entities']['places']])
        self.context['people'].extend([f"{person} ({dominant_sentiment.capitalize()}: {dominant_prob:.2f})" for person in features_dict['entities']['people']])
        self.context['orgs'].extend([f"{org} ({dominant_sentiment.capitalize()}: {dominant_prob:.2f})" for org in features_dict['entities']['orgs']])

        # Si hay hate speech o ironía, se pueden agregar al contexto también
        if features_dict.get('hate'):
            hate_score = features_dict['hate'].get('hate_speech', 0)
            self.context['hate'] = f"Hate speech score: {hate_score:.2f}"

        if features_dict.get('irony'):
            irony_score = features_dict['irony'].get('irony', 0)
            self.context['irony'] = f"Irony score: {irony_score:.2f}"

            
    def get_system_role(self):
        """
        Context formatting as system role for the chatbot input
        """
        context_description = "\n".join([
        f"- Género del usuario: {self.gender}",
        f"- Emociones detectadas en el chat: {', '.join(self.context['emotions']) if self.context['emotions'] else 'No detectadas'}",
        f"- Sentimiento (positividad): {self.context['sentiment']}",
        f"- Personas mencionadas previamente: {', '.join(self.context['people']) if self.context['people'] else 'No mencionadas'}",
        f"- Lugares mencionados previamente: {', '.join(self.context['places']) if self.context['places'] else 'No mencionados'}",
        f"- Empresas mencionadas previamente: {', '.join(self.context['orgs']) if self.context['orgs'] else 'No mencionadas'}",
        f"- Hate speech detectado: {self.context['hate']}",
        f"- Ironía detectada: {self.context['irony']}"
    ])

        if self.is_ready_for_recommendation():
            system_role = f"Eres un psicólogo especializado que tiene los datos suficientes para recomendar actividades basadas en un análisis detallado de las emociones y situaciones en el contexto del usuario. Genera una respuesta, de extensión media, bien argumentada y bien introducida teniendo en cuenta el género del usuario. Su contexto es: {context_description}."
        else:
            system_role = f"Eres un psicólogo especializado que está recogiendo información sobre el estado emocional del usuario y las situaciones que lo rodean para entender mejor cómo ayudar. Genera mensajes breves para simular una conversación por chat más cotidiana. Ten en cuenta el género del usuario. ***PROHIBIDO mencionar valores de features ni hablar de si se ha detectado una feature o no***. Por ahora, el contexto del usuario es: {context_description}"

        return system_role

    # def save_conver(self, db, user_input, response, features_dict):
    #     """
    #     Save message to conversations with user message, bot response, and additional features.
        
    #     Args:
    #         user_input (str): User input message
    #         response (str): Bot response
    #         features_dict (dict): Detected features on user's input message
    #     """
    #     print('Saving conversation...')
    #     # Entities preparation for saving in mongo
    #     entities_update = {}
    #     sentiment = features_dict['sentiment']
    #     for entity_type, entities in features_dict['entities'].items():
    #         if entities:  # Verificar si la lista de entidades no está vacía
    #             sentimental_entities = [(entity, sentiment) for entity in entities]
    #             entities_update[f"entities.{entity_type}"] = {"$each": sentimental_entities}
        
    #     # Duration calculation
    #     duration = datetime.now() - self.start_time
    #     duration_sec = duration.total_seconds()
    #     duration_min = int(duration_sec / 60)

    #     # Update conversation data to mongo
    #     update_result = db.conversations.update_one(
    #         {"_id": self.conversation_id},
    #         {
    #             "$push": {
    #                 "messages": {"user_message": user_input, "bot_message": response},
    #                 "emotions": features_dict['emotion'],
    #                 **entities_update
    #             },
    #             "$set": {
    #                 "last_update": datetime.now(),
    #                 "duration": duration_min
    #             }
    #         }
    #     )
    #     return update_result

    def save_conver(self, db, user_input, response, features_dict):
        """
        Save message to conversations with user message, bot response, and additional features.
        
        Args:
            user_input (str): User input message
            response (str): Bot response
            features_dict (dict): Detected features on user's input message
        """
        print('Saving conversation...')
        
        # Preparación de entidades para guardarlas en MongoDB
        entities_update = {}
        sentiment = features_dict['sentiment']
        for entity_type, entities in features_dict['entities'].items():
            if entities:  # Verificar si la lista de entidades no está vacía
                sentimental_entities = [(entity, sentiment) for entity in entities]
                entities_update[f"entities.{entity_type}"] = {"$each": sentimental_entities}

        # Calcular la duración de la conversación
        duration = datetime.now() - self.start_time
        duration_sec = duration.total_seconds()
        duration_min = int(duration_sec / 60)

        # Preparar el documento de MongoDB con las nuevas características
        update_result = db.conversations.update_one(
            {"_id": self.conversation_id},
            {
                "$push": {
                    "messages": {
                        "user_message": user_input,
                        "bot_message": response,
                        "emotions": features_dict['emotion'],  # Almacenar el diccionario completo de emociones
                        "sentiment": sentiment,                # Guardar la puntuación de sentimiento
                        "hate": features_dict['hate'],         # Guardar la detección de hate speech
                        "irony": features_dict['irony']        # Guardar la detección de ironía
                    },
                    **entities_update
                },
                "$set": {
                    "last_update": datetime.now(),
                    "duration": duration_min
                }
            }
        )
        
        return update_result

    
    def get_response(self, user_input):
        """
        Send user input to chatbot model and get a response taking into account the user's context
        
        Args:
            user_input (str): User input message
        """
        try: 
            # Redact system role with context
            system_prompt = self.get_system_role()

            # Query the chatbot for a response
            if self.is_ready_for_recommendation:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=200,
                    stop=["Usuario:", "Bot:", "Adiós", "Bye"]
                )
            else:
                    response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=150,
                    stop=["Usuario:", "Bot:", "Adiós", "Bye"]
                )
                
            message = response.choices[0].message.content

            return message
        
        except Exception as e:
            return f"An error occurred: {str(e)}"

