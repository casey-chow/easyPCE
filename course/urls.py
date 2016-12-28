from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       #url(r'^$', pce.views.login_page),
                       url(
                           r'^(?P<subj>\w{3})(?P<num>\w[a-zA-Z0-9_]+)/?$',
                           views.course),
                       # url(r'^easypce/', include('easypce.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       )
