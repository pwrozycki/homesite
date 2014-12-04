from django.conf.urls import patterns, url, include
from rest_framework.routers import SimpleRouter

import gallery.views


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from gallery.views import DirectoryViewSet, ImageViewSet, SubdirectoryViewSet, UserViewSet, SessionView, \
    TrashImageView, RevertImageView, CollectionInfoView

router = SimpleRouter(trailing_slash=False)
router.register(r'directories', DirectoryViewSet)
router.register(r'subdirectories', SubdirectoryViewSet)
router.register(r'images', ImageViewSet)
router.register(r'users', UserViewSet)

urlpatterns = patterns('',
                       url(r'^api/images/(?P<pk>[0-9]+)/trash$', TrashImageView.as_view()),
                       url(r'^api/images/(?P<pk>[0-9]+)/revert$', RevertImageView.as_view()),
                       url(r'^api/collectionInfos', CollectionInfoView.as_view()),
                       url(r'^api/session$', SessionView.as_view()),
                       url(r'^api/', include(router.urls)),
)

