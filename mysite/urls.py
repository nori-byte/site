from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include
from django.views.generic import RedirectView
from django.views.decorators.cache import never_cache
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('polls/', include('polls.urls')),
    path('', RedirectView.as_view(url='polls/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)