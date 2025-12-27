import pandas as pd
from app.analytics import clean_emotions

def test_clean_emotions():
    """
    Test the clean_emotions function.
    """
    data = {'emotion': ['anger', 'joy', 'sadness '],
            'probability': ['0.9', '0.8', '0.7']}
    df = pd.DataFrame(data)
    cleaned_df = clean_emotions(df)
    assert cleaned_df.shape[0] == 3
    assert cleaned_df['probability'].dtype == 'float64'
    assert cleaned_df['emotion'].iloc[2] == 'sadness'
