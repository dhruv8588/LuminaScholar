from django.urls import path, re_path

from . import views

urlpatterns = [
    # urls for paper
    path('submit/', views.create_paper, name='create_paper'),
    path('<int:paper_id>/submit/step1/', views.submit_paper_step1, name='submit_paper_step1'),
    path('<int:paper_id>/submit/step2/', views.submit_paper_step2, name='submit_paper_step2'),
    path('<int:paper_id>/submit/step3/', views.submit_paper_step3, name='submit_paper_step3'),
    path('<int:paper_id>/submit/step4/', views.submit_paper_step4, name='submit_paper_step4'),
    path('<int:paper_id>/submit/step5/', views.submit_paper_step5, name='submit_paper_step5'),
    path('<int:paper_id>/submit/step6/', views.submit_paper_step6, name='submit_paper_step6'),
    path('<int:paper_id>/submit/step7/', views.submit_paper_step7, name='submit_paper_step7'),

    path('<int:paper_id>/submit/step0/', views.submit_paper_step0, name='submit_paper_step0'),

    path('<int:paper_id>/submit/', views.submit_paper, name='submit_paper'),

    path('<int:paper_id>/create_revision', views.create_revision, name='create_revision'),
    path('<int:paper_id>/view_decision_letter', views.view_decision_letter, name='view_decision_letter'),

    path('<int:paper_id>/save-decision-response-file/', views.save_decision_response_file, name='save_decision_response_file'),
    path('<int:paper_id>/delete-decision-response-file/', views.delete_decision_response_file, name='delete_decision_response_file'),

    path('<int:paper_id>/save-cover-letter-file/', views.save_cover_letter_file, name="save_cover_letter_file"),
    path('<int:paper_id>/delete-cover-letter-file', views.delete_cover_letter_file, name="delete_cover_letter_file"),


    path('start_new_submission', views.start_new_submission, name='start_new_submission'),
    path('unsubmitted_manuscripts/', views.unsubmitted_manuscripts, name='unsubmitted_manuscripts'),
    path('submitted_manuscripts/', views.submitted_manuscripts, name='submitted_manuscripts'),
    path('coAuthored_manuscripts/', views.coAuthored_manuscripts, name='coAuthored_manuscripts'),
    path('manuscripts_with_decision/', views.manuscripts_with_decision, name='manuscripts_with_decision'),
    path('revised_manuscripts/', views.revised_manuscripts, name='revised_manuscripts'),

    path('<int:paper_id>/submit/step2/add_new_author', views.add_new_author, name='add_new_author'),
    path('<int:paper_id>/submit/step2/add_user_as_author/<int:user_id>', views.add_user_as_author, name='add_user_as_author'),
    path('<int:paper_id>/submit/step2/add_author_as_author/<int:author_id>', views.add_author_as_author, name='add_author_as_author'),
    path('<int:paper_id>/submit/step2/add-author-from-my-previous-papers/<int:author_id>', views.add_author_from_my_previous_papers, name='add_author_from_my_previous_papers'),

    path('<int:paper_id>/add-new-reviewer-preference', views.add_new_reviewer, name='add_new_reviewer_preference'),
    path('<int:paper_id>/add-existing-user-as-reviewer-preference/<int:user_id>', views.add_user_as_reviewer, name='add_user_as_reviewer_preference'),
    path('<int:paper_id>/add-existing-reviewer-as-reviewer-preference/<int:reviewer_id>', views.add_reviewer_as_reviewer, name='add_reviewer_as_reviewer_preference'),
    path('<int:paper_reviewer_id>/edit-reviewer-preference', views.edit_reviewer, name='edit_reviewer_preference'),
    path('display-edit-reviewer-modal/<int:paper_reviewer_id>', views.edit_reviewer_modal, name='edit_reviewer_modal'),
    path('<int:paper_id>/search-existing-user-reviewer-preference', views.search_user_reviewer, name='search_user_reviewer_preference'),
    path('paper/<int:paper_id>/delete-reviewer/<int:reviewer_id>/', views.delete_reviewer, name='delete_reviewer_preference'),

    path('<int:paper_id>/delete/conference/', views.delete_paper, name='delete_paper'),


    # urls for reviewer
    
    path('<int:paper_id>/delete_review/', views.delete_review, name='delete_review'),


    path('<int:paper_id>/merge_pdfs/', views.merge_pdfs, name='merge_pdfs'),

    path('delete_attribute/<int:attribute_id>', views.delete_attribute, name='delete_attribute'),


    path('rev_invitations/', views.rev_invitations, name='rev_invitations'),
    path('active_reviews/', views.active_reviews, name='active_reviews'),
    path('submitted_reviews/', views.submitted_reviews, name='submitted_reviews'),

    path('<int:paper_id>/review', views.review, name='review'),
    path('<int:paper_id>/submit_review', views.submit_review, name='submit_review'),
]    

htmx_urlpatterns = [
    # path('<int:paper_id>/search_user/', views.search_user, name='search_user'),
    path('<int:paper_id>/search_user1/', views.search_user1, name='search_user1'),
    path('<int:paper_id>/search_user2/', views.search_user2, name='search_user2'),
    path('<int:paper_id>/upload_file/', views.upload_file, name="upload_file"),
    path('<int:paper_id>/delete_file/<int:file_id>/', views.delete_file, name="delete_file"),
    path('<int:paper_id>/delete_all_files/', views.delete_all_files, name="delete_all_files"),
    path('sort/authors/', views.sort_authors, name='sort_authors'),

    path('<int:paper_id>/delete_author/<int:author_id>/', views.delete_author, name="delete_author"),
    path('<int:paper_id>/sort/files/', views.sort_files, name='sort_files'),

    path('<int:paper_id>/edit_author/<int:author_id>', views.edit_author, name="edit_author"),

    path('<int:paper_id>/step1_errors', views.step1_errors, name='step1_errors'),

    path('success_message', views.success_message, name="success_message"),

    path('<int:review_id>/upload_rev_file/', views.upload_rev_file, name='upload_rev_file'),
    path('<int:review_id>/upload_rev_files/', views.upload_rev_files, name='upload_rev_files'),

    path('<int:review_id>/remove_rev_file/<int:rev_file_id>', views.remove_rev_file, name='remove_rev_file'),

    path('assign_corresponding_author/<int:paper_author_id>/', views.assign_corresponding_author, name='assign_corresponding_author'),

    path('original_files/<int:paper_id>/', views.original_files, name='original_files'),
    path('view_proof/<int:paper_id>/', views.view_proof, name='view_proof'),

    path('<int:paper_id>/save_review', views.save_review, name='save_review'),

    


    

]

urlpatterns += htmx_urlpatterns