import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from rest_framework import serializers
from ckeditor.fields import RichTextField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify



class Contact(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(max_length=700, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    def __str__(self):
        return self.name

# // TRUYỆN
class Customer(models.Model):
    # user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length =200,null=True)
    user_name = models.CharField(max_length =200,null=True)
    email = models.EmailField(max_length =200,null=True)
    password = models.CharField(max_length=200,null=True)
    gender = models.CharField(max_length=10)
    birthdate = models.DateField()
    profile_image = models.ImageField(null=True, blank=True)

    @property
    def ImageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
class Genre(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_genre', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name


class Story(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Đã hoàn thành'),
        ('ongoing', 'Đang tiến hành'),
        ('dropped', 'Bị drop'),
    ]
    NEW_STATUS_CHOICES = [
        ('new', 'Mới'),
        ('not_new', 'Không mới'),
    ]
    name = models.CharField(max_length=200, null=True)
    slug = models.CharField(max_length=200, null=True,blank=True)
    category = models.ManyToManyField(Genre, related_name='story_genre', blank=True)
    image = models.ImageField(null=True, blank=True)
    author = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='ongoing')
    description = models.TextField(null=True)
    view = models.IntegerField(default=0)
    count_comment = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    story_new = models.CharField(max_length=100, choices=NEW_STATUS_CHOICES, default='not_new')
    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def update_total_views(self):
        total_views = sum(chapter.view for chapter in self.chapters.all())
        self.view = total_views
        self.save()

class Chapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    date = models.DateField(default=timezone.now, null=True)
    view = models.IntegerField(default=0)
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    def __str__(self):
        return self.story.name + ' - ' + str(self.name)

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, blank=True)
    followed_at = models.DateField(default=timezone.now, null=True)

    class Meta:
        unique_together = ('user', 'story')  # Đảm bảo mỗi người dùng chỉ theo dõi một truyện duy nhất một lần

    def __str__(self):
        return f"{self.user.username} follows {self.story.name}"
class ImagesChapter(models.Model):
    chap = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.chap.story.name

class Comment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.TextField(null=True, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    def __str__(self):
        return self.story

class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    chapter_id = models.IntegerField()
    is_reading = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
# Create your models here.




# Form của các Model
class FormContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tên của bạn'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email của bạn'}),
            'message': forms.Textarea(attrs={'placeholder': 'Nội dung ....'}),
        }
class CreateUserForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 6:
            raise ValidationError("Tên đăng nhập phải chứa ít nhất 6 ký tự.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise ValidationError("Mật khẩu phải chứa ít nhất 8 ký tự.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Mật khẩu xác nhận không khớp.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1','password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
            'password2': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name')



class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['name', 'slug', 'category', 'description', 'image', 'author', 'status', 'story_new']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            # 'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            #'status': forms.TextInput(attrs={'class': 'form-control'}),
            #'story_new': forms.TextInput(attrs={'class': 'form-control'}),
        }
        STATUS_CHOICES = [
            ('completed', 'Đã hoàn thành'),
            ('ongoing', 'Đang tiến hành'),
            ('dropped', 'Bị drop'),
        ]
        NEW_STATUS_CHOICES = [
            ('new', 'Mới'),
            ('not_new', 'Không mới'),
        ]
        status = forms.ChoiceField(choices=STATUS_CHOICES, initial='ongoing', widget=forms.Select())
        story_new = forms.ChoiceField(choices=NEW_STATUS_CHOICES, initial='not_new', widget=forms.Select())

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }