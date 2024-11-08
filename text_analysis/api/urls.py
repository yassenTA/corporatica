from django.urls import path
from .views import (
    SummarizeView,
    KeywordsView,
    SentimentView,
    VisualizeView,
    SearchView,
    CategorizeView,
    CustomQueryView,
)

urlpatterns = [
    path('summarize/', SummarizeView.as_view(), name='summarize'),
    path('keywords/', KeywordsView.as_view(), name='keywords'),
    path('sentiment/', SentimentView.as_view(), name='sentiment'),
    path('visualize/', VisualizeView.as_view(), name='visualize'),
    path('search/', SearchView.as_view(), name='search'),
    path('categorize/', CategorizeView.as_view(), name='categorize'),
    path('custom_query/', CustomQueryView.as_view(), name='custom_query'),
]