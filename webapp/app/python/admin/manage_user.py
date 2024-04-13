from django.contrib.auth.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
#from forms import CreateUserForm
from app.models import *
from app.python.admin.manage import is_admin
@login_required
@user_passes_test(is_admin)
def manageUser(request):
    users = User.objects.all()  # lay cac damh muc lon
    feedback = Contact.objects.all().count()
    contacts = Contact.objects.all()
    # us = users.staff_status
    form = CreateUserForm()
    print('hahaha: ')

    context = {'users': users,
               'feedback': feedback,
               'contacts': contacts,
               'form': form,
               }
    return render(request, 'admin/users/manageUser.html', context)

def addUser(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid(): # kiểm tra đúng yêu cầu thì lưu cái form đó lại
            form.save()
            messages.success(request, 'Thêm người dùng thành công')
            return redirect('manageUser')
        else:
            messages.error(request, 'Thêm người dùng thất bại')
    else:
        messages.error(request, 'Thêm người dùng thất bại')

    context = {
               'messages': messages,
               }
    return render(request, 'admin/users/addUser.html', context)



def deleteUser(request, id):
    # id = request.GET.get('id', '')  # lấy id khi người dùng vlick vào sản phẩm nào đó
    category = get_object_or_404(User, id=id)
    User.objects.filter(id=id).delete()
    messages.success(request, 'Đã xóa người dùng')
    return redirect('manageUser')
    context ={'category': category,
              'messages': messages,}
    return render(request, 'admin/deleteCategory.html', context)


def editUser(request):
    id = request.GET.get('id', '')  # lấy id khi người dùng vlick vào sản phẩm nào đó
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            print(form)

            messages.success(request, 'Sửa thông tin người dùng thành công!!')
            return redirect('manageUser')  # Chuyển hướng sau khi cập nhật thành công
        else:
            for field in form:
                for error in field.errors:
                    print(f"{field.name}: {error}")
            messages.error(request, 'Sửa thông tin người dùng thất bại')
    else:
        form = CreateUserForm(instance=user)
    context = {'user': user,
               'form': form}
    return render(request, 'admin/users/editUser.html', context)
