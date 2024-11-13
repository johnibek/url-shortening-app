from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from .models import UrlModel
from .serializers import UrlModelSerializer, UrlStatsSerializer


@api_view(['GET'])
def home(request):
    return Response({'message': "Hello world", 'headers': request.headers})


@api_view(['POST'])
def create_short_url(request):
    new_shortened_url = UrlModelSerializer(data=request.data)
    url = request.data['url']

    if UrlModel.objects.filter(url=url).exists():
        return Response({'message': 'This url has already been shortened. Short code: {}'.format(UrlModel.objects.get(url=url).short_code)}, status=status.HTTP_400_BAD_REQUEST)

    if new_shortened_url.is_valid():
        new_shortened_url.save()
        return Response(new_shortened_url.data, status=status.HTTP_201_CREATED)
    
    return Response(new_shortened_url.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
def get_update_delete_short_url(request, short_code):
    if request.method == 'GET':
        try:
            url_obj = UrlModel.objects.get(short_code=short_code)
        except UrlModel.DoesNotExist:
            return Response({'message': 'short code not found'}, status=status.HTTP_404_NOT_FOUND)
        # url_obj = get_object_or_404(UrlModel, short_code=short_code)

        serializer = UrlModelSerializer(url_obj, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


    if request.method == 'PUT':
        url_obj = get_object_or_404(UrlModel, short_code=short_code)
        serializer = UrlModelSerializer(instance=url_obj, data=request.data, many=False)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


    if request.method == 'DELETE':
        try:
            url_obj = UrlModel.objects.get(short_code=short_code)
        except UrlModel.DoesNotExist:
            return Response({'message': 'short code not found'}, status=status.HTTP_404_NOT_FOUND)
        
        url_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def redirect_url(request, short_code):
    """
    Number of times accessed.
    How many times short url has been redirected to original one.
    """
    url_obj = get_object_or_404(UrlModel, short_code=short_code)
    url_obj.access_count += 1
    url_obj.save(update_fields=['access_count'])
    return redirect(url_obj.url)


@api_view(['GET'])
def get_url_stats(request, short_code):
    url_obj = get_object_or_404(UrlModel, short_code=short_code)
    serializer = UrlStatsSerializer(url_obj, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)



