from django.shortcuts import render


def tester(request):
    return render(
        request,
        'core/index.html',
        {'message': 'Request received!'}
    )
