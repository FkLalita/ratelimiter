from django.shortcuts import render
from .mymiddleware import rate_limit


@rate_limit(limit=9, window=22)
def tester(request):
    return render(request, 'core/index.html')
