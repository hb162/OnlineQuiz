from django.contrib import admin

# Register your models here.
from quiz.models import *
admin.site.register(Teacher)
admin.site.register(Quiz)
admin.site.register(Room)
admin.site.register(Subject)
admin.site.register(Questions)
