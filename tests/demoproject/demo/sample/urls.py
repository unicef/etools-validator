from django.urls import re_path

from .views import DemoCreateView, DemoUpdateNonSerializedView, DemoUpdateView

app_name = "sample"

urlpatterns = (
    re_path(r'^create/$', view=DemoCreateView.as_view(), name='create'),
    re_path(
        r'^update/(?P<pk>\d+)/$',
        view=DemoUpdateView.as_view(),
        name='update'
    ),
    re_path(
        r'^update-non-serialized/(?P<pk>\d+)/$',
        view=DemoUpdateNonSerializedView.as_view(),
        name='update-non-serialized'
    ),
)
