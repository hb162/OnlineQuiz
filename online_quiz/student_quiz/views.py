from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import StudentSignIn
from quiz.models import *
from django.core import serializers
import json
import random


@csrf_exempt
def sign_in_with_name(request):
    if request.session.has_key('room_name'):
        room_name = request.session['room_name']
        if request.method == "POST":
            room = Room.objects.get(name=room_name)
            std_name = request.POST['std-name']
            rst = ResultsTest.objects.get(room_id=room.id,
                                          status="1")
            ResultDetail.objects.create(student_name=std_name, result_id=rst.id)
            return redirect('quiz_test')
        else:
            return render(request, 'student_quiz/student_name.html', {'room_name': room_name})


def student_sign_in(request):
    if request.method == "POST":
        form = StudentSignIn(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['room_name']
            room = Room.objects.get(name=room_name, status=1)
            if room:
                request.session['room_name'] = room_name
                request.session.set_expiry(0)
                if room.required_name == '0':
                    i = str(random.randint(0, 999999))
                    rst = ResultsTest.objects.get(room_id=room.id, room__status=1, teacher_id=request.user.id, status=1)
                    ResultDetail.objects.create(student_name='Student' + i, result_id=rst.id)
                    return redirect('quiz_test')
                else:
                    return redirect('sign_in_name')
            else:
                return render(request, 'quiz/student_sign_in.html', {'form': form})
    else:
        form = StudentSignIn()
        return render(request, 'quiz/student_sign_in.html', {'form': form})


def student_quiz_test(request):
    if request.session.has_key('room_name'):
        room_name = request.session['room_name']
        request.session.set_expiry(0)
        quiz = Quiz.objects.get(id=Room.objects.get(name=room_name).quiz_id)
        questions = quiz.questions_set.all()
        questions_detail = []
        q = dict()
        for i in questions:
            q['question_title'] = json.loads(i.title)
            q['choices'] = json.loads(i.choices)
            q['correct'] = json.loads(i.correct_choices)
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
