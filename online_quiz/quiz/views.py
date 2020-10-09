from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .utils import PasswordResetTokenGenerator
from .models import *
from django.contrib.auth.hashers import check_password, make_password
from .forms import AuthenticationForm, UserCreationForm, RegistrationForm, RequestForgetPassword, ResetNewPassword, ChangePasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading
import json
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

User = get_user_model()


class EmailThreading(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


def index(request):
    return render(request, 'quiz/index.html')


def teacher_signup(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            hashed = make_password(password)
            usr = form.save()
            current_site = get_current_site(request)
            email_subject = 'Activate your Account'
            message = render_to_string('quiz/activate.html',
                                       {
                                           'user': usr,
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(usr.pk)),
                                           'token': generate_token.make_token(usr)
                                       })
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            EmailThreading(email_message).start()
            login(request, usr, backend='django.contrib.auth.backends.ModelBackend')
            messages.add_message(request, messages.INFO, 'Last step, checking your email to verify your account.')
            return redirect("index")
        else:
            context = {
                'registration_form': form
            }
    else:
        form = RegistrationForm()
        context = {
            'registration_form': form
        }
    return render(request, 'quiz/teacher_sign_up.html', context)


def activate_account(request, uidb64, token):
    if request.method == "GET":
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Teacher.objects.get(pk=uid)
        except Exception as identider:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.active = True
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Account activated succesfully.')
            return redirect('index')
        return render(request, 'quiz/activate_fail.html', status=401)


def teacher_sign_in(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user:
                if user.active:
                    login(request, user)
                    return redirect("index")
            else:
                return HttpResponse("fail")
        else:
            context = {
                'auth_form': form
            }
    else:
        form = AuthenticationForm()
        context = {
            'auth_form': form
        }
    return render(request, 'quiz/teacher_sign_in.html', context)


def teacher_log_out(request):
    logout(request)
    return redirect("teacher_sign_in")


def teacher_forgot_password(request):
    if request.method == "GET":
        form = RequestForgetPassword(data=request.GET)
        return render(request, "quiz/request_reset_password_email.html", {'form': form})
    else:
        email = request.POST['email']
        u = Teacher.objects.filter(email=email).first()
        if u:
            current_site = get_current_site(request)
            email_subject = 'Reset your Account'
            message = render_to_string('quiz/reset_password_email.html',
                                       {
                                           'user': u,
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(u.pk)),
                                           'token': PasswordResetTokenGenerator().make_token(u)
                                       })
            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            EmailThreading(email_message).start()
            messages.success(
                request, 'We have sent you an email with instructions on how to reset your password')
            return render(request, 'quiz/request_reset_password_email.html')


class SetNewPassordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = Teacher.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, "Password reset link is invalid, please request again")
                return render(request, 'quiz/request_reset_password_email.html')
        except DjangoUnicodeDecodeError:
            messages.info(request, "Invalid link")
            return render(request, 'quiz/request_reset_password_email.html')
        return render(request, 'quiz/set_new_password.html', context)

    def post(self, request, uidb64, token):
        reset_form = ResetNewPassword(data=request.POST)
        if reset_form.is_valid():
            try:
                Teacher = get_user_model()
                id = force_text(urlsafe_base64_decode(uidb64))
                user = Teacher.objects.get(id=id)
                paswd = reset_form.cleaned_data['password1']
                hashed = make_password(paswd)
                user.password = hashed
                user.save()
                return redirect('teacher_sign_in')
            except DjangoUnicodeDecodeError:
                messages.add_message(request, messages.ERROR, 'Something went wrong. Please try again.')
                return render(request, 'quiz/set_new_password.html', {'reset_form': reset_form})
        else:
            context = {
                'uidb64': uidb64,
                'token': token,
                'has_error': False,
                'reset_form': reset_form
            }
        return render(request, 'quiz/set_new_password.html', context)


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            return HttpResponse("SUCCESS")
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(request.user)
        return render(request, 'quiz/change_password.html', {'form': form})


