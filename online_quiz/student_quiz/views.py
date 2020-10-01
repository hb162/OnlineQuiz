from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import StudentSignIn
from quiz.models import *
from django.core import serializers
import json
import random
from django.contrib import messages
from django.contrib.auth import logout


@csrf_exempt
def sign_in_with_name(request):
    if request.session.has_key('room_name'):
        room_name = request.session['room_name']
        if request.method == "POST":
            room = Room.objects.get(name=room_name)
            std_name = request.POST['std-name']
            rst = ResultsTest.objects.get(room_id=room.id, status="1")
            if ResultDetail.objects.filter(student_name=std_name, result_id=rst.id).first():
                err = messages.error(request, 'Name has already taken.')
                return JsonResponse({'error': err}, status=400)
                # return render(request, 'student_quiz/student_name.html', {'room_name': room_name})
            ResultDetail.objects.create(student_name=std_name, result_id=rst.id)
            request.session['student_name'] = std_name
            return redirect('quiz_test')
        else:
            return render(request, 'student_quiz/student_name.html', {'room_name': room_name})


def student_sign_in(request):
    if request.method == "POST":
        form = StudentSignIn(request.POST)
        logout(request)
        if form.is_valid():
            room_name = form.cleaned_data['room_name']
            room = Room.objects.filter(name=room_name, status=1).first()
            if room:
                request.session['room_name'] = room_name
                if room.required_name == '0':
                    i = str(random.randint(0, 999999))
                    student_name = 'Student' + i
                    rst = ResultsTest.objects.get(room_id=room.id, room__status=1, status=1)
                    ResultDetail.objects.create(student_name=student_name, result_id=rst.id)
                    request.session['student_name'] = student_name
                    request.session.set_expiry(0)
                    return redirect('quiz_test')
                else:
                    return redirect('sign_in_name')
            else:
                form = StudentSignIn()
                messages.error(request, "room doesn't exit")
                return render(request, 'quiz/student_sign_in.html', {'form': form})

    else:
        form = StudentSignIn()
        return render(request, 'quiz/student_sign_in.html', {'form': form})


def student_quiz_test(request):
    if request.session.has_key('room_name'):
        room_name = request.session['room_name']
        std_name = request.session['student_name']
        room = Room.objects.get(name=room_name)
        questions = ""
        if room.is_shuffle == 1:
            quiz = QuizCopy2.objects.get(id=room.quiz2_id)
        else:
            quiz = QuizCopy1.objects.get(id=room.quiz1_id)
            questions = quiz.questioncopy1_set.all()
        questions_detail = []
        q = dict()
        for i in questions:
            q['question_title'] = i.title
            q['choices'] = json.loads(i.choices)
            q['correct'] = json.loads(i.correct_choices)
            questions_detail.append(q)
            q = dict()
        questions_detail = json.dumps(questions_detail)

        context = {
            'room_name': room_name,
            'quiz': quiz,
            'detail': questions_detail
        }
    return render(request, 'student_quiz/student_test_quiz.html', context)


@csrf_exempt
def student_answer(request):
    if request.session.has_key('student_name'):
        std_name = request.session['student_name']
        if request.method == "POST":
            score = request.POST['score']
            dict_student_ans = json.loads(request.POST["student_answer_data"])
            try:
                std = ResultDetail.objects.get(student_name=std_name)
                std.scores = score
                std.student_choice = json.dumps(dict_student_ans, ensure_ascii=False)
                std.save()
                return HttpResponse("Success")
            except(ValueError, AttributeError):
                return HttpResponse("Something went wrong")
        return HttpResponse("Fail")


def student_log_out(request):
    del request.session['student_name']
    del request.session['room_name']
    return redirect('student_sign_in')


def finish_quiz(request):
    return render(request, 'student_quiz/finish_quiz.html')
