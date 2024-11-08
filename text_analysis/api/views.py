from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .serializer import (
    TextInputSerializer,
    KeywordExtractionSerializer,
    TextsInputSerializer,
    SearchInputSerializer,
    CategoryInputSerializer,
    CustomQuerySerializer,
)
from .utils import (
    text_summarization,
    keyword_extraction,
    sentiment_analysis,
    tsne_visualization,
    search_texts,
    categorize_text,
    custom_query,
)

class SummarizeView(APIView):
    def post(self, request):
        serializer = TextInputSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            ratio = serializer.validated_data.get('ratio', 0.2)
            summary = text_summarization(text, ratio)
            return Response({"summary": summary})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KeywordsView(APIView):
    def post(self, request):
        serializer = KeywordExtractionSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            top_n = serializer.validated_data.get('top_n', 5)
            keywords = keyword_extraction(text, top_n)
            return Response({"keywords": keywords.tolist()})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SentimentView(APIView):
    def post(self, request):
        serializer = TextInputSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            sentiment = sentiment_analysis(text)
            return Response(sentiment)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VisualizeView(APIView):
    def post(self, request):
        serializer = TextsInputSerializer(data=request.data)
        if serializer.is_valid():
            texts = serializer.validated_data['texts']
            visualization = tsne_visualization(texts)
            return HttpResponse(visualization, content_type="image/png")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchView(APIView):
    def post(self, request):
        serializer = SearchInputSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            texts = serializer.validated_data['texts']
            results = search_texts(query, texts)
            return Response({"results": [{"text": text, "similarity": float(sim)} for text, sim in results]})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategorizeView(APIView):
    def post(self, request):
        serializer = CategoryInputSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            categories = serializer.validated_data['categories']
            category = categorize_text(text, categories)
            return Response({"category": category})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomQueryView(APIView):
    def post(self, request):
        serializer = CustomQuerySerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            query_function = serializer.validated_data['query_function']
            # CAUTION: Executing arbitrary code can be dangerous. Implement proper security measures.
            result = custom_query(text, eval(query_function))
            return Response({"result": result})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)