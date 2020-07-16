from django.contrib import admin
from django.urls import path, reverse_lazy
from django.conf.urls import include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
