from django.conf.urls import patterns, url, include
from rest_framework.routers import SimpleRouter

import gallery.views


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from gallery.views import DirectoryViewSet, ImageViewSet, SubdirectoryViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'directories', DirectoryViewSet)
router.register(r'subdirectories', SubdirectoryViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = patterns('',
                       url(r'^deleteImage/(.*)$', gallery.views.delete_image),
                       url(r'^revertImage/(.*)$', gallery.views.revert_image),
                       url(r'^api/', include(router.urls)),
)

