from django.shortcuts import render
import re
from app.models import *
from django.db.models import Q


def category(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    categories = Genre.objects.all()
    stories = Story.objects.all()
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

    context ={
          'user_login': user_login,
          'user_not_login': user_not_login,
          'categories': categories,
          'stories': stories,
    }
    return render(request, "app/category.html", context)


def stories_by_category(request, category_id):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    categories = Genre.objects.all()
    stories = Story.objects.filter(category__id=category_id)
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
        'categories': categories,
        'stories': stories,
        'user_login': user_login,
        'user_not_login': user_not_login,
    }
    return render(request, 'app/category.html', context)