from django.conf.urls import url

from demo.sample.views import DemoCreateView, DemoUpdateView


urlpatterns = (
    url(r'^create/$', view=DemoCreateView.as_view(), name='create'),
    url(
        r'^update/(?P<pk>\d+)/$',
        view=DemoUpdateView.as_view(),
        name='update'
    ),
)
