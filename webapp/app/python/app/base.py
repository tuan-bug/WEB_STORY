from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Max
from django.db.models.functions import Substr
import re

from app.models import *


def base(request):
    user = request.user
    if user.is_staff:
        print('admin')
        show_manage = 'show'
    else:
        print('not admin')
        show_manage = 'none'
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
            admin_template = 'admin_dashboard.html'
        else:
            profile = None
    context = {
        'show_manage': show_manage,
        'profile': profile,
    }
    return render(request, 'app/base.html', context)

def getHome(request):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "none"

    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    print("TRÌNH DUYỆT: ")
    print(user_agent)
    if 'Chrome' in user_agent:
        BrowserStats.objects.update(chrome_count=models.F('chrome_count') + 1)
    elif 'Firefox' in user_agent:
        BrowserStats.objects.update(firefox_count=models.F('firefox_count') + 1)
    elif 'Edge' in user_agent:
        BrowserStats.objects.update(edge_count=models.F('edge_count') + 1)
    elif 'Safari' in user_agent:
        BrowserStats.objects.update(safari_count=models.F('safari_count') + 1)
    else:
        BrowserStats.objects.update(other_count=models.F('other_count') + 1)

    stories = Story.objects.all()

    # Lặp qua mỗi câu chuyện
    for story in stories:
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
        'storys': stories,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'profile': profile,
    }
    return render(request, 'app/home.html', context)


def show_manage(request):
    check_staff = request.user
    if check_staff.is_staff:
        print('admin')
        show_manage = 'show'
    else:
        print('not admin')
        show_manage = 'none'

    return show_manage
