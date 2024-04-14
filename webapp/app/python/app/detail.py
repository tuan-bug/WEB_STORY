from django.shortcuts import get_object_or_404, render, redirect

from app.models import *


from django.shortcuts import redirect

def detail(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    formComment = FormComment()

    slug = request.GET.get('slug', '') # lấy slug khi người dùng vlick vào truyện nào đó
    story = Story.objects.get(slug=slug)
    categories_story = story.category.values_list('slug', flat=True)
    categories = story.category.all()
    print(story)
    print(story.category)
    listComment = Comment.objects.filter(story=story)

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
    follow = ''
    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, story=story)

    if request.method == 'POST':
        form = FormComment(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['title']
            comments = Comment(user=request.user, story=story, title=content)
            comments.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Chuyển hướng về trang chi tiết của câu chuyện
    story.count_comment = listComment.count()
    story.save()
    print(listComment)

    context = {
        'user_not_login': user_not_login,
        'user_login': user_login,
        'story': story,
        'chapters': chapters,
        'slug': slug,
        'first_chapter': first_chapter,
        'last_chapter': last_chapter,
        'follow': follow,
        'formComment': formComment,
        'listComment': listComment,
        'categories': categories,
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
    chapter.view = chapter.view + 1
    chapter.save()
    prev_chapter = chapters.filter(id__lt=chapter.id).last()
    next_chapter = chapters.filter(id__gt=chapter.id).first()

    print(chapter.name)

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