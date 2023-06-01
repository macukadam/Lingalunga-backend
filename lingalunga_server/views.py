from django.shortcuts import render
from rest_framework import permissions, views


class WelcomeView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'index2.html')


class Privacy(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'privacy_policy.html')
