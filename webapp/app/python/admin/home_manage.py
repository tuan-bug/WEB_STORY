import calendar
import datetime
from datetime import timedelta

from django.shortcuts import render

from app.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, DateTimeField, IntegerField
from django.contrib.admin.models import LogEntry


def is_admin(user):
    return user.is_authenticated and user.is_staff


def generate_calendar(year, month):
    # Tạo một đối tượng lịch cho tháng được chỉ định
    cal = calendar.monthcalendar(year, month)
    return cal


@login_required
@user_passes_test(is_admin)
def homeManage(request):
    # Sử dụng phương thức aggregate() của queryset để tính tổng lượt xem
    # total_views_query = Story.objects.aggregate(total_views=Sum('view'))
    # Lấy giá trị tổng lượt xem từ kết quả truy vấn, hoặc trả về 0 nếu không có bản ghi nào
    # total_views = total_views_query['total_views'] or 0

    total_views = Story.objects.aggregate(total_views=Sum('view'))['total_views'] or 0
    print("Tổng số lượt xem của tất cả các câu chuyện là:", total_views)
    total_likes = Story.objects.aggregate(total_likes=Sum('likes'))['total_likes'] or 0
    print("Tổng số lượt xem của tất cả các câu chuyện là:", total_likes)

    story_view = Story.objects.all().order_by('-view')[:5]

    current_time = timezone.now()
    reads_per_day = []

    for i in range(7):
        start_date = current_time - timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        reads_count = Chapter.objects.filter(date__gte=start_date, date__lt=end_date).aggregate(
            total_views=Sum('view'))['total_views']
        formatted_date = start_date.strftime("%d/%m/%y")
        reads_per_day.append((formatted_date, reads_count if reads_count else 0))

    reads_per_day.sort(key=lambda x: x[0])
    for date, reads_count in reads_per_day:
        print(f"{date}: {reads_count} lượt đọc")

    browser_counts = BrowserStats.objects.aggregate(
        chrome_count=models.Sum('chrome_count'),
        firefox_count=models.Sum('firefox_count'),
        edge_count=models.Sum('edge_count'),
        safari_count=models.Sum('safari_count'),
        other_count=models.Sum('other_count')
    )

    # Trích xuất số lượng của từng loại trình duyệt từ kết quả
    chrome_count = browser_counts['chrome_count']
    firefox_count = browser_counts['firefox_count']
    edge_count = browser_counts['edge_count']
    safari_count = browser_counts['safari_count']
    other_count = browser_counts['other_count']
    print(chrome_count, firefox_count, edge_count, safari_count, other_count)

    year = current_time.year
    month = current_time.month

    # Tính toán lịch cho tháng hiện tại
    calendar_data = generate_calendar(year, month)
    previous_month = current_time.month - 1 if current_time.month > 1 else 12
    previous_year = current_time.year if current_time.month > 1 else current_time.year - 1

    next_month = current_time.month + 1 if current_time.month < 12 else 1
    next_year = current_time.year if current_time.month < 12 else current_time.year + 1
    context = {
        'total_views': total_views,
        'total_likes': total_likes,
        'chrome_count': chrome_count,
        'firefox_count': firefox_count,
        'edge_count': edge_count,
        'safari_count': safari_count,
        'other_count': other_count,
        'story_view': story_view,
        'reads_per_day': reads_per_day,
        'previous_year': previous_year,
        'previous_month': previous_month,
        'next_year': next_year,
        'next_month': next_month,
        'year': current_time.year,
        'month': current_time.month,
        'calendar': calendar_data,
        'current_day': current_time.day,
    }
    return render(request, 'admin/home_manage.html', context)


def manageHistory(request):
    logs = LogEntry.objects.all()
    print(logs)
    for log in logs:
        print(f"Người dùng: {log.user}")
        print(f"Thời gian: {log.action_time}")
        # print(f"Hoạt động: {log.get_action_display()}")
        print(f"Đối tượng: {log.object_repr}")
        print(f"Đối tượng ID: {log.object_id}")
        print(f"Thay đổi: {log.change_message}")
        print("----------")
    context = {
        'logs': logs,
    }
    return render(request, 'admin/history/history.html', context)
