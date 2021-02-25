from rest_framework.response import Response
from rest_framework.decorators import api_view

from main.models import Poster
from .serializers import PosterSerializer

# Конкретное объявление
from rest_framework.generics import RetrieveAPIView
from .serializers import PosterDetailSerializer

# Комменатрии
from rest_framework.decorators import permission_classes
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from main.models import Comment
from .serializers import CommentSerializer

# Все объявления
@api_view(['GET'])
def posters(request):
    if request.method == 'GET':
        posters = Poster.objects.filter(is_active=True)[:10]
        serializer = PosterSerializer(posters, many=True)
        return Response(serializer.data)

# Полный вывод информации
class PosterDetailView(RetrieveAPIView):
    queryset = Poster.objects.filter(is_active=True)
    serializer_class = PosterDetailSerializer

@api_view(['GET', 'POST'])
# Класс разграничения доступа -  IsAuthenticatedOrReadOnly
@permission_classes((IsAuthenticatedOrReadOnly,))
def comments(request, pk):
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    else:
        comments = Comment.objects.filter(is_active=True, poster=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
