from django.conf.urls import patterns, include, url
import pce.devviews
import bayesian.views
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^/?$', pce.devviews.index),
                       url(r'^index/?$', pce.devviews.index),
                       url(r'^search', pce.devviews.search),
                       url(r'^profs/', include('prof.devurls')),
                       url(r'^courses/', include('course.devurls')),
                       url(r'^depts/', include('dept.devurls')),
                       url(r'^favorites', pce.devviews.favorites),
                       url(r'^editfavorites', pce.devviews.editfavorites),
                       url(r'^getfavorites', pce.devviews.getfavorites),
                       url(r'^rankings', bayesian.views.ranking),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       )

# urlpatterns += patterns('django.views.static',
#        ( r'^%s(?P<path>.*)' % settings.STATIC_URL[1:], 'serve', {'document_root': settings.STA#TIC_R
# OOT} ), #for your site's static CSS, Js, etc.
#        ( r'^%s(?P<path>.*)' % settings.MEDIA_URL[1:], 'serve', {'document_root': settings.MEDIA_ROO
# T} ), #for user-added files
#)
