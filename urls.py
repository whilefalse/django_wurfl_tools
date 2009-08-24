from django.conf.urls.defaults import *
import views

urlpatterns = patterns(
    '',
    url(r'^test/$', views.test, name="test"),

)
