from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [

# Shared URLs
path('', views.home, name='home'),
path('about/', views.about, name='about'),
path('contact/', views.contact, name='contact'),
path('lsign/', views.LearnerSignUpView.as_view(), name='lsign'),
path('login_form/', views.login_form, name='login_form'),
path('login/', views.loginView, name='login'),
path('logout/', views.logoutView, name='logout'),


# Admin URLs
path('dashboard/', views.dashboard, name='dashboard'),
path('course/', views.course, name='course'),
path('crear_course/', views.crear_course, name='crear_course'),

path('course/eliminarCurso/<codigo>', views.eliminarCurso),
path('edicionCurso/', views.edicionCurso),
path('course/editarCurso/<codigo>', views.editarCurso),
path('course/detalle_curso/<codigo>/', views.detalle_curso,name='detalle_curso'),
path('course/<codigo>/create_module/', views.create_module, name='create_module'),
#path('course/list/', views.module_list, name='module_list'),
path('module/<int:module_id>/edit/', views.edit_module, name='edit_module'),
path('module/<int:module_id>/delete/', views.delete_module, name='delete_module'),
path('module/<int:module_id>/content/', views.module_detail, name='module_detail'),
path('module/<int:module_id>/create_lesson/', views.create_lesson, name='create_lesson'),
path('module/<int:module_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
path('module/<int:module_id>/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
path('module/<int:module_id>/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),

path('isign/', views.InstructorSignUpView.as_view(), name='isign'),
path('addlearner/', views.AdminLearner.as_view(), name='addlearner'),
path('apost/', views.AdminCreatePost.as_view(), name='apost'),
path('alpost/', views.AdminListTise.as_view(), name='alpost'),
path('alistalltise/', views.ListAllTise.as_view(), name='alistalltise'),
path('adpost/<int:pk>', views.ADeletePost.as_view(), name='adpost'),
path('aluser/', views.ListUserView.as_view(), name='aluser'),
path('aduser/<int:pk>', views.ADeleteuser.as_view(), name='aduser'),
path('create_user_form/', views.create_user_form, name='create_user_form'),
path('create_user/', views.create_user, name='create_user'),
path('acreate_profile/', views.acreate_profile, name='acreate_profile'),
path('auser_profile/', views.auser_profile, name='auser_profile'),



# Instructor URLs
path('instructor/', views.home_instructor, name='instructor'),

path('lista_cursos/', views.lista_cursos, name='lista_cursos'),
path('lista_cursos/editarCurso_instructor/<codigo>', views.editarCurso_instructor),
path('edicionCurso_instructor/', views.edicionCurso_instructor),
path('lista_cursos/detalle_curso_instructor/<codigo>/', views.detalle_curso_instructor,name='detalle_curso_instructor'),
path('lista_cursos/<codigo>/create_module_instructor/', views.create_module_instructor, name='create_module_instructor'),
#path('course/list/', views.module_list, name='module_list'),
path('module_instructor/<int:module_id>/editar/', views.edit_module_instructor, name='edit_module_instructor'),
path('module_instructor/<int:module_id>/eliminar/', views.delete_module_instructor, name='delete_module_instructor'),
path('module_instructor/<int:module_id>/contenido/', views.module_detail_instructor, name='module_detail_instructor'),
path('module_instructor/<int:module_id>/create_lesson/', views.create_lesson_instructor, name='create_lesson_instructor'),
path('module_instructor/<int:module_id>/lesson_instructor/<int:lesson_id>/', views.lesson_detail_instructor, name='lesson_detail_instructor'),
path('module_instructor/<int:module_id>/lesson_instructor/<int:lesson_id>/eliminar/', views.delete_lesson_instructor, name='delete_lesson_instructor'),
path('module_instructor/<int:module_id>/lesson_instructor/<int:lesson_id>/editar/', views.edit_lesson_instructor, name='edit_lesson_instructor'),

path('module_instructor/<int:module_id>/create_activity_instructor/', views.create_activity_instructor, name='create_activity_instructor'),
#path('module_instructor/<int:module_id>/activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
#path('module_instructor/<int:module_id>/activity/<int:activity_id>/edit/', views.edit_activity_instructor, name='edit_activity_instructor'),
#path('module_instructor/<int:module_id>/activity/<int:activity_id>/delete/', views.delete_activity_instructor, name='delete_activity_instructor'),
#path('module_instructor/<int:module_id>/list_activities/', views.list_activities, name='list_activities'),
#path('module_instructor/<int:module_id>/create_class_activity/', views.create_class_activity, name='create_class_activity'),
 # Ruta para crear una actividad de realidad virtual en un módulo
#path('module_instructor/<int:module_id>/create_vr_activity/', views.create_vr_activity, name='create_vr_activity'),

path('module_instructor/<int:module_id>/create_resource/', views.create_resource_instructor, name='create_resource_instructor'),
#path('module_instructor/<int:module_id>/edit/<int:resource_id>/', views.edit_resource_instructor, name='edit_resource_instructor'),
#path('module_instructor/<int:module_id>/delete/<int:resource_id>/', views.delete_resource_instructor, name='delete_resource_instructor'),
path('module_instructor/<int:module_id>/resources/', views.resource_list, name='resource_list'),





path('quiz_add/', views.QuizCreateView.as_view(), name='quiz_add'),
path('question_add/<int:pk>', views.question_add, name='question_add'),
path('quiz/<int:quiz_pk>/<int:question_pk>/', views.question_change, name='question_change'),
path('llist_quiz/', views.QuizListView.as_view(), name='quiz_change_list'),
path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
path('quiz/<int:pk>/results/', views.QuizResultsView.as_view(), name='quiz_results'),
path('quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
path('quizupdate/<int:pk>/', views.QuizUpdateView.as_view(), name='quiz_change'),
path('ipost/', views.CreatePost.as_view(), name='ipost'),
path('llchat/', views.TiseList.as_view(), name='llchat'),
path('user_profile/', views.user_profile, name='user_profile'),
path('create_profile/', views.create_profile, name='create_profile'),
path('tutorial/', views.tutorial, name='tutorial'),
path('post/',views.publish_tutorial,name='publish_tutorial'),
path('itutorial/',views.itutorial,name='itutorial'),
path('itutorials/<int:pk>/', views.ITutorialDetail.as_view(), name = "itutorial-detail"),
path('listnotes/', views.LNotesList.as_view(), name='lnotes'),
path('iadd_notes/', views.iadd_notes, name='iadd_notes'),
path('publish_notes/', views.publish_notes, name='publish_notes'),
path('update_file/<int:pk>', views.update_file, name='update_file'),




# Learner URl's
path('learner/',views.home_learner,name='learner'),
path('lista_cursos_learner/', views.lista_cursos_learner, name='lista_cursos_learner'),
path('lista_cursos_learner/detalle_curso_learner/<codigo>/', views.detalle_curso_learner,name='detalle_curso_learner'),


path('module_learner/<int:module_id>/contenido/', views.module_detail_learner, name='module_detail_learner'),
path('module_learner/<int:module_id>/lesson_learner/<int:lesson_id>/', views.lesson_detail_learner, name='lesson_detail_learner'),


path('ltutorial/',views.ltutorial,name='ltutorial'),
path('llistnotes/', views.LLNotesList.as_view(), name='llnotes'),
path('ilchat/', views.ITiseList.as_view(), name='ilchat'),
path('luser_profile/', views.luser_profile, name='luser_profile'),
path('lcreate_profile/', views.lcreate_profile, name='lcreate_profile'),
path('tutorials/<int:pk>/', views.LTutorialDetail.as_view(), name = "tutorial-detail"),
#path('interests/', views.LearnerInterestsView.as_view(), name='interests'),
path('learner_quiz/', views.LQuizListView.as_view(), name='lquiz_list'),
path('taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),







































]
