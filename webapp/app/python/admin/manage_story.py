from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage

from app.models import *
from django.contrib.auth.decorators import login_required, user_passes_test

from app.python.admin.manage import is_admin
@login_required
@user_passes_test(is_admin)
def manageStory(request):
    storys = Story.objects.all()
    form = StoryForm()
    context = {'storys': storys,
               'form': form,
        }
    return render(request, 'admin/story/managementStory.html', context)

def addStory(request):
    form = StoryForm()
    if request.method == 'POST':
        images = request.FILES.getlist('listImages')
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()  # Lưu thông tin model vào cơ sở dữ liệu
            print('oke luu thanh cong')
            # for image in request.FILES.getlist('images'):
            #     instance.image.create(image=image)
            # for image in images:
            #     photo = ImagesChapter.objects.create(story=instance, image=image)
            messages.success(request, 'Thêm truyện thành công')
            return redirect('manageStory')
        else:
            print('lỗi form')
            print(form.errors)
            messages.error(request, 'Thêm truyện thất bại')
    else:
        print('khog biet')
        print(request.method)
        messages.error(request, 'Thêm sản truyện thất bại')

    context = {'form': form,
               'messages': messages,
               }
    return render(request, 'admin/story/addStory.html', context)


def editStory(request):
    id = request.GET.get('id', '')  # lấy id khi người dùng vlick vào sản phẩm nào đó
    story = get_object_or_404(Story, id=id)
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sửa truyện thành công!!')
            return redirect('manageStory')
    form = StoryForm(instance=story,
                      initial={'name': story.name,
                               # 'category': product.category.values_list('id', flat=True),
                               # 'price': product.price,
                               # 'describe': product.describe,
                               # 'image': product.image
                               })

    context = {'story': story,
               'form': form}
    return render(request, 'admin/story/editStory.html', context)

def deleteStory(request, id):
    print('hello')
    print(id)
    print(request.method)
    if request.method == 'GET':
        print('nhảy vào thằng post')
        print(id)
        Story.objects.filter(id=id).delete()
        messages.success(request, 'Xóa truyện thành công.')
        return redirect(reverse('manageStory'))
    else:
        print('không voo đc rôif')
        return render(request, 'admin/story/managementStory.html')

def viewStory(request):
    id = request.GET.get('id', '')  # lấy id khi người dùng vlick vào sản phẩm nào đó
    user = request.user
    print(user)
    story = get_object_or_404(Story, id=id)
    chapters = Chapter.objects.filter(story=story)

    form_chapter = ChapterForm()
    context = {
        'story': story,
        'chapters': chapters,
        'form_chapter': form_chapter,
    }
    return render(request, 'admin/story/view_story.html', context)
def addChapter(request):
    if request.method == 'POST':
        # Lấy thông tin từ form POST
        story_id = request.POST.get('story_id')
        name = request.POST.get('name')

        # Xử lý tệp hình ảnh được tải lên từ form
        image = request.FILES.get('image')
        fs = FileSystemStorage()
        image_name = fs.save(image.name, image)

        # Tạo một bản ghi mới trong bảng Chapter với story_id, name và image được chỉ định
        chapter = Chapter(story_id=story_id, name=name, image=image_name)
        chapter.save()

        images = request.FILES.getlist('listImages')
        print(images)
        for image in images:
            fs = FileSystemStorage()
            image_name = fs.save(image.name, image)
            # Tạo một bản ghi mới trong bảng ImageChapter với story_id, name và image được chỉ định
            image_chapter = ImagesChapter(chap=chapter, image=image_name)
            image_chapter.save()

        messages.success(request, 'Thêm slide thành công')
        return redirect('manageStory')

    else:
        messages.error(request, 'Thêm slide thất bại')

    context = {

    }
    return render(request, 'admin/story/addChapter.html', context)