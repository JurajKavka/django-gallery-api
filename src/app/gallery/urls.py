from django.urls import path
from rest_framework.schemas import get_schema_view
from .api import (
    gallery_list_view, gallery_detail_view, image_detail_view,
    image_preview_view
)
from .views import FacebookRedirectView

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

    # redirect from facebook auth api
    path('token/',
         FacebookRedirectView.as_view(
             template_name='gallery/facebook_redirect.html'
         )),

    path('', get_schema_view(
        title="Gallery API",
        description="Simple API for the image gallery.",
        version="1.0.0"
    ), name='openapi-schema'),
]
