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
        Initialize conversation register on mongo
        """
        conversation = {
            "user_id": self.user_id,
            "messages": [],
            "entities": {"people": [], "places": [], "orgs": [], "others": []},
            "emotions": [],
            "start_time": datetime.now(),
            "duration": 0,
            "last_update": None
        }
        
        # Insert the conversation document and retrieve the inserted ID
        result = self.db.conversations.insert_one(conversation)
        # Store the conversation ID
        self.conversation_id = result.inserted_id

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


    def update_context(self, features_dict):
        """
        Update conversation context to get a better bot response

        Args:
            features_dict (dict): Detected features on user's input message
        """
        self.context['emotions'].extend([f"{features_dict['emotion']} ({features_dict['sentiment']})"])
        self.context['places'].extend([f"{place} ({features_dict['sentiment']})" for place in features_dict['entities']['places']])
        self.context['people'].extend([f"{person} ({features_dict['sentiment']})" for person in features_dict['entities']['people']])
        self.context['orgs'].extend([f"{org} ({features_dict['sentiment']})" for org in features_dict['entities']['orgs']])
        
    def get_system_role(self):
        """
        Context formatting as system role for the chatbot input
        """
        context_description = "\n".join([
            f"- Género del usuario {self.gender}",
            f"- Emociones detectadas en el chat: {', '.join(self.context['emotions'])}",
            f"- Personas mencionadas previamente: {', '.join(self.context['people'])}",
            f"- Lugares mencionados previamente: {', '.join(self.context['places'])}",
            f"- Empresas mencionadas previamente: {', '.join(self.context['orgs'])}",
            ])

        if self.is_ready_for_recommendation():
            system_role = f"Eres un psicólogo especializado que ahora proporciona recomendaciones de actividades basadas en un análisis detallado de las emociones y situaciones en el contexto del usuario. Su contexto es: {context_description} "
        else:
            system_role = f"Eres un psicólogo especializado que está recogiendo información sobre el estado emocional del usuario y las situaciones que lo rodean para entender mejor cómo ayudar. Por ahora, el contexto del usuario es: {context_description}"

        return system_role

    def save_conver(self, db, user_input, response, features_dict):
        """
        Save message to conversations with user message, bot response, and additional features.
        
        Args:
            user_input (str): User input message
            response (str): Bot response
            features_dict (dict): Detected features on user's input message
        """
        print('Saving conversation...')
        # Entities preparation for saving in mongo
        entities_update = {}
        sentiment = features_dict['sentiment']
        for entity_type, entities in features_dict['entities'].items():
            if entities:  # Verificar si la lista de entidades no está vacía
                sentimental_entities = [(entity, sentiment) for entity in entities]
                entities_update[f"entities.{entity_type}"] = {"$each": sentimental_entities}
        
        # Duration calculation
        duration = datetime.now() - self.start_time
        duration_sec = duration.total_seconds()
        duration_min = int(duration_sec / 60)

        # Update conversation data to mongo
        update_result = db.conversations.update_one(
            {"_id": self.conversation_id},
            {
                "$push": {
                    "messages": {"user_message": user_input, "bot_message": response},
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
        Send user input to chatbot model and get a response taking into account the user's context
        
        Args:
            user_input (str): User input message
        """
        try: 
            # Redact system role with context
            system_prompt = self.get_system_role()

            # Query the chatbot for a response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=100,
                stop=["Usuario:", "Bot:", "Adiós", "Bye"]
            )
            message = response.choices[0].message.content

            return message
        
        except Exception as e:
            return f"An error occurred: {str(e)}"

