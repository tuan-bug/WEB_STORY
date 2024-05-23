import numpy as np
import pandas as pd
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.db.models import Max, Sum
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

from app.models import *


def ratting(request):
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    stories = Story.objects.all()
    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
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
    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=7)

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
        'stories': popular_stories,
        'profile': profile,
    }
    return render(request, 'app/ratting.html', context)


def ratting_month(request):
    # Kiểm tra người dùng đăng nhập
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    current_date = date.today()
    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=30)

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
        'stories': popular_stories,
        'profile': profile,
    }
    return render(request, 'app/ratting.html', context)

def ratting_year(request):
    # Kiểm tra người dùng đăng nhập
    user_not_login = "none" if request.user.is_authenticated else "show"
    user_login = "show" if request.user.is_authenticated else "none"
    current_date = date.today()
    profile = None
    if request.user.is_authenticated:
        profiles = Customer.objects.filter(user=request.user).order_by('-created_at')
        if profiles:
            profile = profiles.first()  # Lấy đối tượng đầu tiên trong danh sách đã sắp xếp
            print(profile.profile_image)
        else:
            profile = None
    # Lấy ngày hiện tại
    current_date = date.today()

    # Tính ngày 7 ngày trước
    date_7_days_ago = current_date - timedelta(days=300)

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
        'stories': popular_stories,
        'profile': profile,
    }
    return render(request, 'app/ratting.html', context)
