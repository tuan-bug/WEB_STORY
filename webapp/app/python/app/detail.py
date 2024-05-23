from django.shortcuts import get_object_or_404, render, redirect

from app.models import *
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from django.shortcuts import render


from django.shortcuts import redirect



def detail(request):
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
    formComment = FormComment()

    slug = request.GET.get('slug', '') # lấy slug khi người dùng vlick vào truyện nào đó
    story = Story.objects.get(slug=slug)
    story.view = story.view + 1
    story.save()
    categories_story = story.category.values_list('slug', flat=True)
    categories = story.category.all()
    print(story)
    print(story.category)
    listComment = Comment.objects.filter(story=story)

    lstStory = Story.objects.all()[:4]
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
    recommendations = recommend_stories()
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
        'lstStory': lstStory,
        'profile': profile,
        'is_logged_in': request.user.is_authenticated,
        'recommendations': recommendations,
    }
    return render(request, 'app/detail.html', context)



def detail_chapter(request, chapter_slug):
    global chapter
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
    listComment = Comment.objects.filter(story=story)
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
        'profile': profile,
        'listComment': listComment,
    }
    return render(request, 'app/detail_chapter.html', context)



def get_story_data():
    stories = Story.objects.all()
    data = []
    for story in stories:
        data.append([story.id, story.view, story.count_comment, story.likes])
    return pd.DataFrame(data, columns=['id', 'views', 'comments', 'likes'])

def train_kmeans():
    df = get_story_data()
    kmeans = KMeans(n_clusters=8)  # Chọn số lượng cụm phù hợp
    df['cluster'] = kmeans.fit_predict(df[['views', 'comments', 'likes']])
    return kmeans, df

kmeans_model, clustered_data = train_kmeans()

def recommend_stories(num_recommendations=5):
    # Lấy dữ liệu truyện và cluster đã được gán nhãn
    global clustered_data

    # Chọn một cụm ngẫu nhiên
    random_cluster = np.random.choice(clustered_data['cluster'].unique())

    # Lấy các truyện thuộc cụm này
    similar_stories = clustered_data[clustered_data['cluster'] == random_cluster]

    # Sắp xếp các truyện trong cụm theo số lượt xem, bình luận, yêu thích và chọn top N truyện
    similar_stories = similar_stories.sort_values(by=['views', 'comments', 'likes'], ascending=False)
    recommended_stories_ids = similar_stories['id'].head(num_recommendations).tolist()

    # Lấy các đối tượng truyện từ ID
    recommended_stories = Story.objects.filter(id__in=recommended_stories_ids)

    return recommended_stories