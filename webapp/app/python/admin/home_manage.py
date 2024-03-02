from django.shortcuts import render

from app.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def homeManage(request):
    # Sử dụng phương thức aggregate() của queryset để tính tổng lượt xem
    #total_views_query = Story.objects.aggregate(total_views=Sum('view'))
    # Lấy giá trị tổng lượt xem từ kết quả truy vấn, hoặc trả về 0 nếu không có bản ghi nào
    #total_views = total_views_query['total_views'] or 0

    total_views = Story.objects.aggregate(total_views=Sum('view'))['total_views'] or 0
    print("Tổng số lượt xem của tất cả các câu chuyện là:", total_views)
    total_likes = Story.objects.aggregate(total_likes=Sum('likes'))['total_likes'] or 0
    print("Tổng số lượt xem của tất cả các câu chuyện là:", total_likes)
    context = {
       'total_views': total_views,
        'total_likes': total_likes,
    }
    return render(request, 'admin/home_manage.html', context)