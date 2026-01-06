from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_project, name='create_project'),
    path('<uuid:pk>/', views.project_detail, name='project_detail'),
    path('<uuid:pk>/delete/', views.delete_project, name='delete_project'),
    path('<uuid:pk>/duplicate/', views.duplicate_project_view, name='duplicate_project'),
    path('<uuid:pk>/flow-debug/', views.flow_debug, name='flow_debug'),
    path('<uuid:pk>/wizard/', views.project_wizard, name='project_wizard'),
    path('<uuid:pk>/summary/', views.project_summary, name='project_summary'),
    path('<uuid:pk>/generate/', views.project_generate, name='project_generate'),
    path('<uuid:pk>/blueprint/', views.project_blueprint, name='project_blueprint'),
    path('<uuid:pk>/docs/', views.project_docs, name='project_docs'),
    path('<uuid:pk>/get_task_help/', views.get_task_help, name='get_task_help'),
]