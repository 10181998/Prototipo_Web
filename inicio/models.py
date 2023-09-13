from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.contrib.auth import get_user_model
#from embed_video.fields import EmbedVideoField
import os


class User(AbstractUser):
    is_learner = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to = '', default = 'no-img.jpg', blank=True)
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    email = models.EmailField(default='none@email.com')
    phonenumber = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(default='1975-12-12')
    bio = models.TextField(default='')
    city = models.CharField(max_length=255, default='')
    state = models.CharField(max_length=255, default='')
    country = models.CharField(max_length=255, default='')
    favorite_animal = models.CharField(max_length=255, default='')
    hobby = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.user.username



class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return str(self.content)


class Course(models.Model):
    codigo=models.CharField(primary_key=True, max_length=6 )
    name = models.CharField(max_length=200)
    descripcion = models.TextField()
    

    def __str__(self):
        return self.name

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

class Content(models.Model):
    title = models.CharField(max_length=150)
    content_type_choices = [
        ('video', 'Video'),
        ('link', 'Link'),
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('ppt', 'PowerPoint'),
        ('xls', 'Excel'),
        
    ]
    content_type = models.CharField(max_length=10, choices=content_type_choices)
    file = models.FileField(upload_to='content_files/', blank=True, null=True)
    

    def get_content_filename(self):
        return os.path.basename(self.content.name)
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    content_type_choices = [
        ('video', 'Video'),
        ('link', 'Link'),
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('ppt', 'PowerPoint'),
        ('xls', 'Excel'),
        
    ]
    content_type = models.CharField(max_length=10, choices=content_type_choices)
    content = models.FileField(upload_to='lesson_content/', blank=True, null=True)
    """contents = models.ManyToManyField(Content, blank=True)"""
    
    def get_content_filename(self):
        return os.path.basename(self.content.name)

    def __str__(self):
        return self.title
    


class Activity(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    ACTIVITY_TYPE_CHOICES = [
        ('clase', 'Actividad de Clase'),
        ('realidad_virtual', 'Actividad de Realidad Virtual'),
    ]
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    title = models.CharField(max_length=150)
    description = models.TextField()

    # Campos específicos para Actividad de Clase
    content_type_choices = [
        ('video', 'Video'),
        ('link', 'Link'),
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('ppt', 'PowerPoint'),
        ('xls', 'Excel'),
    ]
    content_type = models.CharField(max_length=10, choices=content_type_choices)
    content = models.FileField(upload_to='activity_content/', blank=True, null=True)

    # Campos específicos para Actividad de Realidad Virtual
    vr_game_title = models.CharField(max_length=150, blank=True, null=True)
    vr_game_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    
class Resource(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    contents = models.ManyToManyField(Content, blank=True)

    def __str__(self):
        return self.title
    
    
class Tutorial(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    thumb = models.ImageField(upload_to='', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    video = EmbedVideoField(blank=True, null=True)


class Notes(models.Model):
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to='', null=True, blank=True)
    cover = models.ImageField(upload_to='', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.file.delete()
        self.cover.delete()
        super().delete(*args, **kwargs)    

  

class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    interests = models.ManyToManyField(Course, related_name='interested_learners')

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username



class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interest = models.ManyToManyField(Course, related_name="more_locations")


class TakenQuiz(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)



class LearnerAnswer(models.Model):
    student = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')    