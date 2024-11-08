from rest_framework import serializers

class TextInputSerializer(serializers.Serializer):
    text = serializers.CharField()
    ratio = serializers.FloatField(required=False, default=0.2)

class KeywordExtractionSerializer(serializers.Serializer):
    text = serializers.CharField()
    top_n = serializers.IntegerField(required=False, default=5)

class TextsInputSerializer(serializers.Serializer):
    texts = serializers.ListField(child=serializers.CharField())

class SearchInputSerializer(serializers.Serializer):
    query = serializers.CharField()
    texts = serializers.ListField(child=serializers.CharField())

class CategoryInputSerializer(serializers.Serializer):
    text = serializers.CharField()
    categories = serializers.ListField(child=serializers.CharField())

class CustomQuerySerializer(serializers.Serializer):
    text = serializers.CharField()
    query_function = serializers.CharField()