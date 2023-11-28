from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.urls import resolve
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.files.base import ContentFile


from PyPDF2 import PdfReader, PdfWriter
from docx2pdf import convert
import os
import pythoncom
from reportlab.pdfgen import canvas
from PIL import Image
from PyPDF2 import PdfMerger
from django.template.loader import get_template
from xhtml2pdf import pisa
import win32com.client 
from reportlab.lib.pagesizes import letter

from accounts.models import Role, User
from accounts.views import login
from conference.utils import send_review_invitation_email, send_review_invitation_email2

from .forms import AuthorForm, PaperForm1, PaperForm2, PaperForm3, PaperForm4, ReviewFileModelFormset, ReviewForm, additionalAttributeFormSet
from .models import AERecommendation, Author, EICDecision, File, Paper, Paper_Author, Paper_Reviewer, PreferencePaper_Reviewer, Review, ReviewFile, Reviewer, additionalAttribute
from .utils import get_max_order_author, get_max_order_file, reorder_authors, reorder_files, reorder_reviewers

# Create your views here.

def check_role_author(user):
    if user.role == 'Author':
        return True
    else:
        raise PermissionDenied  


def delete_author(request, paper_id, author_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.authors.remove(author_id)

    reorder_authors(paper_id)

    # Paper_Author.objects.get(paper=paper, author=author).delete()

    author = get_object_or_404(Author, id=author_id)

    papers = Paper.objects.filter(paper_author__author_id=author)
    if not papers:
        author.delete()

    paper_authors = Paper_Author.objects.filter(paper=paper)  

    papers = Paper.objects.filter(submitter=request.user)
    # authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).distinct()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()

    context = {
        'paper': paper,
        'authors': authors,
        'paper_authors': paper_authors,
    }  

    return render(request, 'partials/add_authors.html', context)


def search_user1(request, paper_id):
    email = request.POST.get('email')

    # paper = Paper.objects.get(id=paper_id)
    # paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    # for paper_reviewer in paper_reviewers:
    #     if paper_reviewer.reviewer.email == email:
    #         break
    # reviewer = paper_reviewer.reviewer  

    try:
        reviewer = PreferencePaper_Reviewer.objects.get(paper_id=paper_id, reviewer__email=email).reviewer
    except:
        reviewer = None

    if reviewer == None:    
        try:
            user = User.objects.get(email=email)
        except:
            user = None   

        if user == None:
            try:
                author = Author.objects.get(email=email)
            except:
                author = None    
        else:
            author = None        
    else:
        user = None
        author = None        
         
    context = {
        'user': user,
        'author': author,
        'paper_id': paper_id,
        'reviewer': reviewer
    }
    return render(request, 'partials/search_user_result1.html', context)


def search_user2(request, paper_id):
    email = request.POST.get('email')

    try:
        reviewer = PreferencePaper_Reviewer.objects.get(paper_id=paper_id, reviewer__email=email).reviewer
    except:
        reviewer = None

    if reviewer == None:    
        try:
            user = User.objects.get(email=email)
        except:
            user = None   

        if user == None:
            try:
                author = Author.objects.get(email=email)
            except:
                author = None    
        else:
            author = None        
    else:
        user = None
        author = None        
         
    context = {
        'user': user,
        'author': author,
        'paper_id': paper_id,
        'reviewer': reviewer
    }
    return render(request, 'partials/search_user_result2.html', context)



def add_user_as_author(request, paper_id, user_id):
    user = get_object_or_404(User, id=user_id)
    user.roles.add(Role.objects.get(name='AU'))

    author = Author.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email, institution=user.institution, city=user.city, state=user.state, country=user.country)[0]

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Author.objects.filter(paper=paper, author=author).exists():
        Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    papers = Paper.objects.filter(submitter=request.user)

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()

    context = {
        'paper': paper,
        'authors': authors,
        'paper_authors': paper_authors
    }

    return render(request, 'partials/add_authors.html', context)


def add_author_as_author(request, paper_id, author_id):
    author = get_object_or_404(Author, id=author_id)

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Author.objects.filter(paper=paper, author=author).exists():
        Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    papers = Paper.objects.filter(submitter=request.user)
    # authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).distinct()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()

    context = {
        'paper': paper,
        'authors': authors,
        'paper_authors': paper_authors
    }

    return render(request, 'partials/add_authors.html', context)


def add_new_author(request, paper_id):
    email = request.POST.get('email').lower()
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()
    institution = request.POST.get('institution').capitalize()
    country = request.POST.get('country').capitalize()
    state = request.POST.get('state').capitalize()
    city = request.POST.get('city').capitalize()

    author = Author.objects.create(first_name=first_name, last_name=last_name, email=email, institution=institution, country=country, state=state, city=city)  
    author.save() 
        
    paper = Paper.objects.get(id=paper_id)    
    #paper.authors.add(author)
    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    papers = Paper.objects.filter(submitter=request.user)
    # authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).distinct()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()

    context = {
        'paper': paper,
        'authors': authors,
        'paper_authors': paper_authors
    }

    return render(request, 'partials/add_authors.html', context)


