import datetime

from django.http import JsonResponse

from . import models


def format_data():
    return {
        'code': 0,
        'message': ''
    }


def get_date(date):
    """
    将date字符串转换成datetime.date对象, date字符串格式为 y-m-d,
    当date为None时取今天的日期

    :return: <datetime.date object>
    """
    if date is None:
        return datetime.datetime.now().date()
    return datetime.date(*tuple(map(int, date.split("-"))))


def reserve(request):
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            date = get_date(request.POST.get('date'))
            new = models.QueInfo.reserve(request.POST['openId'], date)
            if new is not None:
                data['message'] = "预约成功"
                data['pos'] = new.pos - models.QueInfo.get_pos_delta(date)
            else:
                data['code'] = -1
                data['message'] = "您今日已预约, 无法再次预约"
        except Exception as e:
            data['message'] = str(e)
            data['code'] = -1

    return JsonResponse(data)


def create(request):
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            models.User.objects.create(**request.POST.dict())
            data['message'] = "创建成功"
        except Exception as e:
            data['code'] = -1
            data['message'] = str(e)

    return JsonResponse(data)


def complete(request):
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            current = models.QueInfo.objects.get(
                user__openId=request.POST['openId'], date__date=datetime.datetime.now().date()
            )
            if current.status == 1:
                data['code'] = -1
                data['message'] = "请不要重复提交"
            elif current.user.openId != models.QueInfo.first().user.openId:
                data['code'] = -1
                data['message'] = "未到您检测, 现在无法提交"
            else:
                current.complete(request.POST['code'])
                data['message'] = "提交成功"
        except Exception as e:
            data['code'] = -1
            data['message'] = str(e)

    return JsonResponse(data)


def get_user_pos(request):
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            date = get_date(request.POST.get('date'))
            que_info = models.Date.objects.get(date=date).que_info
            uq = que_info.get(user__openId=request.POST['openId'])

            if uq.status == 1:
                data['pos'] = None  # noqa
                data['message'] = "已完成预约"
            else:
                data['pos'] = uq.pos - models.QueInfo.get_pos_delta(date)
                data['message'] = "获取成功"
        except Exception as e:
            data['code'] = -1
            data['message'] = str(e)
    return JsonResponse(data)


def user_reserved(request):
    """用户是否已预约"""
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        if not models.QueInfo.valid(request.POST['openId']):
            data['code'] = 2
    return JsonResponse(data)


def delay(request):
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            pos = request.POST['pos']
            openId = request.POST['openId']
            date = get_date(request.POST.get('date'))
            models.QueInfo.delay(openId, int(pos), date)
        except Exception as e:
            data['code'] = -1
            data['message'] = str(e)
        else:
            data['message'] = "延迟成功"
    return JsonResponse(data)


def message(request):
    """获取消息"""
    data = format_data()
    if request.method != "POST":
        data['code'] = -1
        data['message'] = f"不支持{request.method}请求"
    else:
        try:
            pass
        except Exception as e:
            data['code'] = -1
            data['message'] = str(e)
        else:
            data['message'] = "操作成功"
    return JsonResponse(data)
