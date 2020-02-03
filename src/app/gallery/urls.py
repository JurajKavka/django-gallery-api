from django.urls import path
from .api import (
    gallery_list_view, gallery_detail_view, image_detail_view,
    image_preview_view
)
from rest_framework.schemas import get_schema_view

app_name = 'gallery'

urlpatterns = [
    # Gallery list endpoint: GET, POST
    path('gallery/', gallery_list_view),

    # Gallery detail denpoint: GET, DELETE, POST
    path('gallery/<str:path>', gallery_detail_view),

    # Image detail endpoint: DELETE, GET
    path('gallery/<str:gallery_path>/<str:image_path>', image_detail_view),

    # Image preview (request for thumbnails): GET
    path('images/<int:x_size>x<int:y_size>/<str:gallery_path>/<str:image_path>/',
         image_preview_view),

    path('', get_schema_view(
        title="Gallery API",
        description="Simple API for the image gallery.",
        version="1.0.0"
    ), name='openapi-schema'),
]