def add_author_from_my_previous_papers(request, author_id, paper_id):
    author = get_object_or_404(Author, id=author_id)

    paper = Paper.objects.get(id=paper_id)
    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    papers = Paper.objects.filter(submitter=request.user)
    # authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).distinct()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()

    context = {
        'paper': paper,
        'paper_authors': paper_authors,
        'authors': authors
    }

    return render(request, 'partials/add_authors.html', context)


def assign_corresponding_author(request, paper_author_id):
    paper_author_1 = get_object_or_404(Paper_Author, id=paper_author_id)

    paper_author = get_object_or_404(Paper_Author, paper=paper_author_1.paper, corresponding_author=True)
    paper_author.corresponding_author = False
    paper_author.save()

    paper_author_1.corresponding_author = True
    paper_author_1.save()

    paper_authors = Paper_Author.objects.filter(paper=paper_author.paper)

    context = {
        'paper_authors': paper_authors,
    }    

    return render(request, 'partials/authors.html', context)

    

def sort_authors(request):
    author_pks_order = request.POST.getlist('author_order')
    paper_authors = []
    for idx, author_pk in enumerate(author_pks_order, start=1):
        paper_author = Paper_Author.objects.get(pk=author_pk)
        paper_author.order = idx
        paper_author.save()
        paper_authors.append(paper_author)

    context = {
        'paper_authors': paper_authors,
    }    

    return render(request, 'partials/authors.html', context)


def sort_files(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    file_ids_order = request.POST.getlist('file_order')
    
    for idx, file_id in enumerate(file_ids_order, start=1):
        file = File.objects.get(id=file_id)
        file.order = idx
        file.save()
    
    context = {
        'paper': paper
    }

    return render(request, 'partials/files.html', context)    


def edit_author(request, paper_id, author_id):
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()
    institution = request.POST.get('institution').capitalize()
    country = request.POST.get('country').capitalize()
    state = request.POST.get('state').capitalize()
    city = request.POST.get('city').capitalize()

    author = get_object_or_404(Author, id=author_id)
    author.first_name = first_name
    author.last_name = last_name
    author.institution = institution
    author.country = country
    author.state = state
    author.city = city

    author.save()
    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)

    context = {
        'paper_authors': paper_authors,
    }  

    return render(request, 'partials/authors.html', context)


def coAuthored_manuscripts(request):
    try: 
        papers = Paper.objects.filter(date_submitted__isnull=False).exclude(submitter=request.user).filter(Q(authors__user=request.user))
    except:
        papers = None 
           
    context = {
        'papers': papers,
    }
    return render(request, 'paper/co-authored_manuscripts.html', context)

              
def submitted_manuscripts(request):
    try: 
        papers = Paper.objects.filter(date_submitted__isnull=False, submitter=request.user, eicdecision__date_submitted__isnull=True)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/submitted_manuscripts.html', context)


def unsubmitted_manuscripts(request):
    try: 
        papers = Paper.objects.filter(date_submitted__isnull=True, submitter=request.user, eicdecision__date_submitted__isnull=True)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/unsubmitted_manuscripts.html', context)


def manuscripts_with_decision(request):
    try: 
        papers = Paper.objects.filter(date_submitted__isnull=False, submitter=request.user, eicdecision__date_submitted__isnull=False)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/manuscripts_with_decision.html', context)


def revised_manuscripts(request):
    try: 
        papers = Paper.objects.filter(date_submitted__isnull=True, submitter=request.user, eicdecision__date_submitted__isnull=False)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/revised_manuscripts.html', context)


import re

def increment_string(s):
    pattern = re.compile(r'(_R(\d+))?$')

    match = pattern.search(s)
    if match:
        if match.group(2) is not None:
            # String contains '_R' with a number
            new_number = int(match.group(2)) + 1
            return re.sub(pattern, f'_R{new_number}', s, count=1)
        else:
            # String does not contain '_R', append '_R1'
            return s + '_R1'
    else:
        return s
    

