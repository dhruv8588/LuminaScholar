from django.urls import path

from . import views

urlpatterns = [
    path('eic_dashboard/', views.eic_dashboard, name='eic_dashboard'),
    path('awaiting_ae_assignment', views.awaiting_ae_assignment, name='awaiting_ae_assignment'),
    # path('assign_ae/paper/<paper_id>/<int:page_number>/', views.assign_ae, name='assign_ae'),

    path('select_ae/paper/<int:page_number>/', views.select_ae, name='select_ae'),

    path('ae_dashboard/', views.ae_dashboard, name='ae_dashboard'),
    
    path('awaiting_rev_selection', views.awaiting_rev_selection, name='awaiting_rev_selection'),
    path('awaiting_rev_invitation', views.awaiting_rev_invitation, name='awaiting_rev_invitation'),
    path('awaiting_rev_assignment', views.awaiting_rev_assignment, name='awaiting_rev_assignment'),
    path('awaiting_ae_recommendation', views.awaiting_ae_recommendation, name='awaiting_ae_recommendation'),

    path('rev_affairs/<str:type>/', views.rev_affairs, name="rev_affairs"),

    path('agree-to-review/<int:paper_reviewer_id>/', views.agree_to_review, name="agree_to_review"),
    path('decline-to-review/<int:paper_reviewer_id>/', views.decline_to_review, name="decline_to_review"),
]


htmx_urlpatterns = [
    path('assign_ae/paper/<int:paper_id>/', views.assign_ae, name="assign_ae"),
    path('<int:paper_id>/change_req_reviews/', views.change_req_reviews, name="change_req_reviews"),


    path('select_rev/<user_id>/paper/<int:paper_id>/', views.select_rev, name="select_rev"),

    path('sort/reviewers/', views.sort_reviewers, name='sort_reviewers'),

    path('paper/<int:paper_id>/delete-reviewer/<int:reviewer_id>/', views.delete_reviewer, name='delete_reviewer'),

    path('invite_rev/<int:paper_rev_id>/', views.invite_rev, name="invite_rev"),
    path('invite_rev_all/<int:paper_id>/', views.invite_rev_all, name="invite_rev_all"),


    path('<int:paper_id>/add_new_reviewer', views.add_new_reviewer, name='add_new_reviewer'),
    path('<int:paper_id>/add_user_as_reviewer/<int:user_id>', views.add_user_as_reviewer, name='add_user_as_reviewer'),
    path('<int:paper_id>/add_reviewer_as_reviewer/<int:reviewer_id>', views.add_reviewer_as_reviewer, name='add_reviewer_as_reviewer'),

    path('<int:paper_id>/search_user_rev', views.search_user_rev, name='search_user_rev'),

    path('<int:paper_id>/edit_reviewer/<int:reviewer_id>', views.edit_reviewer, name="edit_reviewer"),





]

urlpatterns += htmx_urlpatterns


