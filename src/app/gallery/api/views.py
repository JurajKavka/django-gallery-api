import logging
import os
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from ..models import Gallery, Image
from .serializers import (
    GallerySerializer, GalleryDetailSerializer, ImageUploadSerializer,
    ImagePreviewSerializer
)


logger = logging.getLogger(__name__)


def get_gallery(path):
    gallery = None
    try:
        gallery = Gallery.objects.get(name=path)
    except Gallery.DoesNotExist:
        raise NotFound()
    except Exception:
        raise APIException()

    return gallery


def get_image(gallery_path, image_path):
    image = None
    try:
        image = Image.objects.get(gallery__name=gallery_path,
                                  path=image_path)
    except Image.DoesNotExist:
        raise NotFound()
    except Exception as e:
        logger.error(e)
        raise APIException()

    return image


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def gallery_list_view(request):

    if request.method == 'GET':
        galleries = Gallery.objects.all()
        serializer = GallerySerializer(galleries, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GallerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors.get('name')
        if len(errors) == 1 and errors[0].code == 'unique':
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'POST'])
@authentication_classes([])
@permission_classes([])
def gallery_detail_view(request, path):

    if request.method == 'GET':
        gallery = get_gallery(path)
        serializer = GalleryDetailSerializer(gallery)
        return Response(serializer.data)

    elif request.method == 'POST':

        success_response = {
            'uploaded': [],
            'errors': []
        }

        # find galery
        gallery = get_gallery(path)

        # in case of no files in body, return bad request
        if not request.FILES:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        try:
            for key, val in request.FILES.items():
                image = {
                    'gallery': gallery.pk,
                    'path': val.name,
                    'name': os.path.splitext(val.name)[0],
                    'file': val,
                }
                serializer = ImageUploadSerializer(data=image)
                if serializer.is_valid():
                    img = serializer.save()
                    success_response['uploaded'].append({
                        'name': img.name,
                        'path': img.path,
                        'fullpath': img.fullpath,
                        'modified': img.modified,
                    })
                else:
                    success_response['errors'].append({
                        'name': val.name,
                        'error': serializer.errors
                    })

            return Response(success_response, status=status.HTTP_200_OK)
        except Exception:
            raise APIException()

    elif request.method == 'DELETE':
        gallery = get_gallery(path)
        gallery.delete()
        return Response(None, status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
@authentication_classes([])
@permission_classes([])
def image_detail_view(request, gallery_path, image_path):

    if request.method == 'GET':
        logger.debug('GET Image {}/{}'.format(gallery_path, image_path))
        image = get_image(gallery_path, image_path)
        return FileResponse(image.file.file)

    elif request.method == 'DELETE':
        logger.debug('DELETE Image {}/{}'.format(gallery_path, image_path))
        image = get_image(gallery_path, image_path)
        image.delete()

    return Response(None, status=status.HTTP_200_OK)


@api_view(['GET'])
def image_preview_view(request, x_size, y_size, gallery_path, image_path):

    if request.method == 'GET':
        logger.debug(('GET Image preview x={x_size}, y={y_size}, path={gallery_path}/{image_path}'
                      .format(x_size=x_size, y_size=y_size, gallery_path=gallery_path,
                              image_path=image_path)))

        serializer = ImagePreviewSerializer(data={'x_size': x_size, 'y_size': y_size})
        if serializer.is_valid():
            image = get_image(gallery_path, image_path)
            # resize image
            try:
                resized_image = image.get_thumbnail(x_size, y_size)
            except Exception as e:
                logger.error(e)
                raise APIException()

            return FileResponse(resized_image)

        return Response(serializer.errors, status=status.HTTP_200_OK)
