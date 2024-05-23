import calendar
import datetime
from datetime import timedelta

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from app.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, DateTimeField, IntegerField, Count
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION


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

    users = User.objects.all().count()
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

    today = timezone.now().date()
    top_stories = Story.objects.filter(chapters__date__gte=today).annotate(
        total_views=Count('chapters__view')).order_by('-total_views')[:3]
    for story in top_stories:
        print(story.name, "- hi -", story.total_views)

    # Tính số lượt đọc của từng truyện
    story_views = ViewHistory.objects.values('story_id').annotate(num_views=Count('story_id'))

    # Tính số lượt theo dõi của từng truyện
    story_follows = Follow.objects.values('story_id').annotate(num_follows=Count('story_id'))

    # Kết hợp thông tin số lượt đọc và số lượt theo dõi của mỗi truyện
    trending_stories = {}
    for view in story_views:
        story_id = view['story_id']
        num_views = view['num_views']
        num_follows = Follow.objects.filter(story_id=story_id).count()
        trending_stories[story_id] = num_views + num_follows

    # Sắp xếp các truyện theo thứ tự giảm dần của số lượt đọc và số lượt theo dõi kết hợp
    trending_stories = dict(sorted(trending_stories.items(), key=lambda item: item[1], reverse=True))

    # Lấy ra các truyện xu hướng (ví dụ: 10 truyện đầu tiên)
    trending_stories = list(trending_stories.keys())[:10]
    # trending_stories là danh sách các ID của các truyện xu hướng
    trending_stories_info = []
    for story_id in trending_stories:
        story = Story.objects.get(id=story_id)
        trending_stories_info.append(story)
        print(story.name)

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
        'trending_stories': trending_stories_info,
        'users': users,
    }
    return render(request, 'admin/home_manage.html', context)


def manageHistory(request):
    logs = LogEntry.objects.all()
    paginator = Paginator(logs, 15)  # Số lượng mục trên mỗi trang (đây là 10, bạn có thể điều chỉnh)

    page_number = request.GET.get('page')
    try:
        page_logs = paginator.page(page_number)
    except PageNotAnInteger:
        page_logs = paginator.page(1)
    except EmptyPage:
        page_logs = paginator.page(paginator.num_pages)

    for log in page_logs:
        if log.action_flag == ADDITION:
            log.change_message = "Thêm mới"
        elif log.action_flag == CHANGE:
            change_message = log.get_change_message()
            words = change_message.split()
            if words:
                words.pop(0)
                new_paragraph = ' '.join(words)
            print(new_paragraph)
            log.change_message = "Chỉnh sửa " + new_paragraph
        elif log.action_flag == DELETION:
            log.change_message = "Xóa"

    context = {
        'logs': page_logs,
    }
    return render(request, 'admin/history/history.html', context)
