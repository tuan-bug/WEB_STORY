import numpy as np
import pandas as pd
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.db.models import Max
from django.db.models.functions import Substr
import re

from sklearn.cluster import KMeans

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

    stories_list = Story.objects.all()

    # Lặp qua mỗi câu chuyện
    for story in stories_list:
        latest_chapter = story.chapters.order_by('-name').first()
        if latest_chapter:
            match = re.search(r'\d+', latest_chapter.name)
            if match:
                chapter_number = match.group()
                story.chapter_number = chapter_number
                story.latest_chapter_date = latest_chapter.date
                story.chapter_id = latest_chapter.id
                print("Chapter number:", story.chapter_number)
                print("Chapter id:", story.chapter_id)
                print("Latest chapter date:", latest_chapter.date)
            else:
                print("No number found in chapter name")
        else:
            print("No chapters found for story:", story.name)

    # Sử dụng Paginator cho danh sách câu chuyện
    paginator = Paginator(stories_list, 24)  # 10 câu chuyện mỗi trang
    page = request.GET.get('page')

    try:
        stories = paginator.page(page)
    except PageNotAnInteger:
        stories = paginator.page(1)
    except EmptyPage:
        stories = paginator.page(paginator.num_pages)

    recommended_stories = recommend_stories()
    context = {
        'storys': stories,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'profile': profile,
        'recommended_stories': recommended_stories,
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


def get_story_data():
    stories = Story.objects.all()
    data = []
    for story in stories:
        data.append([story.id, story.view, story.count_comment, story.likes])
    return pd.DataFrame(data, columns=['id', 'views', 'comments', 'likes'])


def train_kmeans(min_cluster_size=7, initial_num_clusters=2):
    df = get_story_data()
    num_samples = len(df)
    num_clusters = initial_num_clusters

    if num_samples < min_cluster_size:
        raise ValueError(f"Not enough samples ({num_samples}) to form clusters with minimum size {min_cluster_size}.")

    while True:
        if num_clusters > num_samples:
            # Giảm số lượng cụm xuống nếu nó vượt quá số lượng mẫu
            num_clusters = num_samples
            print(f"Adjusted number of clusters to {num_clusters} to match the number of samples.")
            break

        kmeans = KMeans(n_clusters=num_clusters)  # Chọn số lượng cụm phù hợp
        df['cluster'] = kmeans.fit_predict(df[['views', 'comments', 'likes']])

        # Kiểm tra kích thước của các cụm
        cluster_sizes = df['cluster'].value_counts()
        if all(size >= min_cluster_size for size in cluster_sizes):
            break
        else:
            num_clusters += 1  # Tăng số lượng cụm nếu có cụm nào nhỏ hơn min_cluster_size

    return kmeans, df


kmeans_model, clustered_data = train_kmeans()


def recommend_stories(num_recommendations=8):
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