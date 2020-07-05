from django.db import models


class Teacher(models.Model):
    role = (
        ('1', 'Teacher'),
        ('2', 'Administrator'),
        ('3', 'IT/Technology'),
        ('4', 'Orther')
    )
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    roles = models.CharField(max_length=1, choices=role)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.username


class Student(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.username


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    results = models.ManyToManyField(Student, through='Results')

    def __str__(self):
        return self.title


class Questions(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="choice")
    choice = models.CharField(max_length=255)


class Results(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    scores = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField()
