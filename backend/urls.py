from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from django.views.decorators.cache import never_cache
import os
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # User-specific backend routes
    path('clients/', include('clients.urls')),  # Client-specific backend routes

    # Frontend rendering
    path('', never_cache(TemplateView.as_view(template_name='portal.html')), name='portal'),
    re_path(r'^user/(?P<path>.*)$', never_cache(TemplateView.as_view(template_name='users_index.html')), name='user_index'),
    re_path(r'^client/(?P<path>.*)$', never_cache(TemplateView.as_view(template_name='clients_index.html')), name='client_index'),
    # Serving media files
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
