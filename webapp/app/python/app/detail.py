from django.shortcuts import get_object_or_404, render

from app.models import *


def detail(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"

    slug = request.GET.get('slug', '') # lấy slug khi người dùng vlick vào truyện nào đó
    story = Story.objects.get(slug=slug)
    categories_story = story.category.values_list('slug', flat=True)
    category_names = Genre.objects.filter(id__in=categories_story).values_list('name', flat=True)
    print(story.category)
    chapters = Chapter.objects.filter(story=story)
    if chapters.exists():
        first_chapter = chapters.first()
        last_chapter = chapters.last()
    else:
        # Xử lý trường hợp không có chap nào
        first_chapter = None
        last_chapter = None

    # In kết quả để kiểm tra
    if first_chapter and last_chapter:
        print(first_chapter.id)
        print(last_chapter.id)

    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, story=story)
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'story': story,
        'chapters': chapters,
        'slug': slug,
        'first_chapter': first_chapter,
        'last_chapter': last_chapter,
        'follow': follow,
    }
    return render(request, 'app/detail.html', context)


def detail_chapter(request, chapter_slug):
    global chapter
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    story = Story.objects.get(slug=chapter_slug)
    chapter_slug = request.GET.get('chapter_slug')
    chapters = Chapter.objects.filter(story=story)
    print(chapters)
    id = request.GET.get('chap', '')
    print('TÌm thấy id')
    print(id)
    chapter = get_object_or_404(Chapter, id=id)

    prev_chapter = chapters.filter(id__lt=chapter.id).last()
    next_chapter = chapters.filter(id__gt=chapter.id).first()

    print(chapter.name)

    # print('Chap trước')
    # print(prev_chapter.name)
    # print('Chap sau')
    # print(next_chapter.name)
    images = ImagesChapter.objects.filter(chap=chapter)
    print(chapter)
    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'chapter': chapter,
        'images': images,
        'story': story,
        'chapters': chapters,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
    }
    return render(request, 'app/detail_chapter.html', context)