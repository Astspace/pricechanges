from django.shortcuts import redirect
from django.urls import reverse
from pricechanges import settings


class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)
        if request.path in [reverse(settings.LOGIN_URL), reverse(settings.REGISTER_URL)]:
            return self.get_response(request)
        if not request.user.is_authenticated:
            return redirect(reverse(settings.LOGIN_URL))
        response = self.get_response(request)
        return response
