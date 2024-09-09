from transformers import pipeline
from pprint import pprint

class FeatureExtraction:
    def __init__(self, text):
        self.text = text

        self.entity_extractor = pipeline("token-classification", model="PlanTL-GOB-ES/roberta-base-bne-capitel-ner-plus")
        self.emotion_extractor = pipeline("text-classification", model="finiteautomata/beto-emotion-analysis")
        self.sentiment_extractor = pipeline("text-classification", model="finiteautomata/beto-sentiment-analysis")

        self.emotion = None
        self.sentiment = None
        self.entities = {
            'people': [],
            'places': [],
            'orgs': [],
            'others': []
        }
    
    def get_entities(self):
        raw_entities = self.entity_extractor(self.text)
        self.clean_entities(raw_entities)
        return self.entities

    def clean_entities(self, raw_entities):
        # Diccionario para mapear los tipos de entidades a los nombres usados en self.entities
        master_entities = {
            'PER': 'people',
            'LOC': 'places',
            'ORG': 'orgs',
            'OTH': 'others'
        }

        # Inicializa una variable para guardar entidades compuestas temporalmente
        current_entity = []

        # Iterar a través de las entidades crudas
        new_word = True
        for entity in raw_entities:
            word = self.text[entity['start']:entity['end']]  # Extrae la palabra de la posición indicada
            entity_prefix = entity['entity'][0]  # B, I, E, S
            entity_type = entity['entity'][2:]  # PER, LOC, ORG, OTH
            current_type = master_entities[entity_type]
            if new_word:

                if entity_prefix == 'S':  # Si es el comienzo de una entidad o una entidad singular
                    self.entities[current_type].append(word)
                elif entity_prefix == 'B':
                    current_entity.append(word)
                    new_word = False
                else:
                    continue
            else:
                current_entity.append(word)
                if entity_prefix == 'E':
                    self.entities[current_type].append(" ".join(current_entity))
                    current_entity = []
                    new_word = True

    def get_emotion(self):
        emotions = self.emotion_extractor(self.text)
        if  emotions[0]['label']== 'others':
            self.emotion = 'neutral'
        else:
            self.emotion = emotions[0]['label']
        return self.emotion
    
    def get_sentiment(self):
        sentiments = self.sentiment_extractor(self.text)
        sentiment_master = {
            'POS': 'positivo',
            'NEG': 'negativo',
            'NEU': 'neutral'
        }
        self.sentiment = sentiment_master[sentiments[0]['label']]
        return self.sentiment



def feature_extraction(message):
    """
    Extract emotions, entities, and places from the message.

    Parameters:
    message (str): The text message to process.

    Returns:
    dict: A dictionary with extracted features.
    """
    featurer = FeatureExtraction(text = message)
    featurer.get_entities()
    featurer.get_emotion()
    featurer.get_sentiment()

    features_dict = {
        'emotion': featurer.emotion,
        'entities': featurer.entities,
        'sentiment': featurer.sentiment
    }

    return features_dict