# from itertools import product
from django.contrib import messages
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
from .python.app.search import searchProduct
from .python.app.updateItem import updateItem
from .python.app.contact import contact


# admin
from .python.admin.manage import Manage
from .python.admin.home_manage import homeManage
from .python.admin.manage_slide import manageSlide, addSlide, editSlide, deleteSlide, get_slide
from .python.admin.updateStatus import update_status
from .python.admin.manage_user import manageUser, deleteUser, addUser, editUser

from .python.admin.manage_category import manageCategory, addCategory, editCategory, deleteCategory
from .python.admin.manage_story import manageStory, addStory, editStory, deleteStory, viewStory, addChapter
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
    }
    return render(request, 'app/follow.html', context)


def ratting(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    stories = Story.objects.all()

    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'stories': stories
    }
    return render(request, 'app/ratting.html', context)


def ratting_date(request):
    # Kiểm tra người dùng đăng nhập
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    current_date = date.today()

    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=100)

    # Lấy danh sách các chapter có lượt xem nhiều trong 7 ngày qua
    popular_stories = Story.objects.filter(chapters__date__range=[date_7_days_ago, current_date]) \
                           .annotate(total_views=Sum('chapters__view')) \
                           .order_by('-total_views')[:10]

    print(popular_stories)
    for story in popular_stories:
        print(story.total_views)
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'stories': popular_stories
    }
    return render(request, 'app/ratting.html', context)


def ratting_month(request):
    # Kiểm tra người dùng đăng nhập
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    current_date = date.today()

    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=100)

    # Lấy danh sách các chapter có lượt xem nhiều trong 7 ngày qua
    popular_chapters = Chapter.objects.filter(date__range=[date_7_days_ago, current_date]) \
                           .annotate(total_views=Sum('view')) \
                           .order_by('-total_views')[:20]

    print(popular_chapters)
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'stories': popular_chapters
    }
    return render(request, 'app/ratting.html', context)

def ratting_year(request):
    # Kiểm tra người dùng đăng nhập
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    current_date = date.today()

    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=100)

    # Lấy danh sách các chapter có lượt xem nhiều trong 7 ngày qua
    popular_chapters = Chapter.objects.filter(date__range=[date_7_days_ago, current_date]) \
                           .annotate(total_views=Sum('view')) \
                           .order_by('-total_views')[:20]

    print(popular_chapters)
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'stories': popular_chapters
    }
    return render(request, 'app/ratting.html', context)