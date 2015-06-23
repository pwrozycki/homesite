from django.conf.urls import patterns, url, include
from rest_framework.routers import SimpleRouter


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from gallery.views import DirectoryViewSet, ImageViewSet, SubdirectoryViewSet, UserViewSet, SessionView, \
    CollectionInfoView, ImageGroupView, FileMoveAPIView

router = SimpleRouter(trailing_slash=False)
router.register(r'directories', DirectoryViewSet)
router.register(r'subdirectories', SubdirectoryViewSet)
router.register(r'images', ImageViewSet)
router.register(r'users', UserViewSet)

urlpatterns = patterns('',
                       url(r'^api/files/(?P<pk>[0-9]+)/move$', FileMoveAPIView.as_view()),
                       url(r'^api/imageGroups', ImageGroupView.as_view()),
                       url(r'^api/collectionInfos', CollectionInfoView.as_view()),
                       url(r'^api/session$', SessionView.as_view()),
                       url(r'^api/', include(router.urls)),
)

