from django.conf.urls import patterns, include, url
import pce.views
import bayesian.views
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^login/?$', pce.views.login_page),
                       url(r'^/?$', pce.views.index),
                       url(r'^index/?$', pce.views.index),
                       url(r'^logout/?$', pce.views.logout),
                       url(r'^search', pce.views.search),
                       url(r'^profs/', include('prof.urls')),
                       url(r'^courses/', include('course.urls')),
                       url(r'^depts/', include('dept.urls')),
                       url(r'^hello/?$', pce.views.hello),
                       url(r'^COS333Final/?$', pce.views.induce),
                       url(r'^test/?$', pce.views.test),
                       url('^timeline/?$', pce.views.timeline),
                       url(r'^favorites', pce.views.favorites),
                       url(r'^editfavorites', pce.views.editfavorites),
                       url(r'^getfavorites', pce.views.getfavorites),
                       url(r'^autotest', pce.views.autotest),
                       url(r'^pop', pce.views.pop),
                       url(r'^rankings/?', bayesian.views.ranking),
                       url(r'^maintenance/?', pce.views.maintenance),
                       #url(r'^profiler/?', include('profiler.urls')),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )

urlpatterns += patterns('django.views.static',
                        # for your site's static CSS, Js, etc.
                        (
                            r'^%s(?P<path>.*)' %
                            settings.STATIC_URL[
                                1:], 'serve', {
                                'document_root': settings.STATIC_ROOT}),
                        (
                            r'^%s(?P<path>.*)' %
                            settings.MEDIA_URL[
                                1:], 'serve', {
                                'document_root': settings.MEDIA_ROOT}),  # for user-added files
                        )
