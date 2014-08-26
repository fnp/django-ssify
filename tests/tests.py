from django.test import Client, TestCase
from django.test.utils import override_settings


class SsifyTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_zero(self):
        self.assertEqual(
            self.client.get('/number_zero').content,
            "<!--#set var='ve023a08d2c2075118e25b5f4339438dc' value='0'-->"
            "<!--#echo var='ve023a08d2c2075118e25b5f4339438dc' "
            "encoding='none'-->"
        )

    def test_single_quote(self):
        self.assertEqual(
            self.client.get('/quote/3').content.strip(),
            """Explicit is better than implicit.
Line 3 of <!--#echo var='va50d914691ecf9b421c680d93ba1263e' encoding='none'-->
<!--#if expr='${vddc386e120ab274a980ab67384391a1a}'-->Odd number of characters.
<!--#else-->Even number of characters.
<!--#endif-->"""
        )

    def test_random_quote(self):
        self.assertEqual(
            self.client.get('/').content.strip(),
            "<!--#set var='vda0df841702ea993b36d101460264364' value='4'-->"
            "<!--#set var='va50d914691ecf9b421c680d93ba1263e' value='22'-->"
            "<!--#set var='vafe010f2e683908fee32c48d01bb2650' value=''-->"
            "\n\n<!--#include file='/random_quote'-->"
        )

        # Do it again, this time from cache.
        self.assertEqual(
            self.client.get('/').content.strip(),
            "<!--#set var='vda0df841702ea993b36d101460264364' value='4'-->"
            "<!--#set var='va50d914691ecf9b421c680d93ba1263e' value='22'-->"
            "<!--#set var='vafe010f2e683908fee32c48d01bb2650' value=''-->"
            "\n\n<!--#include file='/random_quote'-->"
        )
        self.assertEqual(
            self.client.get('/random_quote').content.strip(),
            "<!--#include "
            "file='/quote/${vda0df841702ea993b36d101460264364}'-->"
        )

    @override_settings(SSIFY_DEBUG=True)
    def test_debug_render_random_quote(self):
        """Renders the complete view using the DebugSsiMiddleware."""
        response = self.client.get('/')
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        self.assertEqual(
            response.content.strip(),
            """Simple is better than complex.
Line 4 of 22
Even number of characters."""
        )
