# Third party imports
from transformers import pipeline
from pysentimiento import create_analyzer

class FeatureExtractor:
    """
    Feature extraction from user's messages, including entities, emotion and sentiment.
    """
    def __init__(self, text):
        """
        Initialize feature extractor
        """
        self.text = text

        self.entity_extractor = pipeline("token-classification", model="PlanTL-GOB-ES/roberta-base-bne-capitel-ner-plus")
        self.emotion_extractor = create_analyzer(task="emotion", lang="es") #pipeline("text-classification", model="finiteautomata/beto-emotion-analysis")
        self.sentiment_extractor = create_analyzer(task="sentiment", lang="es") #pipeline("text-classification", model="finiteautomata/beto-sentiment-analysis")
        self.hate_extractor = create_analyzer(task="hate_speech", lang="es")
        self.irony_extractor = create_analyzer(task="irony", lang="es")

        self.emotion = None
        self.sentiment = None
        self.hate = None
        self.irony = None
        self.entities = {
            'people': [],
            'places': [],
            'orgs': [],
            'others': []
        }
        
    
    def get_entities(self):
        """
        Extract entities from the text and format it as a dictionary
        """
        raw_entities = self.entity_extractor(self.text)
        self.clean_entities(raw_entities)
        return self.entities

    def clean_entities(self, raw_entities):
        # Master dictionary to format entities
        master_entities = {
            'PER': 'people',
            'LOC': 'places',
            'ORG': 'orgs',
            'OTH': 'others'
        }

        # Initialize list to join multiple entities
        current_entity = []

        # Iteration over raw entities to extract them
        new_word = True
        for entity in raw_entities:
            word = self.text[entity['start']:entity['end']]
            if len(word) <=2:
                continue
            entity_prefix = entity['entity'][0]
            entity_type = entity['entity'][2:]
            current_type = master_entities[entity_type]
            if new_word:
                # Singular entities
                if entity_prefix == 'S':
                    self.entities[current_type].append(word) 
                # Beggining of multiple entities
                elif entity_prefix == 'B':
                    current_entity.append(word)
                    new_word = False
                else:
                    continue
            else:
                current_entity.append(word)
                # End of multiple entities
                if entity_prefix == 'E':
                    self.entities[current_type].append(" ".join(current_entity))
                    current_entity = []
                    new_word = True

    def get_emotions(self):
        """
        Extract emotion from user's input message.
        """
        # Analizar emociones en el texto usando el extractor de emociones (Robertuito)
        result = self.emotion_extractor.predict(self.text)

        # Almacenar las probabilidades de cada emoción en el atributo self.emotions
        self.emotions = result.probas
        print(self.emotions)
        return result.output

        # Opcional: obtener la emoción dominante (la de mayor probabilidad)
        # dominant_emotion = max(self.emotions, key=self.emotions.get)

        # # Guardar la emoción dominante en un atributo (si es necesario)
        # self.dominant_emotion = dominant_emotion

        # return self.dominant_emotion  # Puedes devolver la emoción dominante si lo necesitas

        
        # emotions = self.emotion_extractor(self.text)
        # if  emotions[0]['label']== 'others':
        #     self.emotion = 'neutral'
        # else:
        #     self.emotion = emotions[0]['label']
        # return self.emotion
    
    def get_sentiment(self):
        """
        Extract sentiment from the user's input message and return the dominant sentiment.
        """
        # Extraer el sentimiento usando el extractor de sentimientos
        sentiments = self.sentiment_extractor.predict(self.text)

        # Guardar el diccionario de probabilidades (con 'NEG', 'NEU', 'POS') en self.sentiment
        self.sentiment = sentiments.probas

        # Encontrar el sentimiento mayoritario y su probabilidad
        dominant_sentiment = max(self.sentiment, key=self.sentiment.get)
        dominant_prob = self.sentiment[dominant_sentiment]
        print(self.sentiment)
        # Retornar una lista con el sentimiento mayoritario y su probabilidad
        return [dominant_sentiment, dominant_prob]


    def get_hate_speech(self):
        """
        Detect hate speech in user's input message
        """
        hate = self.hate_extractor.predict(self.text)
        self.hate = hate.probas
        print(self.hate)

    def get_irony(self):
        """
        Detect irony in user's input message
        """
        irony = self.irony_extractor.predict(self.text)
        self.irony = irony.probas
        print(self.irony)

def feature_extraction(user_input):
    """
    Extract emotions, entities, and sentiment from the user's input.

    Args:
        user_input (str): The text message to process.

    Returns:
        features_dict: A dictionary with extracted features.
    """
    featurer = FeatureExtractor(text = user_input)
    featurer.get_entities()
    featurer.get_emotions()
    featurer.get_sentiment()
    featurer.get_hate_speech()
    featurer.get_irony()

    features_dict = {
        'emotion': featurer.emotions,
        'entities': featurer.entities,
        'sentiment': featurer.sentiment,
        'hate': featurer.hate,
        'irony': featurer.irony
    }

    return features_dict