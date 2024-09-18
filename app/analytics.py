
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
import time 

matplotlib.use('Agg')

def clean_emotions(df):
    """
    Preprocess detected emotions for analytics
    Args:
        df (pd.DataFrame): Emotion dataset to clean
    """
    df['probability'] = pd.to_numeric(df['probability'], errors='coerce')
    df = df.dropna(subset=['emotion', 'probability'])
    df['emotion'] = df['emotion'].astype(str).str.strip().str.lower()
    return df

def clean_empty_convers(analyzer):
    """
    Preprocess convers to delete those empty
    Args:
        analyzer (Object)
    """
    if analyzer.emotion_df.empty and analyzer.entity_df.empty and analyzer.sentiment_df.empty and analyzer.hate_df.empty:
        print("No useful data found in the current conversation. Skipping.")
        return False
    print("Conversations with valid data found.")
    return True 

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
        """
        Recover user's historical feature_dicts
        """
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
            conversation_id = conversation['_id']
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
                            'conversation_id': str(conversation_id)
                        })

                hate_data = message.get('hate', {})
                if hate_data:
                    hate_list.append({
                        'hateful': hate_data.get('hateful', 0),
                        'targeted': hate_data.get('targeted', 0),
                        'aggressive': hate_data.get('aggressive', 0),
                        'timestamp': timestamp,
                        'conversation_id': str(conversation_id)
                    })

                irony_data = message.get('irony', {})
                if irony_data:
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
                    if len(entity_info) == 2 and isinstance(entity_info[1], dict):
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
        return clean_empty_convers(self)

    def plot_sentiments_over_time(self):
        """
        Generate a barplot with historical sentiments

        Returns:
            filename_irony (str): Output file name
        """

        # Filepath definition
        filename_irony = f'irony_evolution_{int(time.time())}.png'
        temp_file_path = os.path.join(self.image_dir, filename_irony)

        # Delete empty
        self.sentiment_df.dropna(subset=['timestamp'], inplace=True)
        
        # Set types
        self.sentiment_df['timestamp'] = pd.to_datetime(self.sentiment_df['timestamp'], errors='coerce')
        self.sentiment_df['Positive'] = pd.to_numeric(self.sentiment_df['Positive'], errors='coerce')
        self.sentiment_df['Negative'] = pd.to_numeric(self.sentiment_df['Negative'], errors='coerce')
        self.sentiment_df['Neutral'] = pd.to_numeric(self.sentiment_df['Neutral'], errors='coerce')

        # Group by date
        sentiment_by_date = self.sentiment_df.groupby(self.sentiment_df['timestamp'].dt.date).mean(numeric_only=True)

        if sentiment_by_date.empty:
            print("No data available for plotting.")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.25
        positions = np.arange(len(sentiment_by_date.index))
        ax.bar(positions - bar_width, sentiment_by_date['Positive'], width=bar_width, label='Positive', color='green')
        ax.bar(positions, sentiment_by_date['Negative'], width=bar_width, label='Negative', color='orange')
        ax.bar(positions + bar_width, sentiment_by_date['Neutral'], width=bar_width, label='Neutral', color='purple')
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Probability')
        ax.set_xticks(positions)
        ax.set_xticklabels(sentiment_by_date.index, rotation=45)
        ax.legend(loc='upper right')

        # Save in temporal folder
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_irony

    def plot_emotion_pie_chart(self):
        """
        Generate pie chart with all emotions

        Returns:
            filename_pie (str): Output file name
        """
        if self.emotion_df.empty:
            print("No emotion data to plot.")
            return None

        # Path definition
        filename_pie = f'emotion_pie_{int(time.time())}.png'
        temp_file_path = os.path.join(self.image_dir, filename_pie)

        # Data cleaning
        self.emotion_df = clean_emotions(self.emotion_df)

        # Check enough data
        if self.emotion_df.empty:
            print("No emotion data to plot after cleaning.")
            return None

        # Group by emotion
        emotion_totals = self.emotion_df.groupby('emotion')['probability'].sum()

        # Check emptyness
        if emotion_totals.empty:
            print("No emotion totals to plot.")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        wedges, texts, autotexts = ax.pie(
            emotion_totals,
            labels=emotion_totals.index,
            autopct='%1.1f%%',
            colors=plt.cm.Paired.colors
        )
        ax.legend(
            wedges,
            emotion_totals.index,
            title="Emociones", 
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        # Save in temporal file
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_pie

    def plot_emotion_evolution_over_time(self):
        """
        Generate line graph with emotion evolution

        Returns:
            filename_emotion (str): Output file name
        """
        
        if self.emotion_df.empty:
            print("No emotion data to plot.")
            return None
        
        # Path definition
        filename_emotion = f'emotion_time.png'
        temp_file_path = os.path.join(self.image_dir, filename_emotion)

        # Data cleaning
        self.emotion_df['timestamp'] = pd.to_datetime(self.emotion_df['timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        self.emotion_df.dropna(subset=['timestamp'], inplace=True)

        # Group by emotion and date
        daily_emotions = self.emotion_df.groupby(['emotion', pd.Grouper(key='timestamp', freq='D')])['probability'].mean().unstack(0)
        daily_emotions.fillna(0, inplace=True)

        # Check enough data
        if daily_emotions.empty:
            print("No data available for plotting.")
            return None

      
        fig, ax = plt.subplots(figsize=(10, 6))
        for emotion in daily_emotions.columns:
            if not daily_emotions[emotion].empty:
                ax.plot(daily_emotions.index, daily_emotions[emotion], label=emotion)
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Probability')
        ax.legend(loc='upper right')
        
        # Save to temporal folder
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_emotion

    def plot_most_positive_entities(self):
        """
        Generates a bar plot with the entities that have the most positivity associated with them.

        Returns:
            filename_most_pos(str): Output file name
        """
        if self.entity_df.empty:
            print("No entity data to plot.")
            return None

        most_positive_entities = self.entity_df.sort_values(by='sentiment_pos', ascending=False).head(10)

        # Checkk enough data
        if most_positive_entities.empty:
            print("No data to plot after filtering.")
            return None

        # Path definition
        filename_most_pos = f'most_positive_entities_{int(time.time())}.png'
        temp_file_path = os.path.join(self.image_dir, filename_most_pos)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(most_positive_entities['entity'], most_positive_entities['sentiment_pos'], color='green')
        ax.set_xlabel('Positivity Score')
        ax.set_ylabel('Entity')
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_most_pos

    def plot_least_positive_entities(self):
        """
        Generate a barplot with the least positive entities for the user

        Returns:
            filename_least_pos (str): Output file name
        """
        if self.entity_df.empty:
            print("No entity data to plot.")
            return None

        least_positive_entities = self.entity_df.sort_values(by='sentiment_pos', ascending=True).head(10)

        # Check  enough data
        if least_positive_entities.empty:
            print("No data to plot after filtering.")
            return None

        # Path definition
        filename_least_pos = f'least_positive_entities_{int(time.time())}.png'
        temp_file_path = os.path.join(self.image_dir, filename_least_pos)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(least_positive_entities['entity'], least_positive_entities['sentiment_pos'], color='red')
        ax.set_xlabel('Positivity Score')
        ax.set_ylabel('Entity')
        ax.invert_yaxis()
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_least_pos

    def plot_hate_speech_evolution(self):
        """
        Generate a plot with hate speech evolution in time

        Returns:
            filename_hate (Str): Output filename
        """
        if self.hate_df.empty:
            print("No hate speech data to plot.")
            return None

        # Group by conversation
        grouped_df = self.hate_df.groupby('conversation_id').agg({
            'hateful': 'mean',
            'targeted': 'mean',
            'aggressive': 'mean',
            'timestamp': 'max'
        }).reset_index()

        # Path definition
        filename_hate = f'hate_evolution_{int(time.time())}.png'
        temp_file_path = os.path.join(self.image_dir, filename_hate)

        img = io.BytesIO()
        plt.figure(figsize=(10, 6))
        plt.plot(grouped_df['timestamp'], grouped_df['hateful'], label='Hate Speech', color='blue', marker='o')
        plt.plot(grouped_df['timestamp'], grouped_df['targeted'], label='Targeted Speech', color='green', marker='o')
        plt.plot(grouped_df['timestamp'], grouped_df['aggressive'], label='Aggressive Speech', color='red', marker='o')
        plt.xlabel('Time')
        plt.ylabel('Probability')
        plt.xticks(rotation=45, ha='right')
        plt.legend(['Hateful', 'Targeted', 'Aggressive'],loc='upper right')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(temp_file_path, format='png') 
        plt.clf()
        plt.close()

        img.seek(0)
        return filename_hate

    def plot_irony_evolution(self):
        """
        Generate a plot with irony evolution in time

        Returns:
            filename_irony (str): Filename output
        """
        if self.irony_df.empty:
            print("No irony data to plot.")
            return None
        
        # Path definition
        filename_irony = f'irony_evolution.png'
        temp_file_path = os.path.join(self.image_dir, filename_irony)

        # Data cleaning
        self.irony_df['timestamp'] = pd.to_datetime(self.irony_df['timestamp'], errors='coerce')
        self.irony_df.dropna(subset=['timestamp'], inplace=True)

        # Check enough data
        if self.irony_df.empty:
            print("No valid irony data after cleaning.")
            return None

        # Group by conversation
        grouped_irony_df = self.irony_df.groupby('conversation_id').agg({
            'ironic': 'mean',
            'not_ironic': 'mean',
            'timestamp': 'max'
        }).reset_index()

        # Check empty
        if grouped_irony_df.empty:
            print("No data to plot after grouping.")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        width = 0.35  
        x = np.arange(len(grouped_irony_df['conversation_id']))
        ax.bar(x - width/2, grouped_irony_df['ironic'], width=width, label='Ironic', color='green')
        ax.bar(x + width/2, grouped_irony_df['not_ironic'], width=width, label='Not Ironic', color='orange')
        ax.set_xlabel('Conversation ID')
        ax.set_ylabel('Probability')
        ax.set_xticks(x)
        ax.set_xticklabels(grouped_irony_df['timestamp'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')
        ax.legend(loc='upper right')
        fig.savefig(temp_file_path, format='png')
        plt.close(fig)

        return filename_irony
    
    #### TO CHECK EVERYHING IS WORKING -> Also uncomment its use in analyics page (app.py)

    # def save_all_dfs_to_excel(self, base_path):
    #     """
    #     Save all dataframes with analysis extracted data

    #     Args:
    #     base_path (str): Outputpath where to save dfs
    #     """
    #     # Map DataFrames names
    #     dataframes = {
    #         'emotion_data.xlsx': self.emotion_df,
    #         'irony_data.xlsx': self.irony_df,
    #         'hate_speech_data.xlsx': self.hate_df,
    #         'sentiment_data.xlsx': self.sentiment_df,
    #         'entity_data.xlsx': self.entity_df
    #     }

    #     for filename, df in dataframes.items():
    #         file_path = f"{base_path}/{filename}"
    #         if not df.empty:
    #             df.to_excel(file_path, index=False, engine='openpyxl')
    #             print(f"Saved {filename} successfully.")
    #         else:
    #             print(f"No data to save for {filename}.")