def submit_paper_step0(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        form = PaperForm4(request.POST, instance=paper)
          
        if form.is_valid():
            form.save() 

        next = request.GET.get('next')
        if next == 'step1' or 'save_and_continue' in request.POST:
            return redirect('submit_paper_step1', paper_id)
        if next == 'step2':
            return redirect('submit_paper_step2', paper_id)
        elif next == 'step3':
            return redirect('submit_paper_step3', paper_id)
        elif next == 'step4':
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        elif next == 'step6':
            return redirect('submit_paper_step6', paper_id)
        elif next == 'step7':
            return redirect('submit_paper_step7', paper_id)
    else:
        form = PaperForm4(instance=paper)

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
    reviews = Review.objects.filter(paper_reviewer__in = paper_reviewers, date_submitted__isnull=False, revision=revision_number(paper.journal_id)-1)

    eic = User.objects.get(roles=Role.objects.get(name='EIC'))

    context = {
        'paper': paper,
        'form': form,
        'reviews': reviews,
        'eic': eic
    }        

    return render(request, 'paper/submit_paper/step0.html', context)        


def get_grouped_reviews_list(paper_reviewers):
    reviews = Review.objects.filter(paper_reviewer__in = paper_reviewers, date_submitted__isnull=False)

    # Group reviews by revision using a defaultdict
    grouped_reviews_dict = defaultdict(list)
    for review in reviews:
        grouped_reviews_dict[review.revision].append(review)

    # Convert the dictionary values to a list of lists
    grouped_reviews_list = list(grouped_reviews_dict.values())   
    grouped_reviews_list = list(reversed(grouped_reviews_list))  

    return grouped_reviews_list


def revision_number(value):
    # Use regular expression to find the numeric part after '_R' at the end
    match = re.search(r'_R(\d+)$', value)

    # If a numeric part is found, convert it to an integer; otherwise, return 0
    return int(match.group(1)) if match else 0


def view_decision_letter(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
    reviews = Review.objects.filter(paper_reviewer__in = paper_reviewers, date_submitted__isnull=False, revision=revision_number(paper.journal_id))

    eic = User.objects.get(roles=Role.objects.get(name='EIC'))

    context = {
        'paper': paper,
        'reviews': reviews,
        'eic': eic
    }

    return render(request, 'paper/view_decision_letter.html', context)


def create_revision(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    paper.journal_id = increment_string(paper.journal_id)
    paper.date_submitted = None
    paper.save()

    return redirect('submit_paper_step0', paper.id)


def rev_invitations(request):
    try: 
        # papers = Paper.objects.filter(reviewers__user = request.user, paper_reviewer__status='Invited')
        paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user = request.user, status='Invited')
    except:
        paper_reviewers = None    
    context = {
        'paper_reviewers': paper_reviewers,
    }
    return render(request, 'paper/reviewer_invitations.html', context)


def active_reviews(request): 
    # papers = Paper.objects.filter(reviewers__user = request.user, paper_reviewer__status='Agreed')
    # paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user = request.user, status='Agreed')
    paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user = request.user)

    reviews = Review.objects.filter(paper_reviewer__in = paper_reviewers, date_submitted__isnull=True)
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'paper/active_reviews.html', context)


def submitted_reviews(request):
    # papers = Paper.objects.filter(reviewers__user = request.user, paper_reviewer__status='Submitted')
    # paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user = request.user, status='Submitted')
    paper_reviewers = Paper_Reviewer.objects.filter(reviewer__user = request.user)
    reviews = Review.objects.filter(paper_reviewer__in = paper_reviewers, date_submitted__isnull=False)
      
    context = {
        'reviews': reviews,
    }
    return render(request, 'paper/submitted_reviews.html', context)


def start_new_submission(request):
    return render(request, 'paper/start_new_submission.html')

def create_paper(request):
    paper = Paper.objects.create(submitter = request.user, journal_id="draft")

    author = Author.objects.get_or_create(user=request.user, first_name=request.user.first_name, last_name=request.user.last_name, email=request.user.email)[0]

    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper.id), corresponding_author=True)
    
    return redirect('submit_paper_step1', paper.id)     


