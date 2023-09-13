from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django import forms
from django.forms import formset_factory
from inicio.models import (Answer, Question, Learner, LearnerAnswer,Module,
                            Course, User, Announcement,Lesson,Content,Activity,Resource)




class PostForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('content', )

class ProfileForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.EmailInput())
    confirm_email=forms.EmailField(widget=forms.EmailInput())

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',

        ]

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError(
                "Emails must match!"
            )



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email') 


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
    """interests = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )"""

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
        #learner.interests.add(*self.cleaned_data.get('interests'))
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

"""
class LearnerCourse(forms.ModelForm):
    class Meta:
        model = Learner
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }

    @transaction.atomic
    def save(self):
        learner = Learner()
        learner.interests.add(*self.cleaned_data.get('interests'))
        return learner_id
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

class ResourceContentForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description']
    
    contents = forms.ModelMultipleChoiceField(
        queryset=Content.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Esto permite que el campo sea opcional
    )

# Esto es un formset que combina el formulario de recursos y el formulario de contenido
ResourceContentFormSet = forms.modelformset_factory(
    Resource,
    form=ResourceContentForm,
    extra=1,  # Puedes cambiar esto dependiendo de cuántos formularios de recursos deseas mostrar inicialmente
)
"""
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['module', 'activity_type', 'title', 'description']

class ClassActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['content_type', 'content']

class VRActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = []  # Agrega los campos específicos de la actividad de realidad virtual aquí
"""
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['module', 'activity_type', 'title', 'description']

class ClassActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['content_type', 'content']

class VRActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['vr_game_title', 'vr_game_link']