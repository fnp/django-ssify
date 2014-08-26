from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    'tests.views',

    url(r'^$',
        TemplateView.as_view(template_name='tests/main.html')
        ),
    url(r'^number_zero$',
        TemplateView.as_view(template_name='tests/number_zero.html')
        ),
    url(r'^random_quote$', 'random_quote', name='random_quote'),
    url(r'^quote/(?P<number>.+)$', 'quote', name='quote'),
)
