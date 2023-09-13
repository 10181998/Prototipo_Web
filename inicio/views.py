from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
# from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
# from .models import Customer, Profile
from .forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, UserForm, ProfileForm, PostForm #LearnerInterestsForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from .models import TakenQuiz, Profile, Quiz, Question, Answer, Learner, User, Course, Tutorial, Notes, Announcement
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                    PasswordChangeForm)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView
from .forms import ModuleForm
from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)
from .models import Course, Module, Lesson, Activity,Content,Resource
from .forms import ModuleForm,LessonForm,ContentForm,ClassActivityForm,VRActivityForm


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def login_form(request):
    return render(request, 'login.html')


def logoutView(request):
    logout(request)
    return redirect('home')


def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_instructor:
                return redirect('instructor')
            elif user.is_learner:
                return redirect('learner')
            else:
                return redirect('login_form')
        else:
            messages.info(request, "Usuario o contraseña incorrecto")
            return redirect('login_form')


# Admin Views
def dashboard(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    context = {'learner': learner, 'course': course,
            'instructor': instructor, 'users': users}

    return render(request, 'dashboard/admin/home.html', context)


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'El Profesor se agregó exitosamente')
        return redirect('isign')


class AdminLearner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'El Estudiante se agregó exitosamente')
        return redirect('addlearner')

class ListCourseView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/admin/course.html'
    context_object_name = 'course_list'
    paginated_by = 10

    def get_queryset(self):
        return Course.objects.order_by('-id')


@login_required
def course(request):
        if request.method == 'POST':
            codigo=request.POST['txtCodigo']
            name = request.POST['name']
            descripcion = request.POST['txtDescripcion']
            

            a = Course(codigo=codigo,name=name, descripcion=descripcion)
            a.save()
            messages.success(request, 'Curso creado exitosamente')
            return redirect('course')
        else:
            course=Course.objects.all()
        return render(request, 'dashboard/admin/course.html',{"course_list":course})

def crear_course(request):
    return render(request, 'dashboard/admin/crear_course.html')


@login_required
def editarCurso(request, codigo):
    course=Course.objects.get(codigo=codigo) #lee los datos 
    return render(request, 'dashboard/admin/editarCurso.html', {"course":course})

    
@login_required
def edicionCurso(request):
    codigo=request.POST['txtCodigo']
    name = request.POST['name']
    descripcion = request.POST['txtDescripcion']
    
    course=Course.objects.get(codigo=codigo)
    course.name = name
    course.descripcion = descripcion
    course.save()
    messages.success(request, '¡Curso actualizado!')
    return redirect('course')

@login_required
def eliminarCurso(request,codigo):
    course=Course.objects.get(codigo=codigo)
    course.delete()
    messages.success(request, '¡Curso eliminado!')
    return redirect('course')

"""@login_required
def detalle_curso(request,codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso
    #temas = curso.temas.all() 
    #temas = Tema.objects.all()
    return render(request, 'dashboard/admin/detalle_curso.html', {"course":course,"codigo": codigo,'modules': modules})"""


def detalle_curso(request, codigo, module_id=None):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course)
    selected_module = None

    if module_id is not None:
        selected_module = get_object_or_404(Module, id=module_id)

    return render(request,'dashboard/admin/detalle_curso.html',
        {"course": course, "codigo": codigo, "modules": modules, "selected_module": selected_module})


