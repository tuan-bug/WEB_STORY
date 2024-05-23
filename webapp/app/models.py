import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from rest_framework import serializers
from ckeditor.fields import RichTextField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinLengthValidator, ValidationError


class Contact(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(max_length=700, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    def __str__(self):
        return self.name

class BrowserStats(models.Model):
    chrome_count = models.IntegerField(default=0)
    firefox_count = models.IntegerField(default=0)
    edge_count = models.IntegerField(default=0)
    safari_count = models.IntegerField(default=0)
    other_count = models.IntegerField(default=0)

# // TRUYỆN
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    @property
    def ImageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url
class Genre(models.Model):
    name = models.CharField(max_length=200, null=False, 
                            validators=[MinLengthValidator(6, "Tên danh mục phải có ít nhất 6 kí tự.")],
                            error_messages={'null': 'Trường này không được để trống.'})
    slug = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=500, null=True)
    def __str__(self):
        return self.name

    def get_change_message_display(self, change_message):
        action = "Sửa" if "changed" in change_message else "Thêm" if "added" in change_message else "Xóa"
        if action == "Sửa":
            changed_fields = ", ".join(change_message[0]["changed"]["fields"])
            return f"{action}: {changed_fields}"
        elif action == "Thêm":
            return "Thêm mới"
        elif action == "Xóa":
            return "Đã xóa"

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
    name = models.CharField(max_length=200, null=False)
    slug = models.CharField(max_length=200, null=False,blank=False)
    category = models.ManyToManyField(Genre, related_name='story_genre')
    image = models.ImageField(null=True, blank=True)
    author = models.CharField(max_length=200, null=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='ongoing')
    description = models.TextField(null=True, blank=True)
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

    def get_change_message_display(self, change_message):
        action = "Sửa" if "changed" in change_message else "Thêm" if "added" in change_message else "Xóa"
        if action == "Sửa":
            changed_fields = ", ".join(change_message[0]["changed"]["fields"])
            return f"{action}: {changed_fields}"
        elif action == "Thêm":
            return "Thêm mới"
        elif action == "Xóa":
            return "Đã xóa"

class Chapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=200, null=False)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sau khi một chương được lưu, cập nhật tổng số lượt xem của câu chuyện liên quan
        self.story.update_total_views()

    def get_change_message_display(self, change_message):
        action = "Sửa" if "changed" in change_message else "Thêm" if "added" in change_message else "Xóa"
        if action == "Sửa":
            changed_fields = ", ".join(change_message[0]["changed"]["fields"])
            return f"{action}: {changed_fields}"
        elif action == "Thêm":
            return "Thêm mới"
        elif action == "Xóa":
            return "Đã xóa"
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, blank=True)
    followed_at = models.DateField(default=timezone.now, null=True)

    class Meta:
        unique_together = ('user', 'story')  # Đảm bảo mỗi người dùng chỉ theo dõi một truyện duy nhất một lần

    def __str__(self):
        return f"{self.user.username} follows {self.story.name}"

    def get_change_message_display(self, change_message):
        action = "Sửa" if "changed" in change_message else "Thêm" if "added" in change_message else "Xóa"
        if action == "Sửa":
            changed_fields = ", ".join(change_message[0]["changed"]["fields"])
            return f"{action}: {changed_fields}"
        elif action == "Thêm":
            return "Thêm mới"
        elif action == "Xóa":
            return "Đã xóa"
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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.TextField(null=True, blank=False)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    # def __str__(self):
    #     return self.story

    def get_change_message_display(self, change_message):
        action = "Sửa" if "changed" in change_message else "Thêm" if "added" in change_message else "Xóa"
        if action == "Sửa":
            changed_fields = ", ".join(change_message[0]["changed"]["fields"])
            return f"{action}: {changed_fields}"
        elif action == "Thêm":
            return "Thêm mới"
        elif action == "Xóa":
            return "Đã xóa"
class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    chapter_id = models.IntegerField()
    is_reading = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.CharField(max_length=300, null=True)


# Create your models here.


class FormChat(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['chat']
    widgets = {
        'chat': forms.TextInput(attrs={'class': 'form-control'}),

    }
# Form của các Model
class FormContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Tên của bạn'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email của bạn'}),
            'message': forms.Textarea(attrs={'placeholder': 'Nội dung ....'}),
        }

class CreateUserForm(UserCreationForm):
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


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="Mật khẩu hiện tại", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Mật khẩu mới", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Xác nhận mật khẩu mới", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")
        return cleaned_data
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields =['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control'})
        }
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['name', 'slug', 'category', 'description', 'image', 'author', 'status', 'story_new']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            # 'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
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
    
class AddCategory(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'description']
        def clean_name(self):
            name = self.cleaned_data.get('name')
            if not name:
                raise forms.ValidationError("Tên không được để trống")
            return name
    
        def clean_slug(self):
            slug = self.cleaned_data.get('slug')
            if not slug:
                raise forms.ValidationError("Slug không được để trống")
            return slug
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FormComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title']
        widgets = {
            'title': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),

        }
    def __str__(self):
        return self.story