@login_required(login_url='login')
def submit_paper_step1(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        form = PaperForm1(request.POST, instance=paper)
          
        if form.is_valid():
            form.save() 

        next = request.GET.get('next')
        if next == 'step2' or 'save_and_continue' in request.POST:
            return redirect('submit_paper_step2', paper_id)
        if next == 'step0':
            return redirect('submit_paper_step0', paper_id)
        elif next == 'step3':
            return redirect('submit_paper_step3', paper_id)
        elif next == 'step4':
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        elif next == 'step6':
            return redirect('submit_paper_step6', paper_id)
        elif next == 'step7':
            return redirect('submit_paper_step7', paper_id)
    else:
        form = PaperForm1(instance=paper)

    context = {
        'paper': paper,
        'form': form,
    }        

    return render(request, 'paper/submit_paper/step1.html', context)        


def save_decision_response_file(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    file = request.FILES.get('decision_response_file')

    if file:
        paper.decision_response_file = file
        paper.save()

    context = {
        'paper': paper
    }    

    return render(request, 'partials/paper/decision_letter_response_file.html', context)


def delete_decision_response_file(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    paper.decision_response_file = None
    paper.save()

    context = {
        'paper': paper
    }    

    return render(request, 'partials/paper/decision_letter_response_file.html', context)


def save_cover_letter_file(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    file = request.FILES.get('cover_letter_file')

    if file:
        paper.cover_letter_file = file
        paper.save()

    context = {
        'paper': paper 
    }
    return render(request, 'partials/paper/cover_letter_file.html', context)    


def delete_cover_letter_file(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.cover_letter_file = None
    paper.save()

    context = {
        'paper': paper
    }   

    return render(request, 'partials/paper/cover_letter_file.html', context)    





    

def submit_paper_step2(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)

    papers = Paper.objects.filter(submitter=request.user)
    # authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).distinct()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    reviewer_emails = [paper_reviewer.reviewer.email for paper_reviewer in paper_reviewers]

    authors = Author.objects.filter(papers__in=papers).exclude(papers=paper).exclude(email__in=reviewer_emails).distinct()
    
    context = {
        'paper': paper,
        'authors': authors,
        'paper_authors': paper_authors,
    }
    return render(request, 'paper/submit_paper/step2.html', context)    

def submit_paper_step3(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        form = PaperForm3(request.POST, instance=paper)
        formset = additionalAttributeFormSet(request.POST, prefix='attributes', instance=paper)

        if form.is_valid() and formset.is_valid():
            form.save() 

            for aform in formset:
                attribute = aform.save(commit=False)
                if attribute.name != '':
                    attribute.paper = paper
                    attribute.save()
                elif attribute.name == '' and aform.instance.id:
                    aform.instance.delete()    

        next = request.GET.get('next')
        if next == 'step4' or 'save_and_continue' in request.POST:
            return redirect('submit_paper_step4', paper_id)
        if next == 'step0':
            return redirect('submit_paper_step0', paper_id)
        elif next == 'step1':
            return redirect('submit_paper_step1', paper_id)
        elif next == 'step2':
            return redirect('submit_paper_step2', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        elif next == 'step6':
            return redirect('submit_paper_step6', paper_id)
        elif next == 'step7':
            return redirect('submit_paper_step7', paper_id)
    else:
        form = PaperForm3(instance=paper)
        formset = additionalAttributeFormSet(prefix='attributes', instance=paper)

    context = {
        'paper': paper,
        'form': form,
        'formset': formset
    }
    return render(request, 'paper/submit_paper/step3.html', context)    


def delete_attribute(request, attribute_id):
    attribute = additionalAttribute.objects.get(id=attribute_id)

    attribute.delete()
   
    return redirect('submit_paper_step3', attribute.paper.id)


# def search_user(request, paper_id):
#     email = request.POST.get('email')

#     try:
#         user = User.objects.get(email=email)
#     except:
#         user = None    
#     context = {
#         'user': user,
#         'paper_id': paper_id,
#         'email': email
#     }
#     return render(request, 'partials/search_user_result.html', context)


def submit_paper_step4(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    context = {
        'paper': paper,
    }    
    return render(request, 'paper/submit_paper/step4.html', context)


# @login_required
# def upload_photo(request, pk):
#     userfilm = get_object_or_404(UserFilms, pk=pk)
#     print(request.FILES)
#     photo = request.FILES.get('photo')
#     userfilm.film.photo.save(photo.name, photo)
#     context = {'userfilm': userfilm}
#     return render(request, 'partials/film-detail.html', context)


def upload_file(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    duplicate_files = []
    
    saved_files = File.objects.filter(paper=paper)
    file_list = []
    for file in saved_files:
        file_list.append(os.path.basename(file.file.name))

    print(file_list)    

    file1 = request.FILES.get('file1') 
    file2 = request.FILES.get('file2')
    file3 = request.FILES.get('file3')

    print(file1.name)
    
    if file1:
        desig1 = request.POST.get('desig1')
        if desig1 != "Choose File Designation...":
            if file1.name in file_list:
                duplicate_files.append(file1.name)
            else:
                file_list.append(file1.name)
                file = File.objects.create(paper=paper, file=file1, order=get_max_order_file(paper_id))
                file.designation = desig1
                file.save()

    if file2:
        desig2 = request.POST.get('desig2')
        if desig2 != "Choose File Designation...":
            if file2.name in file_list:
                duplicate_files.append(file2.name) 
            else:
                file_list.append(file2.name)    
                file = File.objects.create(paper=paper, file=file2, order=get_max_order_file(paper_id))
                file.designation = desig2
                file.save()
    
    if file3:
        desig3 = request.POST.get('desig3')
        if desig3 != "Choose File Designation...":
            if file3.name in file_list:
                duplicate_files.append(file3.name)
            else:  
                file_list.append(file3.name)    
                file = File.objects.create(paper=paper, file=file3, order=get_max_order_file(paper_id))
                file.designation = desig3
                file.save()
        

    context = {
        'paper': paper,
        'duplicate_files': duplicate_files

    }
    return render(request, 'partials/files.html', context)    


def delete_all_files(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    files = File.objects.filter(paper=paper)

    for file in files:
        # Delete the file from storage (optional)
        file.file.delete(save=False)

        # Delete the file record from the database
        file.delete()

    context = {
        'paper': paper
    }
    return render(request, 'partials/files.html', context)    


def delete_file(request, paper_id, file_id):
    paper = get_object_or_404(Paper, id=paper_id)

    file = get_object_or_404(File, id=file_id)
    file.file.delete(save=False)
    file.delete()
    reorder_files(paper_id)
    context = {
        'paper': paper
    }
    return render(request, 'partials/files.html', context) 


def submit_paper_step5(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        form = PaperForm2(request.POST, request.FILES, instance=paper)
          
        if form.is_valid():
            form.save() 
            
        else:
            form.errors()    

        next = request.GET.get('next')
        if next == 'step6' or 'save_and_continue' in request.POST:
            return redirect('submit_paper_step6', paper_id)
        if next == 'step0':
            return redirect('submit_paper_step0', paper_id)
        elif next == 'step1':
            return redirect('submit_paper_step1', paper_id)
        elif next == 'step2':
            return redirect('submit_paper_step2', paper_id)
        elif next == 'step3':
            return redirect('submit_paper_step3', paper_id)
        elif next == 'step4':
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step7':
            return redirect('submit_paper_step7', paper_id)

    else:
        form = PaperForm2(instance=paper)

    context = {
        'paper': paper,
        'form': form
    }        

    return render(request, 'paper/submit_paper/step5.html', context)   


def submit_paper_step6(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper': paper,
        'paper_reviewers': paper_reviewers
    }  

    return render(request, 'paper/submit_paper/step6.html', context)   


def add_new_reviewer(request, paper_id):
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()
    email = request.POST.get('email').lower()

    preference = request.POST.get('preference')
    reason = request.POST.get('reason')

    paper = get_object_or_404(Paper, id=paper_id)

    reviewer = Reviewer.objects.create(first_name=first_name, last_name=last_name, email=email)
    PreferencePaper_Reviewer.objects.create(paper=paper, reviewer=reviewer, preference=preference, reason=reason)

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper_reviewers': paper_reviewers
    }

    return render(request, 'partials/paper/reviewers.html', context)


def edit_reviewer(request, paper_reviewer_id):
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()

    preference = request.POST.get('preference')
    reason = request.POST.get('reason')

    paper_reviewer = get_object_or_404(PreferencePaper_Reviewer, id=paper_reviewer_id)

    reviewer = Reviewer.objects.get(id=paper_reviewer.reviewer.id)
    reviewer.first_name = first_name
    reviewer.last_name = last_name
    reviewer.save()

    paper_reviewer.preference = preference
    paper_reviewer.reason = reason
    paper_reviewer.save()

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper_reviewer.paper)

    context = {
        'paper_reviewers': paper_reviewers,
    }  

    return render(request, 'partials/paper/reviewers.html', context)


def edit_reviewer_modal(request, paper_reviewer_id):
    paper_reviewer = PreferencePaper_Reviewer.objects.get(id=paper_reviewer_id)

    context = {
        'paper_reviewer': paper_reviewer
    }

    return render(request, 'partials/paper/edit_reviewer.html', context)


def delete_reviewer(request, paper_id, reviewer_id):
    paper = get_object_or_404(Paper, id=paper_id)
    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    PreferencePaper_Reviewer.objects.get(paper=paper, reviewer=reviewer).delete()

    papers = Paper.objects.filter(paper_reviewer__reviewer_id=reviewer)
    if not papers and not PreferencePaper_Reviewer.objects.filter(reviewer=reviewer):
        reviewer.delete()
        
    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper) 

    context = {
        'paper_reviewers': paper_reviewers,
    }  

    return render(request, 'partials/paper/reviewers.html', context)

def add_user_as_reviewer(request, paper_id, user_id):
    user = get_object_or_404(User, id=user_id)
    user.roles.add(Role.objects.get(name='REV'))

    reviewer = Reviewer.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)[0]

    paper = Paper.objects.get(id=paper_id)

    preference = request.POST.get('preference1')
    reason = request.POST.get('reason1')

    if not PreferencePaper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        PreferencePaper_Reviewer.objects.create(paper=paper, reviewer=reviewer, preference=preference, reason=reason)

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper_reviewers': paper_reviewers
    }

    return render(request, 'partials/paper/reviewers.html', context)


def add_reviewer_as_reviewer(request, paper_id, reviewer_id):
    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    paper = Paper.objects.get(id=paper_id)

    preference = request.POST.get('preference1')
    reason = request.POST.get('reason1')

    if not PreferencePaper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        PreferencePaper_Reviewer.objects.create(paper=paper, reviewer=reviewer, preference=preference, reason=reason)

    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper_reviewers': paper_reviewers,
    }

    return render(request, 'partials/paper/reviewers.html', context)


def search_user_reviewer(request, paper_id):
    email = request.POST.get('email')

    user = None
    reviewer = None
    try:
        author = Paper.objects.get(id=paper_id).authors.get(email=email)
    except:
        author = None
    if author == None: 
        try:
            user = User.objects.get(email=email)
        except:
            user = None   

        if user == None:
            try:
                reviewer = Reviewer.objects.get(email=email)
            except:
                reviewer = None    
        else:
            reviewer = None            
         
    context = {
        'user': user,
        'reviewer': reviewer,
        'paper_id': paper_id,
        'author': author
    }
    return render(request, 'partials/paper/search_user_reviewer_result.html', context)



def submit_paper_step7(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)
    paper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper)
    form = PaperForm2(instance=paper)
    for field_name in ['cover_letter', 'number_of_tables', 'number_of_figures', 'word_count', 'figures_tables_published_elsewhere_desc']:  # Replace with the field names you want to make readonly
            form.fields[field_name].widget.attrs['readonly'] = True
    context = {
        'paper': paper,
        'paper_authors': paper_authors,
        'paper_reviewers': paper_reviewers,
        'form': form
    }  
    return render(request, 'paper/submit_paper/step7.html', context)   


from django.core.files import File as f
def submit_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    current_date = datetime.now()
    current_year = current_date.year 
    current_month = current_date.month
    print(current_year)
    print(current_month)

    if paper.journal_id == 'draft':
        papers_count = Paper.objects.filter(date_submitted__year=current_year, date_submitted__month=current_month).count()
        print(papers_count)

        paper.journal_id = 'JAIR-' + str(current_year%100) + '-' + str(current_month) + '-' + str(papers_count + 1)

    paper.date_submitted = current_date.date()

    # paper.file.name = str(paper.journal_id) + '.pdf'
    # paper.file.save(str(paper.journal_id)+'.pdf')


    # new_file_name = str(paper.journal_id) + '.pdf'
    # new_file_path = os.path.join("files", new_file_name) 

    # with open(paper.file.path, 'rb') as existing_file:
    #     new_file = f(existing_file, name=new_file_path)
    #     paper.file.save(new_file_name, new_file)

    paper.save()

    merge_pdfs(request, paper.id)

    role = Role.objects.get(name='AU')
    paper.submitter.roles.add(role)

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper, status = 'Submitted')
    for paper_reviewer in paper_reviewers:
        paper_reviewer.status = ''
        paper_reviewer.save()

    if EICDecision.objects.filter(paper=paper).exists():
        paper.eicdecision.date_submitted = None
        paper.eicdecision.save()

    if AERecommendation.objects.filter(paper=paper).exists():
        paper.aerecommendation.date_submitted = None    
        paper.aerecommendation.save()

    return redirect(submitted_manuscripts)


def delete_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    authors_to_delete = paper.authors.all()
    
    for author in authors_to_delete:
        papers = Paper.objects.filter(authors=author).exclude(id=paper_id)

        if not papers:
            author.delete()

    reviewers_to_delete = paper.reviewers.all()
    
    for reviewer in reviewers_to_delete:
        papers = Paper.objects.filter(reviewers=reviewer).exclude(id=paper_id)

        if not papers:
            reviewer.delete()        

    paper.delete()    

    return redirect('unsubmitted_manuscripts')


def step1_errors(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    context = {
        'paper': paper
    }

    return render(request, 'partials/step1_errors.html', context) 


def success_message(request):
    return render(request, 'partials/success_message.html')


def delete_review(request, paper_id):
    review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
    review.delete()
    return redirect('myAccount')


def remove_rev_file(request, review_id, rev_file_id):
    review = get_object_or_404(Review, id=review_id)
    rev_file = get_object_or_404(ReviewFile, id=rev_file_id)
    rev_file.delete()  
    # rev_file.file.delete(save=False)

    formset = ReviewFileModelFormset(queryset=ReviewFile.objects.filter(review=review, view=''))

    context = {
        'review': review,
        'formset': formset
    }

    return render(request, 'partials/review_files.html', context)    





def upload_rev_files(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        formset = ReviewFileModelFormset(request.POST, queryset=ReviewFile.objects.filter(review=review))   
        if formset.is_valid():    
            formset.save()  
        else:
            print(formset.errors)

    formset = ReviewFileModelFormset(queryset=ReviewFile.objects.filter(review=review, view=''))    
    context = {
        'review': review,
        'formset': formset
    }

    return render(request, 'partials/review_files.html', context)       


 

def upload_rev_file(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    duplicate_file = None
    
    saved_files = ReviewFile.objects.filter(review=review)
    file_list = []
    for file in saved_files:
        file_list.append(os.path.basename(file.file.name))

    file = request.FILES.get('rev_file')     

    if file:
        if file.name in file_list:
            duplicate_file = file.name
        else:     
            rev_file = ReviewFile.objects.create(file=file, review=review)
            rev_file.save()   

    formset = ReviewFileModelFormset(queryset=ReviewFile.objects.filter(review=review, view=''))    

    context = {
        'review': review,
        'duplicate_file': duplicate_file,
        'formset': formset
    }

    return render(request, 'partials/review_files.html', context)   


def revision_number(input_string):
    # Use regular expression to find the numeric part after '_R' at the end
    match = re.search(r'_R(\d+)$', input_string)

    # If a numeric part is found, convert it to an integer; otherwise, return 0
    return int(match.group(1)) if match else 0


def create_review(request, paper_id):
    paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
    paper_reviewer.status = 'Agreed'
    paper_reviewer.save()

    r = Review.objects.create(paper_reviewer=paper_reviewer, due_date = (datetime.now() + timedelta(days=20)).replace(hour=23, minute=59), revision = revision_number(paper_reviewer.paper.journal_id))

    return redirect(review, r.id)



def review(request, review_id):
    review = Review.objects.get(id=review_id)
    
    form = ReviewForm(instance=review)

    formset = ReviewFileModelFormset(queryset=ReviewFile.objects.filter(review=review, view=''))

    context = {
        'paper': review.paper_reviewer.paper,
        'form': form,
        'formset': formset,
        'review': review,
        'paper_reviewer': review.paper_reviewer
    }    
    return render(request, 'paper/review.html', context)


def save_review(request, review_id):
    review = Review.objects.get(id=review_id)

    form = ReviewForm(request.POST, instance=review)
    review = form.save(commit=False)
    review.save()

    context = {
        'form': form,
        'review': review,
    }    

    return render(request, 'partials/review_form.html', context)

def submit_review(request, review_id):
    review = Review.objects.get(id=review_id)
    review.paper_reviewer.status = 'Submitted'
    review.paper_reviewer.save()

    review.date_submitted = datetime.now()
    review.save()

    return redirect('submitted_reviews')


def convert_to_pdf(doc_path):
    # Function to convert various file types to PDF
    file_extension = os.path.splitext(doc_path)[-1].lower()

    if file_extension == '.pdf':
        # File is already a PDF, no need to convert
        return doc_path
    
    elif file_extension == '.docx':
        # Convert DOCX to PDF
        pdf_path = os.path.splitext(doc_path)[0] + '.pdf'
        print(pdf_path)

        # Initialize COM
        pythoncom.CoInitialize()

        convert(doc_path, pdf_path)

        pythoncom.CoUninitialize()

        return pdf_path

    elif file_extension in ('.ppt', '.pptx'):
        pdf_path = os.path.splitext(doc_path)[0] + '.pdf'

        pythoncom.CoInitialize()
    
        powerpoint = win32com.client.DispatchEx("Powerpoint.Application")
    
        presentation  = powerpoint.Presentations.Open(doc_path, WithWindow=False)
        presentation.SaveAs(pdf_path, 32) # formatType = 32 for ppt to pdf
        presentation.Close()
        powerpoint.Quit()

        pythoncom.CoUninitialize()
        return pdf_path
    

    elif file_extension in ('.xlsx', '.xls'):
        # Convert Excel to PDF
        pdf_path = os.path.splitext(doc_path)[0] + '.pdf'

        # Initialize COM
        pythoncom.CoInitialize()

        # Create an instance of Excel
        excel = win32com.client.Dispatch("Excel.Application")
        
        # Open the Excel file
        wb = excel.Workbooks.Open(doc_path)
        
        # Export as PDF
        wb.ExportAsFixedFormat(0, pdf_path)
        
        # Close Excel
        wb.Close(False)
        excel.Quit()

        pythoncom.CoUninitialize()

        return pdf_path

    elif file_extension in ('.png', '.jpeg', '.jpg'):
        # # Convert image to PDF
        # pdf_path = os.path.splitext(doc_path)[0] + '.pdf'
        # print(pdf_path)

        # # Open and convert the image to PDF using Pillow
        # image = Image.open(doc_path)
        # image.save(pdf_path, "PDF")

        # return pdf_path
        # Define the desired page size (e.g., letter size)

        page_size = letter

        # Generate a PDF file path
        pdf_path = os.path.splitext(doc_path)[0] + '.pdf'

        # Open and convert the image to PDF using Pillow
        image = Image.open(doc_path)

        # Create a PDF canvas with the desired page size
        c = canvas.Canvas(pdf_path, pagesize=page_size)
        
        # Calculate the scaling factor to fit the image within the page size
        width, height = page_size
        image_width, image_height = image.size
        scale_factor = min(width / image_width, height / image_height)
        
        # Calculate the position to center the image on the page
        x_offset = (width - image_width * scale_factor) / 2
        y_offset = (height - image_height * scale_factor) / 2
        
        # Draw the image on the PDF canvas
        c.drawImage(doc_path, x_offset, y_offset, image_width * scale_factor, image_height * scale_factor)

        # Save the PDF
        c.save()

        return pdf_path
    
    else:
        return None
    

def render_html_to_pdf(html_content, pdf_file_path):
    with open(pdf_file_path, "wb") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)




def merge_pdfs(request, paper_id):
    paper = Paper.objects.get(id=paper_id)
    files = File.objects.filter(paper=paper)

    if not files:
        return HttpResponse("No files submitted yet!")

    merger = PdfMerger()

    context = {'paper': paper, 'failed_conversions': []} 

    for file in files:
        doc_path = file.file.path
        pdf_path = convert_to_pdf(doc_path)
        if pdf_path is not None:
            merger.append(pdf_path)
        else:
            # If conversion failed, add the doc_path to the failed_conversions list
            context['failed_conversions'].append(doc_path)        

    # Create a PDF from a Django template
    html_template = get_template('paper/toPdf.html')
    html_content = html_template.render(context)

    # Temporary path to store the HTML-to-PDF converted file
    temp_html_pdf_path = 'Downloads'  # Replace with the actual path

    # Convert HTML to PDF and append it to the merger
    render_html_to_pdf(html_content, temp_html_pdf_path)
    merger.merge(0, temp_html_pdf_path)        

    

    merged_pdf_content = BytesIO()
    merger.write(merged_pdf_content)
    merged_pdf_content.seek(0)

    # Create a Django ContentFile from the merged PDF content
    merged_pdf_file = ContentFile(merged_pdf_content.read())

    # Get the Paper object
    paper = Paper.objects.get(id=paper_id)

    paper.file.delete(save=False)

    # Assign the merged PDF file to the 'file' field of the Paper model
    paper.file.save(str(paper.journal_id)+'.pdf', merged_pdf_file)

    # Create an HttpResponse with the merged PDF as content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="merged.pdf"'

    # Write the merged PDF content to the response
    # merger.write(response)
    merger.close()

    # Write the merged PDF content to the response
    merged_pdf_content.seek(0)
    response.write(merged_pdf_content.read())

    # Clean up the temporary HTML-to-PDF file
    os.remove(temp_html_pdf_path)

    if not paper.date_submitted:
        return response
    else:
        return


def original_files(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    context = {
        'paper': review.paper_reviewer.paper,
        'review': review,
        'paper_reviewer': review.paper_reviewer
    }    

    return render(request, 'partials/paper/original_files.html', context)


def view_proof(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    context = {
        'paper': review.paper_reviewer.paper,
        'review': review,
        'paper_reviewer': review.paper_reviewer
    }    

    return render(request, 'partials/paper/view_proof.html', context)



# def merge_pdfs(request, paper_id):
#     paper = Paper.objects.get(id=paper_id)
#     files = File.objects.filter(paper=paper)

#     if not files:
#         return HttpResponse("No files to merge")

#     pdf_writer = PdfWriter()

#     for file in files:
#         doc_path = file.file.path
#         pdf_path = convert_to_pdf(doc_path)

#         if pdf_path:
#             print(pdf_path)
#             pdf_reader = PdfReader(pdf_path)

#             for page_num in range( len(pdf_reader.pages)):
#                 page = pdf_reader.pages[page_num]
#                 pdf_writer.add_page(page)

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename=merged.pdf'

#     # Write the merged PDF to the response
#     pdf_writer.write(response)

#     return response


# def merge_pdfs(request, paper_id):
#     paper = Paper.objects.get(id=paper_id)
#     files = File.objects.filter(paper=paper)

#     if not files:
#         return HttpResponse("No files to merge")

#     merger = PdfMerger()
#     for file in files:
#         doc_path = file.file.path
#         pdf_path = convert_to_pdf(doc_path)

#         merger.append(pdf_path)
    
#      # Create an HttpResponse with the merged PDF as content
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename="merged.pdf"'

#     # Write the merged PDF content to the response
#     merger.write(response)
#     merger.close()

#     return response




def agree_to_review(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = "Agreed"
    paper_reviewer.save()

    review = Review.objects.create(paper_reviewer=paper_reviewer, due_date = (datetime.now() + timedelta(days=20)).replace(hour=23, minute=59), revision = revision_number(paper_reviewer.paper.journal_id))

    # send_review_invitation_email2(request, paper_reviewer)

    return redirect(login)

def decline_to_review(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = "Declined"
    paper_reviewer.save()

    paper = paper_reviewer.paper

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
    
    if not paper_reviewers.filter(status='') and (paper_reviewers.filter(status='Agreed') | paper_reviewers.filter(status='Invited')).count() < paper.required_reviews:
        try:
            paper_reviewer = Paper_Reviewer.objects.get(status='Alternate', order=1)
        except:
            paper_reviewer = None

        if paper_reviewer:
            paper_reviewer.status = 'Invited'
            paper_reviewer.invite_sent_date = datetime.now().date()
            paper_reviewer.save()
            send_review_invitation_email(request, paper_reviewer)

            reorder_reviewers(paper_id=paper.id)


    return render(request, 'paper/reviewer_invitations.html')

def decline_to_review_mail(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = "Declined"
    paper_reviewer.save()

    paper = paper_reviewer.paper

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
    
    if not paper_reviewers.filter(status='') and (paper_reviewers.filter(status='Agreed') | paper_reviewers.filter(status='Invited')).count() < paper.required_reviews:
        try:
            paper_reviewer = Paper_Reviewer.objects.get(status='Alternate', order=1)
        except:
            paper_reviewer = None

        if paper_reviewer:
            paper_reviewer.status = 'Invited'
            paper_reviewer.invite_sent_date = datetime.now().date()
            paper_reviewer.save()
            send_review_invitation_email(request, paper_reviewer)

            reorder_reviewers(paper_id=paper.id)


    return redirect(login)