# Local imports
from datetime import datetime

# Third party imports
from openai import OpenAI
from bson.objectid import ObjectId

class Chatbot:
    """
    Chatbot logic including bot response and db management
    """
    def __init__(self, api_key, language="ES", model="gpt-4", mongo=None):
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
        self.mongo = mongo
        self.language = language
        self.start_time = datetime.now()
        self.context = {
            "emotions": [],
            "persons": [],
            "places": [],
            "hobbies": [],
            "conversation": []
        }
          
    def start_conver(self):
        """
        Initialize conversation register on mongo
        """
        conversation = {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,  # Asegúrate de obtener este valor correctamente
            "messages": [],
            "entities": {"people": [], "places": [], "orgs": [], "others": []},
            "emotions": [],
            "start_time": datetime.now(),
            "duration": 0,
            "last_update": None
        }
        self.mongo.db.conversations.insert_one(conversation)

    def get_user_data(self,user_id):
        #### BORRAR? Se usa para analytics?
        user_data = self.mongo.db.users.find_one({"user_id": user_id})
        
        # Extraer emociones y convertirlas para el gráfico
        emotions = [(emotion[0], emotion[1], emotion[2].strftime('%Y-%m-%d')) for emotion in user_data['emotions']]
        emotion_labels = [e[2] for e in emotions]  # fechas
        emotion_data = [e[1] for e in emotions]  # porcentajes

        # Extraer hobbies y convertirlos para el gráfico
        hobbies = [(hobbie[0], hobbie[1]) for hobbie in user_data['hobbies']]
        hobby_labels = [h[0] for h in hobbies]  # nombres de los hobbies
        hobby_data = [h[1] for h in hobbies]  # frecuencias

        return emotion_labels, emotion_data, hobby_labels, hobby_data

    def update_context(self, user_input, response, features_dict):
        """
        Update conversation context to get a better bot response

        Args:
            user_input (str): User input message
            response (str): Bot response 
            features_dict (dict): Detected features on user's input message
        """
        # Add features and messages to context
        # self.context['conversations'].append({"user": user_input, "bot": response, "datetime": datetime.now})  No se si hace falta
        self.context['emotions'].extend(features_dict['emotion'])
        self.context['places'].extend(features_dict['entities']['places'])
        self.context['people'].extend(features_dict['entities']['people'])
        self.context['orgs'].extend(features_dict['entities']['orgs'])
        
    def redact_context(self):
        """
        Context formatting as system role for the chatbot input
        """
        context_description = "\n".join([
            f"Emociones detectadas en el chat: {', '.join(self.context['emotions'])}",
            f"Personas mencionadas previamente: {', '.join(self.context['persons'])}",
            f"Lugares mencionados previamente: {', '.join(self.context['places'])}",
            # f"Hobbies mencionados previamente: {', '.join(self.context['hobbies'])}",
            ])
        # return f"Eres un psicólogo que ayuda a los pacientes en base a su estado emocional y a hobbies y personas mencionadas previamente, \
        #   los cuales tienen asociado un valor de sentimiento. Tu metodología consiste en primero entender cómo se siente el pasciente y, posteriormente, \
        #   recomendar actividades que le ayuden a mejorar su estado emocional. En el caso de no tener información sobre emociones, hobbies, personas, \
        #   recomienda actividades en función de las emociones detectadas en la conversación. Responde al paciente en no más de 50 tokens, teniendo en cuenta la \
        #   siguiente información: \n{context_description}"
    
        system_role = "Eres un psicólogo especializado en pacientes con procastinación y overthinking. Proporciona un lugar seguro para expresarse al paciente \
            y, cuando tengas los datos necesarios sobre su estado emocional y la causa, recomiéndale actividades para paliarlo."

        return system_role

    def save_conver(self, mongo, user_message, response, features_dict):
        """Save message to conversations with user message, bot response, and additional features."""

        # Inicializar la operación de actualización para las entidades
        entities_update = {}
        sentiment = features_dict['sentiment']
        for entity_type, entities in features_dict['entities'].items():
            if entities:  # Verificar si la lista de entidades no está vacía
                sentimental_entities = [(entity, features_dict['sentiment']) for entity in entities]
                entities_update[f"entities.{entity_type}"] = {"$each": sentimental_entities}
        
        # Calcular la duración de la conversación
        duration = datetime.now() - self.start_time
        duration_sec = duration.total_seconds()
        duration_min = int(duration_sec / 60)
        # Preparar y ejecutar la operación de actualización en MongoDB
        update_result = mongo.db.conversations.update_one(
            {"conversation_id": self.conversation_id},
            {
                "$push": {
                    "messages": {"user_message": user_message, "bot_message": response},
                    "emotions": features_dict['emotion'],
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
        Envía la pregunta al modelo y obtiene una respuesta considerando el contexto actualizado.
        """
        try:
            system_prompt = self.redact_context()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=75,
                stop=["Usuario:", "Bot:", "Adiós", "Bye"]
            )
            message = response.choices[0].message.content
            # self.update_context(user_input, message)
            return message
        except Exception as e:
            return f"An error occurred: {str(e)}"

