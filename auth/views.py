from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth import authenticate, login


class LoginView(View):
    http_method_names = ['get', 'post']

    def get(self, request) -> render:
        return render(request, 'auth/auth.html')

    def post(self, request) -> render:
        user = authenticate(request, username=request.POST['login'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'auth/auth.html', context={'error': 'user not found'})
