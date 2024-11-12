import nltk
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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import TextInputSerializer

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
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Summarize the provided text using LSA.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to summarize"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Text summarized successfully",
                examples={"application/json": {"summary": "Summarized text here"}},
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if punkt is downloaded, if not, download it
        print(nltk.data.path)

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 2)  # Summarize to 2 sentences
        summary_text = ' '.join([str(s) for s in summary])
        return JsonResponse({"summary": summary_text})

# KEYWORD EXTRACTION VIEW (using Rake-NLTK)
class KeywordExtractor(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Extract keywords from the provided text using Rake.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to extract keywords from"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Keywords extracted successfully",
                examples={"application/json": {"keywords": ["keyword1", "keyword2"]}},
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
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
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Analyze sentiment of the provided text using VADER and TextBlob.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to analyze sentiment"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Sentiment analyzed successfully",
                examples={
                    "application/json": {
                        "sentiment_vader": {"compound": 0.5, "neg": 0.0, "neu": 0.5, "pos": 0.5},
                        "sentiment_textblob": "(polarity, subjectivity)"
                    }
                },
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
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
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Generate MDS visualization for the provided text.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to visualize"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="MDS visualization generated successfully",
                examples={"application/json": {"message": "MDS visualization generated"}},
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
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
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Search for text in the index using Whoosh.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to search"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Search completed successfully",
                examples={"application/json": {"search_results": ["result1", "result2"]}},
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        qp = QueryParser("communicate", ix.schema)
        q = qp.parse(text)
        with ix.searcher() as searcher:
            results = searcher.search(q)
            result_texts = [r['content'] for r in results]
        return JsonResponse({"search_results": result_texts})

# CATEGORIZATION VIEW (simple categorization)
class CategorizeText(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TextInputSerializer

    @swagger_auto_schema(
        tags=["Text Analysis"],
        operation_description="Categorize the provided text into predefined categories.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Text to categorize"
                ),
            },
            required=["text"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Text categorized successfully",
                examples={"application/json": {"category": "technology"}},
            ),
            status.HTTP_400_BAD_REQUEST: "Text is required",
        },
    )
    def create(self, request, *args, **kwargs):
        text = request.data.get('text')
        if not text:
            return JsonResponse({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        category = simple_categorize(text)
        return JsonResponse({"category": category})