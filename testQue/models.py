from datetime import datetime

from django.db import models


# Create your models here.


class User(models.Model):
    openId = models.CharField(max_length=50, verbose_name="微信openId", unique=True)
    name = models.CharField(max_length=10, verbose_name="姓名")
    gender = models.IntegerField(verbose_name="性别", choices=((0, "男"), (1, "女")))
    age = models.IntegerField(verbose_name="年龄")
    phone = models.CharField(max_length=11, verbose_name="电话号码")

    def __str__(self):
        return "<user: %s, openId: %s>" % (self.id, self.openId)


class QueInfo(models.Model):
    pos = models.IntegerField(verbose_name="排名")
    date = models.ForeignKey('Date', on_delete=models.CASCADE, related_name="que_info")
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="pos")
    status = models.IntegerField(verbose_name="是否完成", default=0, choices=((0, "未完成"), (1, "已完成")))

    def __str__(self):
        return "user: %s, pos: %d, date: %s" % (self.user, self.pos, self.date)

    def complete(self, code):
        UserBarCode.objects.create(code=code, user=self.user, create_date=self.date)
        self.status = 1
        self.save()

    @classmethod
    def get_current_que_info(cls):
        today = Date.get_date()
        return today.que_info.filter(status=0).order_by('pos')

    @classmethod
    def first(cls, date=None, real=False):
        """
        :param date: 日期
        :param real: date中, 为False则返回还未完成的第一个, True为全部的第一个
        :return:
        """
        que_info = Date.get_date(date).que_info
        try:
            if not real:
                return que_info.filter(status=0).order_by('pos').first()
            return que_info.order_by('pos').first()
        except cls.DoesNotExist:
            pass

    @classmethod
    def last(cls, date=None):
        que_info = Date.get_date(date).que_info
        try:
            return que_info.order_by('pos').last()
        except cls.DoesNotExist:
            pass

    @classmethod
    def valid(cls, open_id, date=None):
        """
        指定用户预约是否有效
        如果在指定日期已预约, 则返回False, 反之True
        """
        que_info = Date.get_date(date).que_info
        try:
            que_info.get(user__openId=open_id)
        except cls.DoesNotExist:
            return True
        return False

    @classmethod
    def _reserve(cls, open_id, date=None):
        last = cls.last(date)
        date = Date.get_date(date=date)
        user = User.objects.get(openId=open_id)
        if last is None:
            return cls.objects.create(
                user=user, pos=1, date=date
            )
        new = cls.objects.create(
            user=user,
            pos=last.pos + 1,
            date=date,
        )
        return new

    @classmethod
    def reserve(cls, open_id, date=None):
        """

        :param open_id: 微信Id
        :param date: <object datetime.date>
        :return:
        """
        if cls.valid(open_id, date):
            return cls._reserve(open_id, date)

    @staticmethod
    def get_pos_delta(date=None):
        que_info = Date.get_date(date).que_info
        return que_info.filter(status=1).count()

    @classmethod
    def delay(cls, open_id, pos, date=None):
        que_info = Date.get_que_info(date)
        count = que_info.count()
        self = que_info.get(user__openId=open_id)
        ori_pos = self.pos
        new_pos = ori_pos + pos

        if self.status == 1:  # 已完成的不允许调整位置
            raise ValueError("今日您已完成检测, 无法延迟")

        if pos >= count - ori_pos:
            new_pos = count

        for i in range(ori_pos + 1, new_pos + 1):
            uq = que_info.get(pos=i)
            uq.pos -= 1
            uq.save()
        self.pos = new_pos
        self.save()


class Date(models.Model):
    date = models.DateField(verbose_name="排队日期", unique=True)

    @classmethod
    def get_date(cls, date=None):
        date = date or datetime.now().date()

        return cls.objects.get_or_create(date=date)[0]

    @classmethod
    def get_que_info(cls, date):
        return cls.get_date(date).que_info

    def __str__(self):
        return str(self.date)


class UserBarCode(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="barcode")
    code = models.CharField(max_length=50, verbose_name="条形码", unique=True)
    create_date = models.ForeignKey('Date', on_delete=models.CASCADE, related_name="codes")


class UserMessage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="messages")
    message = models.CharField(max_length=200, verbose_name="用户消息")
    time = models.DateTimeField("时间")
