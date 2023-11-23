from django.urls import path

from . import views

urlpatterns = [
    # path('awaiting_ae_assignment', views.awaiting_ae_assignment, name='awaiting_ae_assignment'),

    path('select_ae/paper/<int:paper_id>/', views.select_ae, name='select_ae'),
    
    path('papers-awaiting-reviewer-selection', views.display_papers_awaiting_reviewer_selection, name='awaiting_reviewer_selection'),
    path('papers-awaiting-reviewer-invitation', views.display_papers_awaiting_reviewer_invitation, name='awaiting_reviewer_invitation'),
    path('papers-awaiting-reviewer-assignment', views.display_papers_awaiting_reviewer_assignment, name='awaiting_reviewer_assignment'),
    path('papers-awaiting-ae-recommendation', views.display_papers_awaiting_ae_recommendation, name='awaiting_ae_recommendation'),
    path('papers-submitted-ae-recommendation', views.display_papers_submitted_ae_recommendation, name='submitted_ae_recommendation'),

    path('papers-awaiting-ae-selection', views.display_papers_awaiting_ae_selection, name='awaiting_ae_selection'),
    path('papers-awaiting-ae-assignment', views.display_papers_awaiting_ae_assignment, name='awaiting_ae_assignment'),
    path('papers-awaiting-eic-decision', views.display_papers_awaiting_eic_decision, name='awaiting_eic_decision'),
    path('papers-submitted-eic-decision', views.display_papers_submitted_eic_decision, name='submitted_eic_decisions'),

    path('rev_affairs/<str:type>/', views.rev_affairs, name="rev_affairs"),
    path('ae_recommendation/', views.ae_recommendation, name='ae_recommendation'),
    path('eic-decision', views.eic_decision, name='eic_decision'),

    path('ae_affairs/<str:type>/', views.ae_affairs, name="ae_affairs"),

    path('agree-to-review/<int:paper_reviewer_id>/', views.agree_to_review, name="agree_to_review"),
    path('decline-to-review/<int:paper_reviewer_id>/', views.decline_to_review, name="decline_to_review"),

    path('view_review/<int:paper_reviewer_id>/', views.view_review, name='view_review'),
    path('view_recommendation/<int:aerecommendation_id>/', views.view_recommendation, name='view_recommendation'),
]


htmx_urlpatterns = [
    path('<int:paper_id>/change_req_reviews/', views.change_req_reviews, name="change_req_reviews"),


    path('select_rev/<user_id>/paper/<int:paper_id>/', views.select_rev, name="select_rev"),

    path('sort/reviewers/', views.sort_reviewers, name='sort_reviewers'),

    path('paper/<int:paper_id>/delete-reviewer/<int:reviewer_id>/', views.delete_reviewer, name='delete_reviewer'),
    path('remove-reviewer/<int:paper_reviewer_id>', views.remove_reviewer, name='remove_reviewer'),

    path('invite_rev/<int:paper_rev_id>/', views.invite_rev, name="invite_rev"),
    path('invite_rev_all/<int:paper_id>/', views.invite_rev_all, name="invite_rev_all"),

    path('add_alternate_reviewer/<int:paper_reviewer_id>', views.add_alternate_reviewer, name='add_alternate_reviewer'),

    path('<int:paper_id>/add_new_reviewer', views.add_new_reviewer, name='add_new_reviewer'),
    path('<int:paper_id>/add_user_as_reviewer/<int:user_id>', views.add_user_as_reviewer, name='add_user_as_reviewer'),
    path('<int:paper_id>/add_reviewer_as_reviewer/<int:reviewer_id>', views.add_reviewer_as_reviewer, name='add_reviewer_as_reviewer'),

    path('add-preference-reviewer/<int:paper_reviewer_id>', views.add_preference_reviewer, name='add_preference_reviewer'),

    path('<int:paper_id>/search_user_rev', views.search_user_rev, name='search_user_rev'),

    path('<int:paper_id>/edit_reviewer/<int:reviewer_id>', views.edit_reviewer, name="edit_reviewer"),

    path('<int:paper_id>/save_recommendation', views.save_recommendation, name='save_recommendation'),
    path('<int:paper_id>/submit_recommendation', views.submit_recommendation, name='submit_recommendation'),

    path('<int:paper_id>/save_decision', views.save_decision, name='save_decision'),
    path('<int:paper_id>/submit_decision', views.submit_decision, name='submit_decision'),

    path('<int:recommendation_id>/upload-ae-files/', views.upload_ae_files, name='upload_ae_files'),

    path('<int:recommendation_id>/delete-ae-file/<int:file_id>', views.delete_ae_file, name='delete_ae_file'),

    path('<int:decision_id>/save-eic-files/', views.save_decision_files, name='save_eic_files'),

    path('<int:decision_id>/delete-eic-file/<int:file_id>', views.delete_decision_file, name='delete_eic_file'),






]

urlpatterns += htmx_urlpatterns


