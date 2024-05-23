from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from app.models import *
from app.python.app.base import show_manage


def Information(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    profile = None
    form = CustomerForm()
    information = request.user
    password_change_form = ChangePasswordForm()  # Tạo form đổi mật khẩu
    if request.method == 'POST':
        # Kiểm tra nếu là yêu cầu đổi mật khẩu
        if 'change_password' in request.POST:
            password_change_form = ChangePasswordForm(request.POST)
            if password_change_form.is_valid():
                user = request.user
                new_password = password_change_form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Cập nhật session để tránh đăng nhập lại
                print("LOLLLLL")
                print(request.session)
                return redirect('information')
        else:
            form = CustomerForm(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                if request.user.is_authenticated:
                    instance.user = request.user
                instance.save()
                return redirect('information')
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()
    context = {
        'user_login': user_login,
        'user_not_login': user_not_login,
        'form': form,
        'profile': profile,
        'information': information,
        'password_change_form': password_change_form,  # Truyền form đổi mật khẩu vào context
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
