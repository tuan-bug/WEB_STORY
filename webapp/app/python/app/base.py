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
    #slide = Slide.objects.all()
    #  # lay cac damh muc lon
    context = {
        'show_manage': show_manage,
    }
    return render(request, 'app/base.html', context)

def getHome(request):
    if request.user.is_authenticated:
        user_not_login = "none"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "none"

    # storys_with_latest_chapters = Story.objects.annotate(
    #     latest_chapter_name=Substr('chapters__name', 1, 7)
    # )
    # story = Story.objects.all()
    #
    # # Tạo một thuộc tính mới latest_chapter_words để lưu hai từ đầu tiên từ tên của chương mới nhất
    # for story in story:
    #     latest_chapter = story.chapters.order_by('-name').first()
    #     if latest_chapter:
    #         story.latest_chapter_words = latest_chapter.name.split()[:2]
    #     else:
    #         story.latest_chapter_words = []
    #
    # # In hai từ đầu tiên từ tên chương mới nhất của mỗi câu chuyện
    # for story in story:
    #     print(story.latest_chapter_words)
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
