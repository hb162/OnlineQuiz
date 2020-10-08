from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
import datetime
import json


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          last_login=now,
                          date_joined=now,
                          **extra_fields)
        user.staff =False
        user.admin = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self._create_user(email, password, **extra_fields)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self._create_user(email, password, **extra_fields)
        user.staff = True
        user.admin = True
        return user


class Teacher(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True, verbose_name='email address')
    date_joined = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'teacher'

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class Quiz(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    created_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.title

    @property
    def total_question(self):
        questions = self.questions_set.all()
        total = questions.count()
        return total

    @property
    def all_questions(self):
        return self.questions_set

    class Meta:
        db_table = 'quiz'


class QuizCopy1(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField(default=datetime.datetime.now())
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def total_question(self):
        questions = self.questioncopy1_set.all()
        total = questions.count()
        return total

    class Meta:
        db_table = 'quizcopy1'


class QuestionCopy1(models.Model):
    quiz1 = models.ForeignKey(QuizCopy1, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    explain = models.TextField(null=True, blank=True)
    choices = models.TextField()
    correct_choices = models.TextField()

    class Meta:
        db_table = 'questions_copy1'

    def choices_data(self):
        return json.loads(self.choices)

    def title_data(self):
        return json.loads(self.title)


class QuizCopy2(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'quiz_copy2'


class Room(models.Model):
    STATUS = (
        ('1', 'active'),
        ('0', 'deactive')
    )
    REQUIRED_NAME = (
        ('1', 'required'),
        ('0', 'not required')
    )
    SHUFFLE = (
        ('1', 'shuffle'),
        ('0', 'not shuffle')
    )

    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    quiz1 = models.ForeignKey(QuizCopy1, on_delete=models.CASCADE, blank=True, null=True)
    quiz2 = models.ForeignKey(QuizCopy2, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(choices=STATUS, default=0, max_length=1)
    required_name = models.CharField(default=0, choices=REQUIRED_NAME, max_length=1)
    is_shuffle = models.CharField(default=0, choices=SHUFFLE, max_length=1)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'room'


class Questions(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    explain = models.TextField(null=True, blank=True)
    choices = models.TextField()
    correct_choices = models.TextField()

    def __str__(self):
        return self.title

    def choices_data(self):
        return json.loads(self.choices)

    def title_data(self):
        return json.loads(self.title)

    class Meta:
        db_table = 'questions'


class ResultsTest(models.Model):
    STATUS = (
        ('1', 'active'),
        ('0', 'deactive')
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    quiz1 = models.ForeignKey(QuizCopy1, on_delete=models.CASCADE, blank=True, null=True)
    quiz2 = models.ForeignKey(QuizCopy2, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS, default=0)

    class Meta:
        db_table = 'result_test'


class ResultDetail(models.Model):
    result = models.ForeignKey(ResultsTest, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=50, null=True, blank=True)
    scores = models.IntegerField(default=0)
    student_choice = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.student_name

    @property
    def student_choice_data(self):
        return json.loads(self.student_choice)

    class Meta:
        db_table = 'result_detail'
