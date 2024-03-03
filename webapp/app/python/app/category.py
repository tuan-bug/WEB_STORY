from django.shortcuts import render

from app.models import *
from django.db.models import Q


def category(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    categories = Genre.objects.all()
    stories = Story.objects.all()

    context ={
          'user_login': user_login,
          'user_not_login': user_not_login,
          'categories': categories,
          'stories': stories,
    }
    return render(request, "app/category.html", context)
