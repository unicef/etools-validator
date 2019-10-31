from django.conf.urls import url

from .views import DemoCreateView, DemoUpdateNonSerializedView, DemoUpdateView

app_name = "sample"

urlpatterns = (
    url(r'^create/$', view=DemoCreateView.as_view(), name='create'),
    url(
        r'^update/(?P<pk>\d+)/$',
        view=DemoUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^update-non-serialized/(?P<pk>\d+)/$',
        view=DemoUpdateNonSerializedView.as_view(),
        name='update-non-serialized'
    ),
)
