from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes

from .models import Font
from .serializers import FontSerializer,FontLookAroundSerializer,FontPublicSerializer, NameUniqueCheckSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

# Create your views here.

@permission_classes([IsAuthenticatedOrReadOnly])
class FontListView(ListCreateAPIView):
    queryset = Font.objects.all().order_by('-created_date')
    serializer_class = FontSerializer

class FontView(RetrieveAPIView):
    queryset = Font.objects.all()
    serializer_class = FontSerializer

class NameUniqueCheck(CreateAPIView):
    serializer_class = NameUniqueCheckSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            return Response(data={'detail':'You can use this Name :)'}, status=status.HTTP_200_OK)
        else:
            detail = dict()
            detail['detail'] = 'This Name is alreay Used :('
            return Response(data=detail, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fontview(request):
    queryset = Font.objects.filter(public=True)
    name = request.query_params.get('name')
    if name is not None:
        queryset = queryset.get(name=name, public=True)
        serializer = FontLookAroundSerializer(queryset, context={'request':request}).data
    else:
        serializer = FontLookAroundSerializer(queryset,many=True, context={'request':request}).data
    return Response(serializer)