from django.db.models import Max
from django.shortcuts import get_object_or_404
from paper.models import Paper, Paper_Author, File, Paper_Reviewer


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

def get_max_order_reviewer(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    existing_reviewers = Paper_Reviewer.objects.filter(paper=paper).exclude(status='Alternate')
    if not existing_reviewers.exists():
        return 1
    else:
        current_max = existing_reviewers.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


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

def reorder_reviewers(paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    existing_reviewers = Paper_Reviewer.objects.filter(paper=paper).exclude(status='Alternate')
    if existing_reviewers.exists(): 
        number_of_reviewers = existing_reviewers.count()
        new_ordering = range(1, number_of_reviewers+1)

        for order, paper_reviewer in zip(new_ordering, existing_reviewers):
            paper_reviewer.order = order
            paper_reviewer.save()  


    existing_reviewers = Paper_Reviewer.objects.filter(paper=paper).filter(status='Alternate')
    if not existing_reviewers.exists():
        return
    number_of_reviewers = existing_reviewers.count()
    new_ordering = range(1, number_of_reviewers+1)

    for order, paper_reviewer in zip(new_ordering, existing_reviewers):
        paper_reviewer.order = order
        paper_reviewer.save()      



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


