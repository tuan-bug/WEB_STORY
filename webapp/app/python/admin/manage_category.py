from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from app.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from app.python.admin.manage import is_admin


@login_required
@user_passes_test(is_admin)
def manageCategory(request):
    form = AddCategory()
    categories = Genre.objects.all().order_by('name')  # lay cac damh muc lon
    paginator = Paginator(categories, 8)
    page_number = request.GET.get('page')
    page_categories = paginator.get_page(page_number)
    feedback = Contact.objects.all().count()
    contacts = Contact.objects.all()
    context ={'categories': page_categories,
              'feedback': feedback,
              'contacts': contacts,
              'form': form,
              }
    return render(request, 'admin/category/managementCategory.html', context)

# def addCategory(request):
#     if request.method == 'POST':
#         form = AddCategory(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Thêm danh mục thành công')
#             return redirect('manageCategory')
#         else:
#             return render(request, 'admin/category/manageCategory.html', {'form': form})
#             #messages.error(request, 'Thêm danh mục thất bại. Vui lòng kiểm tra lại thông tin.')
#     else:
#         messages.error(request, 'Thêm danh mục thất bại. Vui lòng kiểm tra lại thông tin.')
#         #form = AddCategory()
#     context = {'form': form}
#     return render(request, 'admin/category/addCategory.html', context)


def addCategory(request):
    if request.method == 'POST':
        form = AddCategory(request.POST)
        if form.is_valid():
            genre = form.save()
            messages.success(request, 'Thêm danh mục thành công')
            return JsonResponse({'success': "Thêm danh mục thành công", 'genre_name': genre.name})
        else:
            errors = form.errors  # Lấy ra lỗi của trường 'name'
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': errors}, status=405)

     

def editCategory(request):
    id = request.GET.get('id', '')  # Lấy id khi người dùng click vào sản phẩm nào đó
    category = get_object_or_404(Genre, id=id)
    
    if request.method == 'POST':
        form = AddCategory(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sửa danh mục thành công')
            return JsonResponse({'success': True})
        else:
            errors = form.errors  # Lấy ra tất cả các lỗi của biểu mẫu
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        return JsonResponse({'success': False, 'errors': errors}, status=405)

    # form = AddCategory(instance=category,
    #                    initial={'sub_category': category.sub_category,
    #                             'is_sub': category.is_sub,
    #                             'name': category.name,
    #                             'slug': category.slug,
    #                             'messages': messages,
    #                             })

    # context = {'category': category,
    #            'form': form}
    # return render(request, 'admin/category/editCategory.html', context)


def deleteCategory(request, id):
    # id = request.GET.get('id', '')  # lấy id khi người dùng vlick vào sản phẩm nào đó
    category = get_object_or_404(Genre, id=id)
    Genre.objects.filter(id=id).delete()
    messages.success(request, 'Đã xóa danh mục')
    return redirect('manageCategory')
    context ={'category': category,
              'messages': messages,}
    return render(request, 'admin/deleteCategory.html', context)