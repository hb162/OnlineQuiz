from django.shortcuts import render, redirect
from quiz.models import *
from django.core import serializers
import json

def student_sign_in(request):
    if request.method == "POST":
        room_name = request.POST['room_name']
        if Room.objects.filter(name=room_name, status=1):
            request.session['room_name'] = room_name
            request.session.set_expiry(0)
            return redirect('quiz_test')
        else:
            return render(request, 'quiz/student_sign_in.html')
    else:
        return render(request, 'quiz/student_sign_in.html')


def student_quiz_test(request):
    if request.session.has_key('room_name'):
        room_name = request.session['room_name']
        request.session.set_expiry(0)
        quiz = Quiz.objects.get(id=Room.objects.get(name=room_name).quiz_id)
        questions = quiz.questions_set.all()
        questions_detail = []
        q = dict()
        for i in questions:
            q['question_title'] = i.title
            q['choices'] = i.choices
            q['correct'] = i.correct_choices
            questions_detail.append(q)
            q = dict()
        print(questions_detail)
        questions_detail = json.dumps(questions_detail)
        print(questions_detail)
        print(type(questions_detail))
        context = {
            'room_name': room_name,
            'quiz': quiz,
            'detail': questions_detail
        }
    return render(request, 'student_quiz/student_test_quiz.html', context)

