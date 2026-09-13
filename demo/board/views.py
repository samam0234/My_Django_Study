from django.http import HttpResponse


def hello(request):
    return HttpResponse("<h1>Hello, Django!</h1><p>board 앱이 정상적으로 연결되었습니다.</p>")
