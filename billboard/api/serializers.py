from rest_framework import serializers

from main.models import Poster
from main.models import Comment

class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = ('id', 'title', 'content', 'price', 'created_at')

class PosterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = ('id', 'title', 'content', 'price', 'created_at', 'contacts', 'image')

# Сериализатор выдает нужную для просмотра комменатрия информацию
# + ключ (poster), чтобы можно было оставить комменатрий
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('poster', 'author', 'content', 'created_at')