def quizz_tab(request):
    ctx = {}
    try:
        quiz = Quiz.objects.filter(teacher_id=request.user.id)
        ctx["quiz"] = quiz
        if request.is_ajax():
            html = render_to_string(
                template_name="quiz/quiz_search_result.html", context={"quiz": quiz}
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
    except(ValueError, AttributeError):
        return HttpResponse("sai")
    return render(request, "quiz/quiz_tab.html", context=ctx)


@csrf_exempt
def add_quiz(request):
    if request.method == "POST":
        question_data = request.POST['question_data']
        quiz_data = request.POST['quiz_data']
        dict_data = json.loads(question_data)
        dict_quiz = json.loads(quiz_data)
        try:
            quiz_title = dict_quiz[0]['quiz-title']
            Quiz.objects.create(
                title=quiz_title,
                teacher_id=request.user.id
            )
            for i in dict_data:
                question_title = i['question_title']
                selector = json.dumps(i['selector'], ensure_ascii=False)
                correct = json.dumps(i['correct'], ensure_ascii=False)
                explain = i['exp']
                q_id = Quiz.objects.get(title=quiz_title).id
                Questions.objects.create(
                    title=question_title,
                    choices=selector,
                    quiz_id=q_id,
                    correct_choices=correct,
                    explain=explain
                )

        except (ValueError, AttributeError):
            return HttpResponse("error")
    else:
        print("abc")
    return render(request, 'quiz/add_quiz.html')


def quiz_detail(request, pk):
    if request.method == "GET":
        quiz = Quiz.objects.filter(id=pk)
        questions = Questions.objects.filter(quiz_id=pk)
        context = {'quiz': quiz, 'questions': questions}
        return render(request, 'quiz/quiz_detail.html', context)
    else:
        if request.method == "POST":
            question_data = json.loads(request.POST['question_data'])
            quiz_data = json.loads(request.POST['quiz_data'])
            q = Quiz.objects.get(id=pk)
            try:
                for i in quiz_data:
                    q.title = i['quiz-title']
                    q.save()
                for i in question_data:
                    question_title = i['question_title']
                    answers = json.dumps(i['selector'], ensure_ascii=False)
                    correct = i['correct']
                    explain = i['exp']
                    Questions.objects.create(title=question_title, choices=answers, correct_choices=correct, explain=explain, quiz_id=pk)
                    quiz_data = {"error": False, "error_message": "Quiz has been updated."}
                    return JsonResponse(quiz_data)
            except(ValueError, AttributeError, ConnectionAbortedError, TimeoutError):
                quiz_data = {"error": True, "error_message": "Something went wrong!."}
                return JsonResponse(quiz_data)
            return HttpResponse("gg")


@csrf_exempt
def question_detail(request, pk):
    if request.method == "GET":
        question_id = request.GET['question_id']
        q_detail = Questions.objects.filter(id=question_id)
        return render(request, 'quiz/quiz_detail.html', {'q_detail': q_detail})
    elif request.method == "POST":
        q = Questions.objects.get(id=pk)
        json_data = json.loads(request.POST['json_data'])
        try:
            for i in json_data:
                question_title = i['question_title']
                answers = json.dumps(i['answer_data'], ensure_ascii=False)
                correct = json.dumps(i['correct'], ensure_ascii=False)
                explain = i['exp']
                q.title = question_title
                q.choices = answers
                q.correct_choices = correct
                q.explain = explain
                q.save()
        except(ValueError, AttributeError, ConnectionError, ObjectDoesNotExist):
            return HttpResponse("Wrong")
        return HttpResponse("Good")


def delete_quiz(request):
    error_data = {}
    if request.is_ajax():
        list_id = json.loads(request.POST['selected_quiz'])
        try:
            for i, quiz in enumerate(list_id):
                if quiz != '':
                    quiz_del = Quiz.objects.filter(id=quiz).delete()
                    error_data = {'error': False, 'error_message': 'Quiz has been deleted.'}
                return JsonResponse(error_data)
        except(AttributeError, ValueError, ConnectionAbortedError):
            error_data = {'error': True, 'error_message': 'Id not found'}
            return HttpResponse(error_data)
    return JsonResponse("abc")


@csrf_exempt
def delete_question(request):
    question_id = request.POST['q_id']
    try:
        question = Questions.objects.get(id=question_id)
        question.delete()
        question_data = {"error": False, "error_message": "Question has been deleted."}
        return JsonResponse(question_data)
    except(ValueError, ObjectDoesNotExist):
        question_data = {"error": True, "error_message": "Question does not exist"}
        return JsonResponse(question_data)


@csrf_exempt
def rooms_tab(request):
    if request.method == "GET":
        rooms = Room.objects.filter(teacher_id=request.user.id).values('id', 'name', 'status')
        context = {'rooms': rooms}
        return render(request, 'quiz/rooms_tab.html', context)
    else:
        room_name = request.POST['room_name']
        try:
            room = Room(name=room_name, teacher_id=request.user.id, status='0')
            room.save()
            room_data = {"id": room.id, "status": room.status, "error": False,
                         "error_message": "Room create successfully."}
            return JsonResponse(room_data, safe=False)
        except (ValueError, AttributeError):
            room_data = {"error": False, "error_message": "Something went wrong!"}
            return JsonResponse(room_data, safe=False)


@csrf_exempt
def delete_room(request):
    room_id = request.POST.get("id")
    try:
        room = Room.objects.get(id=room_id)
        room.delete()
        room_data = {"error": False, "errorMessage": "Deleted Successfully"}
        return JsonResponse(room_data, safe=False)
    except (ValueError, AttributeError, ConnectionError, NameError):
        room_data = {"error": True, "errorMessage": "Failed to Delete Data"}
        return JsonResponse(room_data, safe=False)


def check_before_launch_quiz(request):
    if Room.objects.filter(status=1, teacher_id=request.user.id).first():
        warning_data = {"warning": True, "warning_message": "Would you like to stop the current quiz and start a new one?"}
        return JsonResponse(warning_data)
    else:
        warning_data = {"warning": False}
        return JsonResponse(warning_data)


@csrf_exempt
def launch_quizz(request):
    if request.method == "POST":
        quiz_title = request.POST["quiz"]
        room_name = request.POST['room']
        required_name = request.POST['req_name']
        shuffle_question = request.POST['is_shuffle']
        quiz = Quiz.objects.get(title=quiz_title)
        questions = Questions.objects.filter(quiz_id=quiz.id)
        q_filter = Questions.objects.filter(quiz_id=quiz.id).values("title", "choices", "explain", "correct_choices")
        r = Room.objects.get(name=room_name)

        try:
            if required_name == 'Yes':
                r.required_name = 1
            elif required_name == 'No':
                r.required_name = 0
                # Trường hợp không shuffle câu hỏi
            if shuffle_question == 'No':
                # Check câu hỏi và quiz có bị thay đổi không
                quiz_copy1 = QuizCopy1.objects.filter(title=quiz.title, teacher_id=request.user.id).order_by('-date').first()
                try:
                    question_copy_1 = QuestionCopy1.objects.filter(quiz1_id=quiz_copy1.id).values("title", "choices", "explain", "correct_choices")
                except(ValueError, AttributeError, ConnectionError):
                    question_copy_1 = []
                if quiz_copy1 is not None and list(question_copy_1) == list(q_filter):
                    r.quiz1_id = quiz_copy1.id
                    ResultsTest.objects.create(date=datetime.datetime.now(), quiz1_id=quiz_copy1.id, room_id=r.id,
                                               teacher_id=request.user.id, status=1)

                # Câu hỏi và quiz bị thay đổi hoặc chưa tồn tại
                else:
                    quiz_launch = QuizCopy1.objects.create(title=quiz.title, teacher_id=request.user.id)
                    for q in questions:
                        r.is_shuffle = 0
                        r.quiz1_id = quiz_launch.id
                        QuestionCopy1.objects.create(title=q.title,
                                                     explain=q.explain,
                                                     choices=q.choices,
                                                     correct_choices=q.correct_choices,
                                                     quiz1_id=quiz_launch.id)
                    ResultsTest.objects.create(date=datetime.datetime.now(), quiz1_id=quiz_launch.id, room_id=r.id,
                                               teacher_id=request.user.id, status=1)
            elif shuffle_question == 'Yes':
                r.is_shuffle = 1
                quiz_launch = QuizCopy2.objects.create(title=quiz.title)
            r.status = 1
            r.save()
            return HttpResponse("Success")

        except(ValueError, AttributeError, ConnectionError):
            return HttpResponse("error")
    else:
        quiz = Quiz.objects.filter(teacher_id=request.user.id).values('title', 'created_date')
        room = Room.objects.filter(teacher_id=request.user.id).values('id', 'name')
        context = {
            "quiz": quiz,
            "room": room
        }
    return render(request, 'quiz/launch_quiz.html', context)


def quiz_result(request):
    std_choice = ""
    result_detail = ""
    questions = ""
    q_correct = []
    list_correct = {}
    q = ""
    if request.method == "GET":
        try:
            rs = ResultsTest.objects.get(teacher_id=request.user.id, room__status=1, status=1)
            if rs.quiz1:
                q = QuizCopy1.objects.get(id=rs.quiz1.id, teacher_id=request.user.id)
                questions = QuestionCopy1.objects.filter(quiz1_id=q.id)
            elif rs.quiz2:
                q = QuizCopy2.objects.get(title=rs.quiz2.id, teacher_id=request.user.id)
                questions = QuestionCopy1.objects.filter(quiz1_id=q.id)
            for i in questions:
                i = json.loads(i.correct_choices)
                q_correct.append(i)
            for k, v in enumerate(q_correct, start=1):
                list_correct[k] = v
            # list_correct = json.dumps(list_correct)
            result_detail = ResultDetail.objects.filter(result_id=rs.id)
            context = {'result_test': rs, 'rs_detail': result_detail,
                       'std_choice': std_choice,
                       'q': q, 'question': questions, 'list_correct': list_correct}
            return render(request, 'quiz/quiz_result_single_room.html', context)
        except ResultsTest.DoesNotExist:
            rs = None
            return HttpResponse('<h1>NONE OF QUIZ IS RUNNING NOW! CLICK BACK BUTTON TO BACK TO MAIN MENU</h1>')


def end_quiz(request):
    r = Room.objects.get(teacher_id=request.user.id, status=1)
    r.quiz1_id = None
    r.quiz2_id = None
    r.required_name = 0
    r.is_shuffle = 0
    r.status = 0
    rt = ResultsTest.objects.get(room_id=r.id, teacher_id=request.user.id, status=1)
    rt.status = 0
    r.save()
    rt.save()
    return redirect('report')


def report_tab(request):
    rooms = Room.objects.all()
    rst = ResultsTest.objects.filter(status=0, teacher_id=request.user.id).order_by('-date')
    if request.method == "GET":
        context = {'result_test': rst,
                   'rooms': rooms}
        return render(request, 'quiz/report.html', context)
    else:
        room_select = request.POST['room_select']
        rp_search = request.POST['rp_search']
        q = QuizCopy1.objects.filter(title__contains=rp_search).first()
        result_filter = ResultsTest.objects.filter(Q(quiz1__title=q) | Q(quiz2__title=q), teacher_id=request.user.id, room__name=room_select)
        if result_filter:
            context = {'rooms': rooms, 'result': result_filter}
            return render(request, 'quiz/report.html', context)
        else:
            message = "Search Not Found!"
            return render(request, 'quiz/report.html', {'rooms': rooms, 'message': message})


def delete_report(request):
    rp_data = {}
    if request.is_ajax():
        list_id = json.loads(request.POST['selected_report'])
        try:
            for i, report in enumerate(list_id):
                if report != '':
                    rp_del = ResultsTest.objects.filter(id=report).delete()
                    rp_data = {'error': False, 'error_message': 'Report has been deleted.'}
                return JsonResponse(rp_data)
        except(AttributeError, ValueError, ConnectionAbortedError):
            rp_data = {'error': True, 'error_message': 'Id not found'}
            return HttpResponse(rp_data)
    return JsonResponse("abc")


def report_detail(request, pk):
    result = ResultsTest.objects.get(id=pk)
    result_detail = ResultDetail.objects.filter(result_id=pk)
    std_choice = ""
    result_detail = ""
    questions = ""
    q_correct = []
    list_correct = {}
    q = ""
    if request.method == "GET":
        try:
            rs = ResultsTest.objects.get(id=pk, status=0)
            if rs.quiz1:
                q = QuizCopy1.objects.get(id=rs.quiz1.id, teacher_id=request.user.id)
                questions = QuestionCopy1.objects.filter(quiz1_id=q.id)
            elif rs.quiz2:
                q = QuizCopy2.objects.get(title=rs.quiz2.id, teacher_id=request.user.id)
                questions = QuestionCopy1.objects.filter(quiz1_id=q.id)
            for i in questions:
                i = json.loads(i.correct_choices)
                q_correct.append(i)
            for k, v in enumerate(q_correct, start=1):
                list_correct[k] = v
            result_detail = ResultDetail.objects.filter(result_id=rs.id)

            context = {'rs': rs, 'rs_detail': result_detail,
                       'std_choice': std_choice,
                       'q': q, 'question': questions, 'list_correct': list_correct}
            return render(request, 'quiz/report_detail.html', context)

        except ResultsTest.DoesNotExist:
            pass
    context = {'rs_detail': result_detail, 'rs': result}
    return render(request, 'quiz/report_detail.html', context)
