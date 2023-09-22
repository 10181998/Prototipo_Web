from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django import forms
from django.forms import formset_factory
from inicio.models import (Answer, Question, Learner, LearnerAnswer,Module,
                            Course, User, Announcement,Lesson,Content,Activity,Resource)

from .models import VRCard ,ResourceContent,RespuestaActividad
from django.utils.translation import gettext_lazy as _

class PostForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('content', )
        labels = {
            'content': _('Contenido'),
        }

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput())
    confirm_email = forms.EmailField(widget=forms.EmailInput(), label=_('Confirmar Email'))

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Email'),
        }

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError(
                _("¡Los correos electrónicos deben coincidir!")
            )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Email'),
        }

class InstructorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(InstructorSignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user

class LearnerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(LearnerSignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_learner = True
        user.save()
        learner = Learner.objects.create(user=user)
        return user



"""class LearnerInterestsForm(forms.ModelForm):
    class Meta:
        model = Learner
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }
"""

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeQuizForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = LearnerAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('text')

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']
        labels = {
            'title': _('Título'),
            'description': _('Descripción'),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'content_type', 'content']
        labels = {
            'title': _('Título'),
            'description': _('Descripción'),
            'content_type': _('Tipo de Contenido'),
            'content': _('Contenido'),
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['content_type', 'file']
        labels = {
            'content_type': _('Tipo de Contenido'),
            'file': _('Archivo'),
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description']
        labels = {
            'title': _('Título'),
            'description': _('Descripción'),
        }

class ResourceContentForm(forms.ModelForm):
    class Meta:
        model = ResourceContent
        fields = ['title', 'content_type', 'content']
        labels = {
            'title': _('Título'),
            'content_type': _('Tipo de Contenido'),
            'content': _('Contenido'),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['module', 'activity_type', 'title', 'description']
        labels = {
            'module': _('Módulo'),
            'activity_type': _('Tipo de Actividad'),
            'title': _('Título'),
            'description': _('Descripción'),
        }

class ClassActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['content_type', 'content']
        labels = {
            'content_type': _('Tipo de Contenido'),
            'content': _('Contenido'),
        }

class VRActivityForm(forms.ModelForm):
    vr_cards = forms.ModelMultipleChoiceField(
        queryset=VRCard.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Tarjetas VR'),
    )

    class Meta:
        model = Activity
        fields = ['vr_cards']

class VRCardForm(forms.ModelForm):
    class Meta:
        model = VRCard
        fields = ['title', 'link']
        labels = {
            'title': _('Título'),
            'link': _('Enlace'),
        }

class RespuestaActividadForm(forms.ModelForm):
    class Meta:
        model = RespuestaActividad
        fields = ['archivo_respuesta']
        labels = {
            'archivo_respuesta': _('Cargar archivo de respuesta'),
        }
        help_texts = {
            'archivo_respuesta': _('Seleccione un archivo para cargar como respuesta a la actividad.'),
        }
"""
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']
        
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description','content_type', 'content']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['content_type', 'file']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description']

class ResourceContentForm(forms.ModelForm):
    class Meta:
        model = ResourceContent
        fields = ['title', 'content_type', 'content']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['module', 'activity_type', 'title', 'description']

class ClassActivityForm(forms.ModelForm):
    
    class Meta:
        model = Activity
        fields = ['content_type', 'content']

class VRActivityForm(forms.ModelForm):
    vr_cards = forms.ModelMultipleChoiceField(
        queryset=VRCard.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Activity
        fields = ['vr_cards']
        
class VRCardForm(forms.ModelForm):
    class Meta:
        model = VRCard
        fields = ['title', 'link']
        
        

class RespuestaActividadForm(forms.ModelForm):
    class Meta:
        model = RespuestaActividad
        fields = ['archivo_respuesta']
        labels = {
            'archivo_respuesta': 'Cargar archivo de respuesta',
        }
        help_texts = {
            'archivo_respuesta': 'Seleccione un archivo para cargar como respuesta a la actividad.',
        }
        
 """       
        