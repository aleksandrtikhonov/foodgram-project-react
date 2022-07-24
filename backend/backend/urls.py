from django.contrib import admin
from django.urls import include, path


admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path("api/", include("users.urls")),
    path("api/", include("recipes.urls")),
    path("admin/", admin.site.urls),
]
