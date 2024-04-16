import tensorflow as tf
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
import numpy as np






#emotion_model = load_model('A:\major project\Avatarfusion\backend-part\models\scripts\e_model')



def preprocess_sentence(sentence):
  sentence = sentence.lower().strip()
  # creating a space between a word and the punctuation following it
  # eg: "he is a boy." => "he is a boy ."
  sentence = re.sub(r"([?.!,])", r" \1 ", sentence)
  sentence = re.sub(r'[" "]+', " ", sentence)
  # removing contractions
  sentence = re.sub(r"i'm", "i am", sentence)
  sentence = re.sub(r"he's", "he is", sentence)
  sentence = re.sub(r"she's", "she is", sentence)
  sentence = re.sub(r"it's", "it is", sentence)
  sentence = re.sub(r"that's", "that is", sentence)
  sentence = re.sub(r"what's", "that is", sentence)
  sentence = re.sub(r"where's", "where is", sentence)
  sentence = re.sub(r"how's", "how is", sentence)
  sentence = re.sub(r"\'ll", " will", sentence)
  sentence = re.sub(r"\'ve", " have", sentence)
  sentence = re.sub(r"\'re", " are", sentence)
  sentence = re.sub(r"\'d", " would", sentence)
  sentence = re.sub(r"\'re", " are", sentence)
  sentence = re.sub(r"won't", "will not", sentence)
  sentence = re.sub(r"can't", "cannot", sentence)
  sentence = re.sub(r"n't", " not", sentence)
  sentence = re.sub(r"n'", "ng", sentence)
  sentence = re.sub(r"'bout", "about", sentence)
  # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
  sentence = re.sub(r"[^a-zA-Z?.!,0-9 %]+", " ", sentence)
  sentence = sentence.strip()
  return sentence
#tokenizer part


def tokenize_and_preprocess(sentence, tokenizer, max_len=None):
    tokenizer.fit_on_texts(sentence)
    tokenized_sequences = tokenizer.texts_to_sequences(sentence)
    padded_sequences = pad_sequences(tokenized_sequences, maxlen=max_len)#, padding='pre', truncating='post')
    return padded_sequences

def predict_emotion(sentence):
    tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='', oov_token='<OOV>')
    e_max_length = 66
    emotion_labels = ['neutral','angry', 'fear', 'joy', 'love', 'sadness', 'suprised']
    label_encoder2 = LabelEncoder()
    label_encoder2.fit(emotion_labels)
    e_processed_sentence = tokenize_and_preprocess(sentence, tokenizer, max_len=e_max_length)
    emotion_model = load_model('models/scripts/e_model/emotion.h5')
    e_prediction = emotion_model.predict(e_processed_sentence)
    
    #print(e_prediction)
    #for prediction in zip(e_prediction)
    #predicted_emotion_index = np.argmax(e_prediction)
    #print(predicted_emotion_index)
    #predicted_emotion = emotion_labels[predicted_emotion_index]
    
    
    # Find the index of the maximum probability for each instance
    predicted_emotion_index = np.argmax(e_prediction, axis=1)
    predicted_emotion_index= np.argmax(predicted_emotion_index)
  # Get the corresponding emotion label
    predicted_emotion = emotion_labels[predicted_emotion_index]
    return str(predicted_emotion)
  
  
print(predict_emotion("i am kidding"))