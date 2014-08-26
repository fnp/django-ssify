from django.shortcuts import render
from ssify import ssi_included, ssi_expect, SsiVariable as V


@ssi_included(use_lang=False, get_ssi_vars=lambda number: [
    ('test_tags.number_of_quotes',),
    ('test_tags.quote_len_odd', (ssi_expect(number, int),))
])
def quote(request, number):
    number = int(number)
    return render(request, 'tests/quote.html', {
        'number': number,
        'quote': QUOTES[number]
    })


@ssi_included(use_lang=False, get_ssi_vars=lambda: (
    lambda number: [number] + quote.get_ssi_vars(number))(
        number=V('test_tags.random_number', [V('test_tags.number_of_quotes')])
    ))
def random_quote(request):
    """
    This view is purposely overcomplicated to test interdependencies
    between SSI variables and SSI includes.

    It finds number of quotes and sets that in an SSI variable,
    then uses that to set a random quote number in a second variable,
    then sets a third saying if the length of the selected quote is odd.

    """
    return render(request, 'tests/random_quote.html')


# Nothing interesting here.
def _quotes():
    import sys
    import cStringIO
    stdout_backup = sys.stdout
    sys.stdout = cStringIO.StringIO()
    import this
    this_string = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = stdout_backup
    return this_string.split('\n')

QUOTES = _quotes()
