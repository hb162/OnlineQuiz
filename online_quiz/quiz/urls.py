from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('teacher/home', views.index, name='index'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('teacher_signin/', views.teacher_sign_in, name='teacher_sign_in'),
    path('activate/<uidb64>/<token>', views.activate_account, name='activate'),
    path('teacher_logout/', views.teacher_log_out, name='teacher_logout'),
    path('request_reset/', views.teacher_forgot_password, name='request_reset'),
    path('reset_password/<uidb64>/<token>', views.SetNewPassordView.as_view(), name='set_new_password'),
    path('teacher/change_password', views.change_password, name='change_password'),
    path('teacher/quizzes/', views.quizz_tab, name='quizzes'),
    path('teacher/question_detail/<int:pk>/', views.question_detail, name='question_detail'),
    path('teacher/rooms/', views.rooms_tab, name='rooms'),
    path('teacher/quizzes/add_quiz/', views.add_quiz, name='add_quiz'),
    path('teacher/quizzes/delete_quiz', views.delete_quiz, name='delete_quiz'),
    path('teacher/quizzes/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('teacher/quizzes/delete_questions/', views.delete_question, name='delete_question'),
    path('rooms/delete/', views.delete_room, name='delete_room'),
    path('teacher/check_launch_quiz/', views.check_before_launch_quiz, name='check_launch'),
    path('teacher/launch_quiz/', views.launch_quizz, name='launch_quiz'),
    path('teacher/quiz_result/', views.quiz_result, name='quiz_result'),
    path('teacher/report/', views.report_tab, name='report'),
    path('teacher/end_quiz', views.end_quiz, name='end_quiz'),
    path('teacher/report/delete_quiz', views.delete_report, name='delete_report'),
    path('teacher/report/<int:pk>', views.report_detail, name='report_detail'),
]
