# Third party imports
from transformers import pipeline

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

    def get_emotion(self):
        """
        Extract emotion from user's input message
        """
        emotions = self.emotion_extractor(self.text)
        if  emotions[0]['label']== 'others':
            self.emotion = 'neutral'
        else:
            self.emotion = emotions[0]['label']
        return self.emotion
    
    def get_sentiment(self):
        """
        Extract sentiment from user's input message
        """
        sentiments = self.sentiment_extractor(self.text)
        sentiment_master = {
            'POS': 'positivo',
            'NEG': 'negativo',
            'NEU': 'neutral'
        }
        self.sentiment = sentiment_master[sentiments[0]['label']]
        return self.sentiment



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
    featurer.get_emotion()
    featurer.get_sentiment()

    features_dict = {
        'emotion': featurer.emotion,
        'entities': featurer.entities,
        'sentiment': featurer.sentiment
    }

    return features_dict