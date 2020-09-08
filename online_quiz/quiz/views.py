from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .utils import PasswordResetTokenGenerator
from .models import *
from django.contrib.auth.hashers import check_password, make_password
from .forms import AuthenticationForm, UserCreationForm, RegistrationForm, RequestForgetPassword, ResetNewPassword
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading
import json

User = get_user_model()


class EmailThreading(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


def index(request):
    quiz = Quiz.objects.filter(teacher_id=request.user.id)
    room = Room.objects.filter(teacher_id=request.user.id)
    context = {
        "quiz": quiz,
        "room": room
    }
    return render(request, 'quiz/index.html', context)


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


def quiz_detail(request, id):
    context = {}
    quiz = Quiz.objects.filter(teacher_id=request.user.id).get(id=id)
    questions = Questions.objects.filter(quiz_id=quiz.id)
    context = {'quiz': quiz, 'questions': questions}
    return render(request, 'quiz/quiz_detail.html', context)


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
                question_title = json.dumps(i['question_title'], ensure_ascii=False)
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


@csrf_exempt
def rooms_tab(request):
    if request.method == "GET":
        rooms = Room.objects.filter(teacher_id=request.user.id)
        context = {'rooms': rooms}
        return render(request, 'quiz/rooms_tab.html', context)
    else:
        room_name = request.POST['room_name']
        try:
            if Room.objects.filter(name=room_name):
                room_data = {"error": True, "error_message": "Room name has been exists"}
                return JsonResponse(room_data, safe=False)
            else:
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


def launch_quizz(request):
    global q1
    if request.method == "POST":
        quiz_title = request.POST["quiz"]
        room_name = request.POST['room']
        required_name = request.POST['req_name']
        shuffle_question = request.POST['is_shuffle']
        quiz = Quiz.objects.get(title=quiz_title)
        try:
            questions = Questions.objects.filter(quiz_id=quiz.id)
            r = Room.objects.get(name=room_name)
            if required_name == 'Yes':
                r.required_name = 1
            if shuffle_question == 'No':
                q1 = QuizCopy1.objects.create(title=quiz.title)
                for q in questions:
                    QuestionCopy1.objects.create(title=q.title,
                                                 explain=q.explain,
                                                 choices=q.choices,
                                                 correct_choices=q.correct_choices,
                                                 quiz1_id=q1.id)
                ResultsTest.objects.create(date=datetime.datetime.now(), quiz_id=quiz.id, room_id=r.id,
                                           teacher_id=request.user.id, status=1)
            print(q1.id)
            r.quiz1_id = q1.id
            r.status = 1
            r.save()
            return HttpResponse("Success")
        except(ValueError, AttributeError, ConnectionError):
            return HttpResponse("error")
    else:
        quiz = Quiz.objects.filter(teacher_id=request.user.id)
        room = Room.objects.filter(teacher_id=request.user.id)
        context = {
            "quiz": quiz,
            "room": room
        }
    return render(request, 'quiz/launch_quiz.html', context)


def quiz_result(request):
    if request.method == "GET":
        rs = ResultsTest.objects.filter(teacher_id=request.user.id, room__status=1)
        s = []
        for result in rs:
            s.append(result)
        return render(request, 'quiz/quiz_result.html', {'s': s})


def report_tab(request):
    return render(request, 'quiz/report.html')
