import logging
from rest_framework import serializers
from ..models import Gallery, Image


logger = logging.getLogger(__name__)


class ImageSerializer(serializers.ModelSerializer):
    """
    REST API serializer for the Image model.
    """
    class Meta:
        model = Image
        fields = ['path', 'fullpath', 'name', 'modified']


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['gallery', 'path', 'fullpath', 'name', 'file']


class GallerySerializer(serializers.ModelSerializer):
    """
    REST API serializer for the Gallery model.
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ['path', 'name', 'image']

    def get_image(self, obj):
        result = None
        image = obj.image_set.all().first()
        if image:
            serializer = ImageSerializer(image)
            result = serializer.data
        return result

    def _remove_image_from_fields(self, repre):
        if repre['image'] is None:
            repre.pop('image')

    def to_representation(self, obj):
        result = super(GallerySerializer, self).to_representation(obj)
        self._remove_image_from_fields(result)
        return result

    def is_valid(self, raise_exception=False):
        result = super(GallerySerializer, self).is_valid(raise_exception)
        return result


class GalleryDetailSerializer(serializers.ModelSerializer):

    # i don't want to rename default `realtion_name` to be
    # consistent with standard Django ORM
    images = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ['path', 'name', 'images']

    def get_images(self, obj):
        image = obj.image_set.all()
        serializer = ImageSerializer(image, many=True)
        return serializer.data


class ImagePreviewSerializer(serializers.Serializer):
    x_size = serializers.IntegerField(min_value=0)
    y_size = serializers.IntegerField(min_value=0)

    def validate(self, data):

        if data['x_size'] + data['y_size'] == 0:
            raise serializers.ValidationError('Both sizes can\'t be zero!')

        return data
