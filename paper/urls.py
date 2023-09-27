from django.urls import path

from . import views

urlpatterns = [
    # urls for paper
    path('submit/', views.submit_paper_step0, name='submit_paper_step0'),
    path('<int:paper_id>/submit/step1/', views.submit_paper_step1, name='submit_paper_step1'),
    path('<int:paper_id>/submit/step2/', views.submit_paper_step2, name='submit_paper_step2'),
    path('<int:paper_id>/submit/step3/', views.submit_paper_step3, name='submit_paper_step3'),
    path('<int:paper_id>/submit/step4/', views.submit_paper_step4, name='submit_paper_step4'),
    path('<int:paper_id>/submit/step5/', views.submit_paper_step5, name='submit_paper_step5'),
    path('<int:paper_id>/submit/step6/', views.submit_paper_step6, name='submit_paper_step6'),

    path('<int:paper_id>/submit/', views.submit_paper, name='submit_paper'),

    path('start_new_submission', views.start_new_submission, name='start_new_submission'),
    path('unsubmitted_manuscripts/', views.unsubmitted_manuscripts, name='unsubmitted_manuscripts'),
    path('submitted_manuscripts/', views.submitted_manuscripts, name='submitted_manuscripts'),
    path('coAuthored_manuscripts/', views.coAuthored_manuscripts, name='coAuthored_manuscripts'),

    path('<int:paper_id>/submit/step2/add_new_author', views.add_new_author, name='add_new_author'),
    path('<int:paper_id>/submit/step2/add_user_as_author/<int:user_id>', views.add_user_as_author, name='add_user_as_author'),
    path('<int:paper_id>/submit/step2/add_author_as_author/<int:author_id>', views.add_author_as_author, name='add_author_as_author'),



    path('<int:paper_id>/delete/conference/', views.delete_paper, name='delete_paper'),


    # urls for reviewer
    path('<int:paper_id>/accept_or_decline_to_review/', views.accept_or_decline_to_review, name='accept_or_decline_to_review'),
    path('<int:paper_id>/review', views.review, name='review'),
    path('<int:paper_id>/decline_to_review/', views.decline_to_review, name='decline_to_review'),
    path('<int:paper_id>/delete_review/', views.delete_review, name='delete_review'),


    path('<int:paper_id>/merge_pdfs/', views.merge_pdfs, name='merge_pdfs'),

    path('delete_attribute/<int:attribute_id>', views.delete_attribute, name='delete_attribute')
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

    path('<int:paper_id>/upload_cover_letter/', views.upload_cover_letter, name="upload_cover_letter"),
    path('<int:paper_id>/delete_cover_letter', views.delete_cover_letter, name="delete_cover_letter")
]

urlpatterns += htmx_urlpatterns