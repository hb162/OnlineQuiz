from django.urls import path
from . import views

urlpatterns = [
    path('sign_in/', views.student_sign_in, name='student_sign_in'),
    path('quiz/', views.student_quiz_test, name='quiz_test'),
    path('sign_in/name', views.sign_in_with_name, name='sign_in_name'),
    path('quiz/finish_quiz/', views.student_answer, name='finish_quiz'),
    path('quiz/wait/', views.finish_quiz, name='wait_after_finish'),
    path('student/log_out', views.student_log_out, name='std_logout'),
]

