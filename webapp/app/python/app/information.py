from django.shortcuts import render, get_object_or_404, redirect

from app.models import *
from app.python.app.base import show_manage


def Information(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"

    context = {'user_login': user_login,
               'user_not_login': user_not_login,
               }
    return render(request, 'app/information.html', context)


def edit_information(request):
    slide_hidden = "none"
    fixed_height = "20px"
    check_staff = request.user
    if check_staff.is_staff:
        print('admin')
        show_manage = 'show'
    else:
        print('not admin')
        show_manage = 'none'

    context = {'slide_hidden': slide_hidden,
               'fixed_height': fixed_height,

               }
    return render(request, 'app/editInformation.html', context)
