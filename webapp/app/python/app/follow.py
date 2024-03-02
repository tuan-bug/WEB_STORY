from django.shortcuts import get_object_or_404, redirect
from app.models import *
from django.urls import reverse
from django.shortcuts import render


def follow_story(request, story_id):

    if request.user.is_authenticated:
        story = get_object_or_404(Story, id=story_id)
        follow, created = Follow.objects.get_or_create(user=request.user, story=story)
        if not created:
            # Người dùng đã theo dõi truyện này
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))

def unfollow_story(request, story_id):
    if request.user.is_authenticated:
        story = get_object_or_404(Story, id=story_id)
        Follow.objects.filter(user=request.user, story=story).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))