@login_required
def create_module(request, codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course

            # Obtener el número del siguiente módulo en la secuencia
            next_module_number = modules.count() + 1
            module.title = f"Módulo {next_module_number}"  # Establecer el nombre del módulo

            module.save()
            messages.success(request, 'Módulo creado exitosamente')
            return redirect('detalle_curso', codigo=course.codigo)  
    else:
        form = ModuleForm()
    
    return render(request, 'dashboard/admin/crear_modulo.html', {'form': form, 'course': course, 'modules': modules})

def module_list(request, codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso
    return render(request, 'dashboard/admin/detalle_curso.html', {'course': course, 'modules': modules})

def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('detalle_curso', codigo=module.course.codigo)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'dashboard/admin/edit_module.html', {'form': form, 'module': module})

def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        codigo = module.course.codigo
        module.delete()
        messages.success(request, '¡Módulo eliminado!')
        return redirect('detalle_curso', codigo=codigo)
    return render(request, 'dashboard/admin/delete_module.html', {'module': module})

def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lessons = Lesson.objects.filter(module=module)
    return render(request, 'dashboard/admin/module_detail.html', {'module': module, 'lessons': lessons})

@login_required
def create_lesson(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lección creada exitosamente')
            return redirect('module_detail', module_id=module.id)  # Cambia 'module_detail' por el nombre correcto de la vista
    else:
        form = LessonForm()
    
    return render(request, 'dashboard/admin/create_lesson.html', {'form': form, 'module': module})

def lesson_detail(request,module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'dashboard/admin/lesson_detail.html', {'lesson': lesson, 'module_id': module_id, 'lesson_id': lesson_id})


@login_required
def edit_lesson(request, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lección actualizada ')
            return redirect('module_detail', module_id=module_id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'dashboard/admin/edit_lesson.html', {'form': form, 'lesson': lesson,'lesson_id': lesson_id})


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    module_id = lesson.module.id  # Obtener el ID del módulo antes de eliminar la lección
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lección eliminada ')
        return redirect('module_detail', module_id=module_id)
    return render(request, 'dashboard/admin/delete_lesson.html', {'lesson': lesson})



class AdminCreatePost(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/admin/post_form.html'
    success_url = reverse_lazy('alpost')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class AdminListTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


class ListAllTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/list_tises.html'
    context_object_name = 'tises'
    paginated_by = 10

    def get_queryset(self):
        return Announcement.objects.order_by('-id')


class ADeletePost(SuccessMessageMixin, DeleteView):
    model = Announcement
    template_name = 'dashboard/admin/confirm_delete.html'
    success_url = reverse_lazy('alistalltise')
    success_message = "Announcement Was Deleted Successfully"  #Corregir 


class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10

    def get_queryset(self):
        return User.objects.order_by('-id')


class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "Usuario Eliminado Correctamente"


def create_user_form(request):
    return render(request, 'dashboard/admin/add_user.html')


def create_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(first_name=first_name, last_name=last_name,
                username=username, password=password, email=email, is_admin=True)
        a.save()
        messages.success(request, 'Admin creado exitosamente')
        return redirect('aluser')
    else:
        messages.error(request, 'Admin Was Not Created Successfully') #corregir 
        return redirect('create_user_form')


def acreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        bio = request.POST['bio']
        phonenumber = request.POST['phonenumber']
        city = request.POST['city']
        country = request.POST['country']
        avatar = request.FILES['avatar']
        hobby = request.POST['hobby']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, phonenumber=phonenumber, first_name=first_name,
                                                last_name=last_name, bio=bio, birth_date=birth_date, avatar=avatar, city=city, country=country)
        messages.success(request, 'Your Profile Was Created Successfully') #corregir
        return redirect('auser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/admin/create_profile.html', users)


def auser_profile(request):
    current_user = request.user
    user_id = current_user.id
    users = Profile.objects.filter(user_id=user_id)
    users = {'users': users}
    return render(request, 'dashboard/admin/user_profile.html', users)


# Instructor Views
def home_instructor(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    context = {'learner': learner, 'course': course,
            'instructor': instructor, 'users': users}

    return render(request, 'dashboard/instructor/home.html', context)


def lista_cursos(request):
    course = Course.objects.all()
    return render(request, 'dashboard/instructor/lista_cursos.html', {"course_list":course})

@login_required
def editarCurso_instructor(request, codigo):
    course=Course.objects.get(codigo=codigo) #lee los datos 
    return render(request, 'dashboard/instructor/editarCurso_instructor.html', {"course":course})

@login_required
def edicionCurso_instructor(request):
    codigo=request.POST['txtCodigo']
    name = request.POST['name']
    descripcion = request.POST['txtDescripcion']
    
    course=Course.objects.get(codigo=codigo)
    course.name = name
    course.descripcion = descripcion
    course.save()
    messages.success(request, '¡Curso actualizado!')
    return redirect('lista_cursos')



def detalle_curso_instructor(request, codigo, module_id=None):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course)
    selected_module = None

    if module_id is not None:
        selected_module = get_object_or_404(Module, id=module_id)

    return render(request,'dashboard/instructor/detalle_curso_instructor.html',
        {"course": course, "codigo": codigo, "modules": modules, "selected_module": selected_module})


@login_required
def create_module_instructor(request, codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course

            # Obtener el número del siguiente módulo en la secuencia
            next_module_number = modules.count() + 1
            module.title = f"Módulo {next_module_number}"  # Establecer el nombre del módulo

            module.save()
            messages.success(request, 'Módulo creado satisfactoriamente')
            return redirect('detalle_curso_instructor', codigo=course.codigo)  
    else:
        form = ModuleForm()
    
    return render(request, 'dashboard/instructor/crear_modulo_instructor.html', {'form': form, 'course': course, 'modules': modules})

def module_list_instructor(request, codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso
    return render(request, 'dashboard/instructor/detalle_curso_instructor.html', {'course': course, 'modules': modules})

def edit_module_instructor(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('detalle_curso_instructor', codigo=module.course.codigo)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'dashboard/instructor/edit_module_instructor.html', {'form': form, 'module': module})

def delete_module_instructor(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        codigo = module.course.codigo
        module.delete()
        messages.success(request, '¡Módulo eliminado!')
        return redirect('detalle_curso_instructor', codigo=codigo)
    return render(request, 'dashboard/instructor/delete_module_instructor.html', {'module': module})


@login_required
def module_detail_instructor(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lessons = Lesson.objects.filter(module=module)
    # Recuperar actividades para este módulo
    activities = Activity.objects.filter(module=module)

    # Recuperar los contenidos asociados a cada actividad
   
    return render(request, 'dashboard/instructor/module_detail_instructor.html', {'module': module, 'lessons': lessons,'activities': activities})

@login_required
def create_lesson_instructor(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lección creada satisfactoriamente')
            return redirect('module_detail_instructor', module_id=module.id)  
    else:
        form = LessonForm()
    
    return render(request, 'dashboard/instructor/create_lesson_instructor.html', {'form': form, 'module': module})

def lesson_detail_instructor(request,module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'dashboard/instructor/lesson_detail_instructor.html', {'lesson': lesson, 'module_id': module_id, 'lesson_id': lesson_id})


@login_required
def edit_lesson_instructor(request, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lección actualizada correctamente')
            return redirect('module_detail_instructor', module_id=module_id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'dashboard/instructor/edit_lesson_instructor.html', {'form': form, 'lesson': lesson,'lesson_id': lesson_id})


@login_required
def delete_lesson_instructor(request, module_id,lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    module_id = lesson.module.id  # Obtener el ID del módulo antes de eliminar la lección
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lección eliminada correctamente')
        return redirect('module_detail_instructor', module_id=module_id)
    return render(request, 'dashboard/instructor/delete_lesson_instructor.html', {'lesson': lesson,'module_id': module_id})


# Vista para crear una actividad

import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Module, Activity, VRCard, Tarjeta,ActivityVRCard
from .forms import ActivityForm, ClassActivityForm, VRActivityForm,VRCardForm

def create_activity_instructor(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        activity_form = ActivityForm(request.POST)

        if activity_form.is_valid():
            activity = activity_form.save(commit=False)
            activity.module = module
            activity.activity_type = request.POST['activity_type']  # Agregar el tipo de actividad

            if activity.activity_type == 'clase':
                class_form = ClassActivityForm(request.POST, request.FILES)
                if class_form.is_valid():
                    activity.content_type = class_form.cleaned_data['content_type']
                    activity.content = class_form.cleaned_data['content']
                else:
                    # Manejar errores en el formulario de actividad de clase
                    return render(request, 'dashboard/instructor/create_activity_instructor.html', {
                        'activity_form': activity_form,
                        'class_form': class_form,
                        'vr_form': VRActivityForm(),
                        'module': module,
                    })
            elif activity.activity_type == 'realidad_virtual':
                vr_form = VRActivityForm(request.POST)
                if vr_form.is_valid():
                    vr_cards = vr_form.cleaned_data.get('vr_cards')
                    activity.vr_cards.set(vr_cards)
                else:
                    print("El formulario de actividad de realidad virtual no es válido:", vr_form.errors)
                    return render(request, 'dashboard/instructor/create_activity_instructor.html', {
                        'activity_form': activity_form,
                        'class_form': ClassActivityForm(),
                        'vr_form': vr_form,
                        'module': module,
                    })

            activity.save()
            return redirect('module_detail_instructor', module_id=module.id)

    else:
        activity_form = ActivityForm()

    return render(request, 'dashboard/instructor/create_activity_instructor.html', {
        'activity_form': activity_form,
        'class_form': ClassActivityForm(),
        'vr_form': VRActivityForm(),
        'module': module,
    })


def detail_activity(request, module_id, activity_id):
    module = get_object_or_404(Module, id=module_id)
    activity = get_object_or_404(Activity, id=activity_id)

    vr_cards = ActivityVRCard.objects.filter(activity=activity)

    return render(request, 'dashboard/instructor/detail_activity.html', {'module': module, 'activity': activity, 'vr_cards': vr_cards})

def edit_activity(request, module_id, activity_id):
    module = get_object_or_404(Module, id=module_id)
    activity = get_object_or_404(Activity, id=activity_id)
    if request.method == 'POST':
        form = ClassActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('module_detail_instructor', module_id=module_id)
    else:
        form = ClassActivityForm(instance=activity)
    return render(request, 'dashboard/instructor/edit_actividad.html', {'form': form,'activity': activity})

def delete_activity(request, module_id, activity_id):
    
    activity = get_object_or_404(Activity, id=activity_id)
    module_id = activity.module.id 
    if request.method == 'POST':
        activity.delete()
        return redirect('module_detail_instructor', module_id=module_id)
    return render(request, 'dashboard/instructor/delete_actividad.html', {'activity': activity,'module_id': module_id})


def lista_actividades(request):
    # Obtén todas las actividades
    actividades = Activity.objects.all()

    return render(request, 'dashboard/instructor/module_detail_instructor.html', {'actividades': actividades})


def Act_Realidad_Virtual(request, module_id, activity_id):
    module = get_object_or_404(Module, id=module_id)
    activity = get_object_or_404(Activity, id=activity_id)
    
    #vr_cards = ActivityVRCard.objects.filter(activity=activity)
    vr_cards = VRCard.objects.all()
    return render(request, 'dashboard/instructor/Act_Realidad_Virtual.html', {'module': module, 'activity': activity, 'vr_cards': vr_cards})

"""def select_vr_card(request, module_id, activity_id, vr_card_id):
    activity = get_object_or_404(Activity, id=activity_id)
    vr_card = get_object_or_404(VRCard, id=vr_card_id)
    
    if vr_card not in activity.vr_cards.all():
        activity.vr_cards.add(vr_card)
    
    return redirect('detalle_actividad', module_id=module_id, activity_id=activity_id)"""

def select_vr_card(request, module_id, activity_id, vr_card_id):
    # Obtener la actividad específica
    activity = get_object_or_404(Activity, pk=activity_id)

    # Obtener la tarjeta VR específica
    vr_card = get_object_or_404(VRCard, pk=vr_card_id)

    # Agregar la tarjeta VR a la actividad
    activity.vr_cards.add(vr_card)

    # Redirigir a la página de detalle de actividad
    return redirect('detail_activity', module_id=module_id, activity_id=activity_id)


def eliminar_seleccion(request, module_id, activity_id, vr_card_id):
    # Obtén la instancia de la actividad
    activity = get_object_or_404(Activity, id=activity_id)
    vr_card = get_object_or_404(VRCard, id=vr_card_id)
    activity.vr_cards.remove(vr_card)
    return redirect('detail_activity', module_id=module_id, activity_id=activity_id)


def detalle_tarjeta(request, vr_card_id):
    vr_card = get_object_or_404(VRCard, id=vr_card_id)
    return render(request, 'dashboard/instructor/detalle_tarjeta.html', {'vr_card': vr_card})

def mostrar_tarjeta(request,module_id, tarjeta_seleccionada):
    module = get_object_or_404(Module, id=module_id)
    # Puedes hacer cualquier procesamiento adicional aquí si es necesario
    try:
        tarjeta = Tarjeta.objects.get(nombre=tarjeta_seleccionada)
    except Tarjeta.DoesNotExist:
        tarjeta = None
    return render(request, 'dashboard/instructor/detail_activity.html', {'module': module, 'activity': None,  'tarjeta': tarjeta})





from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource, ResourceContent
from .forms import ResourceForm, ResourceContentForm

# Vista para crear un nuevo recurso
def create_resource_instructor(request,module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        resource_form = ResourceForm(request.POST)
        if resource_form.is_valid():
            resource = resource_form.save()
            return redirect('module_detail_instructor', module_id=module.id)
    else:
        resource_form = ResourceForm()
    
    return render(request, 'dashboard/instructor/create_resource.html', {'resource_form': resource_form,'module': module})

# Vista para ver detalles de un recurso
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    return render(request, 'dashboard/instructor/resource_detail.html', {'resource': resource})

# Vista para actualizar un recurso
def edit_resource_instructor(request, resource_id,module_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        resource_form = ResourceForm(request.POST, instance=resource)
        if resource_form.is_valid():
            resource_form.save()
            return redirect('module_detail_instructor', module_id=module_id)
    else:
        resource_form = ResourceForm(instance=resource)
    
    return render(request, 'dashboard/instructor/edit_resource.html', {'resource_form': resource_form, 'resource': resource})

# Vista para eliminar un recurso
def delete_resource_instructor(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        resource.delete()
        return redirect('list_resources')
    
    return render(request, 'dashboard/instructor/delete_resource.html', {'resource': resource})

# Vista para listar todos los recursos
def list_resources(request):
    resources = Resource.objects.all()
    return render(request, 'dashboard/instructor/module_detail_instructor.html', {'resources': resources})




class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/Instructor/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(
            self.request, 'Quiz created, Go A Head And Add Questions')
        return redirect('quiz_change', quiz.pk)


class QuizUpateView(UpdateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/instructor/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(
            answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk', self.object.pk})


def question_add(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(
                request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})


def question_change(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormatSet = inlineformset_factory(
        Question,
        Answer,
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormatSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                formset.save()
                formset.save()
            messages.success(
                request, 'Question And Answers Saved Successfully')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormatSet(instance=question)
    return render(request, 'dashboard/instructor/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/instructor/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('course') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset


class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/instructor/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The Question Was Deleted Successfully')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})


class QuizResultsView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related(
            'learner__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(
            request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(
                request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})


class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'course', )
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(
            answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})


class CreatePost(CreateView):
    form_class = PostForm
    model = Announcement
    template_name = 'dashboard/instructor/post_form.html'
    success_url = reverse_lazy('llchat')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class TiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/instructor/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


def user_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users': users}
    return render(request, 'dashboard/instructor/user_profile.html', users)


def create_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, first_name=first_name, last_name=last_name,
                                                phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('user_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/instructor/create_profile.html', users)


def tutorial(request):
    courses = Course.objects.only('codigo', 'name')
    context = {'courses': courses}

    return render(request, 'dashboard/instructor/tutorial.html', context)


def publish_tutorial(request):
    if request.method == 'POST':
        title = request.POST['title']
        codigo = request.POST['txtcodigo']
        content = request.POST['content']
        thumb = request.FILES['thumb']
        current_user = request.user
        author_id = current_user.id
        print(author_id)
        print(codigo)
        a = Tutorial(title=title, content=content, thumb=thumb,
                    user_id=author_id, codigo=codigo)
        a.save()
        messages.success(request, 'Tutorial was published successfully!')
        return redirect('tutorial')
    else:
        messages.error(request, 'Tutorial was not published successfully!')
        return redirect('tutorial')


def itutorial(request):
    tutorials = Tutorial.objects.all().order_by('-created_at')
    tutorials = {'tutorials': tutorials}
    return render(request, 'dashboard/instructor/list_tutorial.html', tutorials)


class ITutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/instructor/tutorial_detail.html'


class LNotesList(ListView):
    model = Notes
    template_name = 'dashboard/instructor/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4

    def get_queryset(self):
        return Notes.objects.order_by('-id')


def iadd_notes(request):
    courses = Course.objects.only('codigo', 'name')
    context = {'courses': courses}
    return render(request, 'dashboard/instructor/add_notes.html', context)


def publish_notes(request):
    if request.method == 'POST':
        title = request.POST['title']
        codigo = request.POST['txtcodigo']
        cover = request.FILES['cover']
        file = request.FILES['file']
        current_user = request.user
        user_id = current_user.id

        a = Notes(title=title, cover=cover, file=file,
                user_id=user_id, codigo=codigo)
        a.save()
        messages.success = (request, 'Notes Was Published Successfully')
        return redirect('lnotes')
    else:
        messages.error = (request, 'Notes Was Not Published Successfully')
        return redirect('iadd_notes')


def update_file(request, pk):
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = request.FILES['file'].name

        fs = FileSystemStorage()
        file = fs.save(file.name, file)
        fileurl = fs.url(file)
        file = file_name
        print(file)

        Notes.objects.filter(id=pk).update(file=file)
        messages.success = (request, 'Notes was updated successfully!')
        return redirect('lnotes')
    else:
        return render(request, 'dashboard/instructor/update.html')


# Learner Views
def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()

    context = {'learner': learner, 'course': course,
            'instructor': instructor, 'users': users}

    return render(request, 'dashboard/learner/home.html', context)

def lista_cursos_learner(request):
    course = Course.objects.all()
    return render(request, 'dashboard/learner/lista_cursos_learner.html', {"course_list":course})


def detalle_curso_learner(request, codigo, module_id=None):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course)
    selected_module = None

    if module_id is not None:
        selected_module = get_object_or_404(Module, id=module_id)

    return render(request,'dashboard/learner/detalle_curso_learner.html',
        {"course": course, "codigo": codigo, "modules": modules, "selected_module": selected_module})


def module_list_learner(request, codigo):
    course = get_object_or_404(Course, codigo=codigo)
    modules = Module.objects.filter(course=course) # Obtener los módulos asociados al curso
    return render(request, 'dashboard/learner/detalle_curso_learner.html', {'course': course, 'modules': modules})


def module_detail_learner(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lessons = Lesson.objects.filter(module=module)
    # Recuperar actividades para este módulo
    activities = Activity.objects.filter(module=module)
    return render(request, 'dashboard/learner/module_detail_learner.html', {'module': module, 'lessons': lessons, 'activities': activities})


def lesson_detail_learner(request,module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'dashboard/learner/lesson_detail_learner.html', {'lesson': lesson, 'module_id': module_id, 'lesson_id': lesson_id})


def detail_activity_learner(request, module_id, activity_id):
    module = get_object_or_404(Module, id=module_id)
    activity = get_object_or_404(Activity, id=activity_id)

    vr_cards = ActivityVRCard.objects.filter(activity=activity)

    return render(request, 'dashboard/learner/detail_activity_learner.html', {'module': module, 'activity': activity, 'vr_cards': vr_cards})


from django.shortcuts import render, redirect
from .models import Activity, RespuestaActividad
from .forms import RespuestaActividadForm

def cargar_respuesta_actividad(request, activity_id):
    actividad = Activity.objects.get(id=activity_id)

    if request.method == 'POST':
        form = RespuestaActividadForm(request.POST, request.FILES)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.actividad = actividad
            respuesta.save()
            return redirect('detalle_actividad', module_id=actividad.module.id, activity_id=actividad.id)
    else:
        form = RespuestaActividadForm()

    return render(request, 'dashboard/learner/detail_activity_learner.html', {'form': form, 'actividad': actividad})


class LearnerSignUpView(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # return redirect('learner')
        return redirect('learner')


def ltutorial(request):
    tutorials = Tutorial.objects.all().order_by('-created_at')
    tutorials = {'tutorials': tutorials}
    return render(request, 'dashboard/learner/list_tutorial.html', tutorials)


class LLNotesList(ListView):
    model = Notes
    template_name = 'dashboard/learner/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4

    def get_queryset(self):
        return Notes.objects.order_by('-id')


class ITiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/learner/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


def luser_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users': users}
    return render(request, 'dashboard/learner/user_profile.html', users)


def lcreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, first_name=first_name, last_name=last_name,
                                                phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/learner/create_profile.html', users)


class LTutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/tutorial_detail.html'

"""
class LearnerInterestsView(UpdateView):
    model = Learner
    form_class = LearnerInterestsForm
    template_name = 'dashboard/learner/interests_form.html'
    success_url = reverse_lazy('lquiz_list')

    def get_object(self):
        return self.request.user.learner

    def form_valid(self, form):
        messages.success(self.request, 'Course Was Updated Successfully')
        return super().form_valid(form)
"""

class LQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/learner/quiz_list.html'

    """def get_queryset(self):
        learner = self.request.user.learner
        learner_interests = learner.interests.values_list('pk', flat=True)
        taken_quizzes = learner.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(course__in=learner_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset"""


class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'dashboard/learner/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.learner.taken_quizzes \
            .select_related('quiz', 'quiz__course') \
            .order_by('quiz__name')
        return queryset


def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    learner = request.user.learner

    if learner.quizzes.filter(pk=pk).exists():
        return render(request, 'dashboard/learner/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = learner.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                learner_answer = form.save(commit=False)
                learner_answer.student = learner
                learner_answer.save()
                if learner.get_unanswered_questions(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = learner.quiz_answers.filter(
                        answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round(
                        (correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(
                        learner=learner, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(
                            request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(
                            request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('lquiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'dashboard/learner/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })
