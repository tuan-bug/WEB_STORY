
from django.contrib import messages
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import JsonResponse

# app
from .python.app.base import *
from .python.app.follow import *

from .python.app.category import category, stories_by_category
from .python.app.detail import detail, detail_chapter
from .python.app.information import Information, edit_information
from .python.app.login import loginPage, logoutPage
from .python.app.register import register
from .python.app.search import searchStory
from .python.app.updateItem import updateItem
from .python.app.ratting import *
from .python.app.contact import *


# admin
from .python.admin.manage import Manage
from .python.admin.home_manage import homeManage, manageHistory
from .python.admin.manage_slide import manageSlide, addSlide, editSlide, deleteSlide, get_slide
from .python.admin.updateStatus import update_status
from .python.admin.manage_user import manageUser, deleteUser, addUser, editUser

from .python.admin.manage_category import manageCategory, addCategory, editCategory, deleteCategory, searchCategory
from .python.admin.manage_story import manageStory, addStory, editStory, deleteStory, viewStory, addChapter, searchStory
from django.views.decorators.csrf import csrf_exempt

import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime, date, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
# from django.utils.http import urlquote



from django.urls import reverse
from django.shortcuts import render


@csrf_exempt
def update_view_history(request, story_id, chapter_id):
    if request.user.is_authenticated:
        # Lấy lịch sử từ cookie
        view_history = request.COOKIES.get('view_history', '[]')
        view_history = json.loads(view_history)

        # Kiểm tra xem story_id đã được đọc chưa
        if story_id not in view_history:
            view_history.append(story_id)

        # Giới hạn lịch sử đọc truyện tối đa là 10 mục (hoặc bất kỳ giới hạn nào bạn muốn)
        view_history = view_history[-10:]

        # Cập nhật cookie với lịch sử mới
        response = JsonResponse({'status': 'success'})
        response.set_cookie('view_history', json.dumps(view_history))
        test = ViewHistory.objects.filter(story_id=story_id)
        if test.exists():
            test.delete()

        # Cập nhật lịch sử trong cơ sở dữ liệu
        ViewHistory.objects.create(user=request.user, story_id=story_id, chapter_id=chapter_id, is_reading=True)
        return response

    return JsonResponse({'status': 'error'})

def view_history(request):
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    story_chapter_list = []
    context = {}
    if request.user.is_authenticated:
        view_history = ViewHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
        for history in view_history:
            story = Story.objects.get(id=history.story_id)
            chapter = Chapter.objects.get(id=history.chapter_id)
            story_chapter_list.append({'story': story, 'chapter': chapter})

        print(story_chapter_list)
        context = {
            'view_history': view_history,
            'story_chapter_list': story_chapter_list,
            'user_not_login':user_not_login,
            'user_login': user_login,
            'profile': profile,
        }
        return render(request, 'app/history.html', context)
    else:
        context = {
            'user_not_login': user_not_login,
            'user_login': user_login,
            'story_chapter_list': story_chapter_list,
        }

    return render(request, 'app/history.html', context)


def story_follow(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    followed_stories = []  # Khởi tạo danh sách các câu chuyện mà người dùng đã theo dõi
    if request.user.is_authenticated:
        follows = Follow.objects.filter(user=request.user)
        print('Following')
        for follow in follows:
            followed_stories.append(follow.story)

    for story in followed_stories:
        latest_chapter = story.chapters.order_by('-name').first()
        if latest_chapter:
            # Lấy số từ tên chương mới nhất
            match = re.search(r'\d+', latest_chapter.name)
            if match:
                chapter_number = match.group()  # Lấy số từ kết quả phù hợp
                story.chapter_number = chapter_number
                story.latest_chapter_date = latest_chapter.date  # Lấy ngày của chương mới nhất
                story.chapter_id = latest_chapter.id
                print("Chapter number:", story.chapter_number )
                print("Chapter id: ", story.chapter_id)
                print("Latest chapter date:", latest_chapter.date)
            else:
                print("No number found in chapter name")
        else:
            print("No chapters found for story:", story.name)


    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'stories': followed_stories,
        'profile': profile,
    }
    return render(request, 'app/follow.html', context)



def chat(request):
    messages = Chat.objects.all()
    users = User.objects.all()
    print(messages)
    for mes in messages:
        print(mes.user)
        for user in users:
            if mes.user == user:
                profiles = Customer.objects.filter(user=user).order_by('-created_at')
                if profiles:
                    profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
                    print(profile.profile_image)
                else:
                    profile = None
                mes.customer_img = profile.profile_image

    form = FormChat()
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    context = {
        'form': form,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'profile': profile,
        'messages': messages,
    }
    return render(request, 'app/chat.html', context)


def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        if message_text:
            # Lưu tin nhắn vào cơ sở dữ liệu
            message = Chat(user=request.user,chat=message_text)
            message.save()
            return redirect('chat')
    return JsonResponse({'success': False})


def editChapter(request):
    if request.method == 'POST' and request.is_ajax():
        chapter_id = request.POST.get('id')
        chapter_name = request.POST.get('name')

        try:
            chapter = Chapter.objects.get(id=chapter_id)
            chapter.name = chapter_name
            chapter.save()
            return JsonResponse({'success': True})
        except Chapter.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chapter not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})


def deleteChap(request, id):
    Chapter.objects.filter(id=id).delete()
    messages.success(request, 'Đã xóa chap thành công')
    return redirect('manageStory')
    context = {
               'messages': messages,
            }
    return render(request, 'admin/story/view_story.html', context)


def Notification(request):
    comments_list = Comment.objects.all()

    # Số lượng comments trên mỗi trang
    paginator = Paginator(comments_list, 10)  # 10 comments mỗi trang

    page = request.GET.get('page')

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # Nếu page không phải là số nguyên, trả về trang đầu tiên
        comments = paginator.page(1)
    except EmptyPage:
        # Nếu page nằm ngoài phạm vi, trả về trang cuối cùng
        comments = paginator.page(paginator.num_pages)
    context = {
        'comments': comments,
    }
    return render(request, 'admin/notification/notification.html', context)