from django import template
from ssify import ssi_variable
from tests.views import QUOTES

register = template.Library()


@ssi_variable(register)
def random_number(request, limit):
    # Guaranteed to be random as of XKCD#221
    return min(limit - 1, 4)


@ssi_variable(register)
def number_of_quotes(request):
    return len(QUOTES)


@ssi_variable(register)
def quote_len_odd(request, which):
    return bool(len(QUOTES[which]) % 1)
