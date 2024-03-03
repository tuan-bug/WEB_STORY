from django.shortcuts import render
from django.db.models import Q
from app.models import *


def searchProduct(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"

    list_search = {}
    if request.method == "POST":
        key = request.POST["searched"]
        list_search = Story.objects.filter(Q(name__icontains=key) | Q(description__icontains=key))
        print(list_search)
    context = {
        "key": key,
        "list_search": list_search,
        "user_not_login": user_not_login,
        "user_login": user_login,
    }
    return render(request, "app/search.html", context)
