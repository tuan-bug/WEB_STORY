from django.contrib import admin
from django.urls import path, include
from . import views
from .views import *


urlpatterns = [
    path('base/', views.base, name="base"),
    path('', views.getHome, name="home"),
    path('update_item/', views.updateItem, name="update_item"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logoutPage, name="logout"),
    path('search/', views.searchProduct, name="search"),
    #BXH
    path('ratting/', views.ratting, name="ratting"),
    path('ratting_date/', views.ratting_date, name="ratting_date"),
    path('ratting_month/', views.ratting_month, name="ratting_month"),
    path('ratting_year/', views.ratting_year, name="ratting_year"),


    # THỂ LOẠI
    path('category/', views.category, name="category"),
    path('category/<int:category_id>/', views.stories_by_category, name='stories_by_category'),

    path('story_follow/', views.story_follow, name="story_follow"),

    # TRUYỆN
    path('detail/', views.detail, name="detail"),
    path('chapter_detail/<slug:chapter_slug>/', views.detail_chapter, name='chapter_detail'),
    # Path để cập nhật lịch sử đọc
    path('update-view-history/<int:story_id>/<int:chapter_id>/', views.update_view_history, name='update_view_history'),
    # Path để hiển thị lịch sử đọc
    path('view-history/', views.view_history, name='view_history'),
    # Follow story
    path('follow/<int:story_id>/', views.follow_story, name='follow_story'),
    path('unfollow/<int:story_id>/', views.unfollow_story, name='unfollow_story'),
    # THÔNG TIN TÀI KHOẢN
    path('information/', views.Information, name="information"),
    path('edit_information/', views.edit_information, name="edit_information"),
    path('contact/', views.contact, name="contact"),



    # ADMIN
    path('manage/', views.Manage, name="manage"),
    path('home_manage/', views.homeManage, name="home_manage"),


    # STORY
    path('manageStory/', views.manageStory, name="manageStory"),
    path('addStory/', views.addStory, name="addStory"),
    path('addChapter/', views.addChapter, name="addChapter"),
    path('editStory/', views.editStory, name="editStory"),
    path('deleteStory/<int:id>', views.deleteStory, name="deleteStory"),
    path('viewStory/', views.viewStory, name="viewStory"),

    # CATEGORY
    path('manageCategory/', views.manageCategory, name="manageCategory"),
    path('addCategory/', views.addCategory, name="addCategory"),
    path('editCategory/', views.editCategory, name="editCategory"),
    path('deleteCategory/<int:id>', views.deleteCategory, name="deleteCategory"),

    # USERS
    path('manageUser/', views.manageUser, name="manageUser"),
    path('addUser/', views.addUser, name="addUser"),
    path('editUser/', views.editUser, name="editUser"),
    path('delUser/<int:id>', views.deleteUser, name="deleteUser"),











]
