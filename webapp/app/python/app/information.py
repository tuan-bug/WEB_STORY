from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404

from app.models import *
from app.python.app.base import show_manage


def Information(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    form = CustomerForm()
    print(profile)
    information = request.user
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)  # Không lưu ngay vào cơ sở dữ liệu
            if request.user.is_authenticated:  # Kiểm tra nếu người dùng đăng nhập
                instance.user = request.user  # Gán người dùng cho trường user
            instance.save()  # Lưu thông tin vào cơ sở dữ liệu
            return redirect('information')
    context = {'user_login': user_login,
               'user_not_login': user_not_login,
               'form': form,
               'profile': profile,
               'information': information,
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
