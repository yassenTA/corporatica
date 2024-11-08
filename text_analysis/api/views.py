from django.http import JsonResponse
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from rake_nltk import Rake
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import whoosh.index as index
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os
import numpy as np
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# Initialize models and components
sia = SentimentIntensityAnalyzer()

# Setup Whoosh schema and index
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
schema = Schema(content=TEXT)
ix = index.create_in("indexdir", schema)

# Function for simple text categorization
def simple_categorize(text):
    categories = {
        "technology": ["software", "computer", "tech", "AI", "robotics"],
        "sports": ["football", "basketball", "cricket", "soccer", "athlete"]
        # Add more categories and keywords as needed
    }
    category_scores = {cat: sum([text.lower().count(word) for word in words]) for cat, words in categories.items()}
    return max(category_scores, key=category_scores.get)

# TEXT SUMMARIZATION VIEW (using Sumy)
class Summarizer(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 2)  # Summarize to 2 sentences
        summary_text = ' '.join([str(s) for s in summary])
        return JsonResponse({"summary": summary_text})

# KEYWORD EXTRACTION VIEW (using Rake-NLTK)
class KeywordExtractor(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        r = Rake()  # Uses stopwords from NLTK and extracts phrases
        r.extract_keywords_from_text(text)
        keywords = r.get_ranked_phrases()
        return JsonResponse({"keywords": keywords})

# SENTIMENT ANALYSIS VIEW (VADER and TextBlob)
class SentimentAnalyzer(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        sentiment_vader = sia.polarity_scores(text)
        sentiment_textblob = TextBlob(text).sentiment
        return JsonResponse({"sentiment_vader": sentiment_vader, "sentiment_textblob": str(sentiment_textblob)})

# MDS VISUALIZATION VIEW (alternative to T-SNE)
class MDSVisualizer(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):

        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        # Assume text is processed into vectors; generate random ones for this demo
        vectors = np.random.rand(len(text), 100)  # Fake 100-dimensional vectors
        mds = MDS(n_components=2)
        mds_results = mds.fit_transform(vectors)
        plt.scatter(mds_results[:, 0], mds_results[:, 1])
        plt.title("MDS Visualization")
        plt.savefig("mds_plot.png")
        return JsonResponse({"message": "MDS visualization generated"})

# SEARCH VIEW (using Whoosh)
class SearchText(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        qp = QueryParser("content", ix.schema)
        q = qp.parse(text)
        with ix.searcher() as searcher:
            results = searcher.search(q)
            result_texts = [r['content'] for r in results]
        return JsonResponse({"search_results": result_texts})

# CATEGORIZATION VIEW (simple categorization)
class CategorizeText(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):

        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        category = simple_categorize(text)
        return JsonResponse({"category": category})
