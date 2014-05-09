from django.conf.urls import patterns, url
import gallery.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^browse/(.*)$', gallery.views.browse),
                       url(r'^listdir/(.*)$', gallery.views.list_dir, name='listdir'),
)

