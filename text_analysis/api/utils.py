import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from nltk.corpus import stopwords
from gensim.summarization import summarize
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
import io
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")
nltk.download("stopwords")

# Load Spacy English model
nlp = spacy.load("en_core_web_sm")

def text_summarization(text, ratio=0.2):
    """Summarizes the text using Gensim's summarize."""
    return summarize(text, ratio=ratio)

def keyword_extraction(text, top_n=5):
    """Extracts top-n keywords from the text using TF-IDF."""
    doc = nlp(text)
    vectorizer = TfidfVectorizer(max_features=top_n, stop_words="english")
    X = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()
    return keywords

def sentiment_analysis(text):
    """Performs basic sentiment analysis using TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    return {"polarity": polarity, "subjectivity": subjectivity}

def tsne_visualization(texts):
    """Generates a T-SNE visualization based on text input."""
    vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
    X = vectorizer.fit_transform(texts).toarray()
    tsne = TSNE(n_components=2)
    tsne_results = tsne.fit_transform(X)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=tsne_results[:, 0], y=tsne_results[:, 1])
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf

def search_texts(query, texts):
    """Search for relevant texts based on the query."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([query] + texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    related_docs_indices = cosine_similarities.argsort()[:-6:-1]
    return [(texts[i], cosine_similarities[i]) for i in related_docs_indices]

def categorize_text(text, categories):
    """Categorize text into predefined categories."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([text] + categories)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    category_index = cosine_similarities.argmax()
    return categories[category_index]

def custom_query(text, query_function):
    """Execute a custom user-defined query on the text."""
    return query_function(text)