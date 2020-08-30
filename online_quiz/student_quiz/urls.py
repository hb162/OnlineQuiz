from django.urls import path
from . import views

urlpatterns = [
    path('sign_in/', views.student_sign_in, name='student_sign_in'),
    path('quiz/', views.student_quiz_test, name='quiz_test'),
]

