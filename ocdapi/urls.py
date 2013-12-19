<<<<<<< HEAD
from django.conf.urls.defaults import patterns, include
=======
from django.conf.urls import patterns, include
>>>>>>> 9fd763d83504c68601273d3cd0a90c662ddf0d77

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
   ('', include('boundaries.urls')),
   ('', include('imago.urls')),
   ('', include('locksmith.mongoauth.urls')),
   #(r'^admin/', include(admin.site.urls)),
)
