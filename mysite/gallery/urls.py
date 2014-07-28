from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import gallery.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from gallery.views import DirectoryViewSet, ImageViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'directories', DirectoryViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = patterns('',
                       url(r'^browse/(.*)$', gallery.views.browse),
                       url(r'^listdir/(.*)$', gallery.views.list_dir, name='listdir'),
                       url(r'^deleteImage/(.*)$', gallery.views.delete_image),
                       url(r'^revertImage/(.*)$', gallery.views.revert_image),
                       url(r'^api/', include(router.urls)),
)

