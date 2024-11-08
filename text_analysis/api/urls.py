from django.urls import path
from .views import *

urlpatterns = [
    path('summarize/', Summarizer.as_view(), name='summarize'),
    path('keywords/', KeywordExtractor.as_view(), name='keywords'),
    path('sentiment/', SentimentAnalyzer.as_view(), name='sentiment'),
    path('mds/', MDSVisualizer.as_view(), name='mds'),
    path('search/', SearchText.as_view(), name='search'),
    path('categorize/', CategorizeText.as_view(), name='categorize'),
]
