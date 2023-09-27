from django.db.models import Max
from django.shortcuts import get_object_or_404
from paper.models import Paper, Paper_Author, File


def get_max_order_author(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    existing_authors = Paper_Author.objects.filter(paper=paper)
    if not existing_authors.exists():
        return 1
    else:
        current_max = existing_authors.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1

def get_max_order_file(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    existing_files = File.objects.filter(paper=paper)
    if not existing_files.exists():
        return 1
    else:
        current_max = existing_files.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1

   
# def reorder(user):
#     existing_films = UserFilms.objects.filter(user=user)
#     if not existing_films.exists():
#         return
#     number_of_films = existing_films.count()
#     new_ordering = range(1, number_of_films+1)
    
#     for order, user_film in zip(new_ordering, existing_films):
#         user_film.order = order
#         user_film.save()


def reorder_authors(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    existing_authors = Paper_Author.objects.filter(paper=paper)
    if not existing_authors.exists():
        return
    number_of_authors = existing_authors.count()
    new_ordering = range(1, number_of_authors+1)

    for order, paper_author in zip(new_ordering, existing_authors):
        paper_author.order = order
        paper_author.save()


def reorder_files(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    existing_files = File.objects.filter(paper=paper)
    if not existing_files.exists():
        return
    number_of_files = existing_files.count()
    new_ordering = range(1, number_of_files+1)

    for order, file in zip(new_ordering, existing_files):
        file.order = order
        file.save()


