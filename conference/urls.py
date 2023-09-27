from django.urls import path

from . import views

urlpatterns = [
    path('view_papers/', views.view_papers, name='view_papers'),
    path('paper/<int:paper_id>/add_reviewer/', views.add_reviewer, name='add_reviewer'),
    path('paper/<int:paper_id>/add_new_reviewer/', views.add_new_reviewer, name='add_new_reviewer'),
    path('paper/<int:paper_id>/edit_reviewer/<int:reviewer_id>/', views.edit_reviewer, name='edit_reviewer'),
    path('paper/<int:paper_id>/delete_reviewer/<int:reviewer_id>/', views.delete_reviewer, name='delete_reviewer'),
    path('paper/<int:paper_id>/reviewer/<int:reviewer_id>/', views.reviewer_info, name='reviewer_info'),
    

    path('eic_dashboard/', views.eic_dashboard, name='eic_dashboard'),
    path('awaiting_ae_assignment', views.awaiting_ae_assignment, name='awaiting_ae_assignment'),
    # path('assign_ae/paper/<paper_id>/<int:page_number>/', views.assign_ae, name='assign_ae'),

    path('select_ae/paper/<int:page_number>/', views.select_ae, name='select_ae'),

    path('ae_dashboard/', views.ae_dashboard, name='ae_dashboard'),
    path('awaiting_reviewer_selection', views.awaiting_reviewer_selection, name='awaiting_reviewer_selection'),
    path('awaiting_reviewer_invitation', views.awaiting_reviewer_invitation, name='awaiting_reviewer_invitation'),
    path('awaiting_reviewer_assignment', views.awaiting_reviewer_assignment, name='awaiting_reviewer_assignment'),


]

htmx_urlpatterns = [
    path('assign_ae/paper/<int:paper_id>/', views.assign_ae, name="assign_ae")
]

urlpatterns += htmx_urlpatterns


