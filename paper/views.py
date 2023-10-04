from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Q

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

from .forms import AuthorForm, PaperForm1, PaperForm2, PaperForm3, ReviewForm, additionalAttributeFormSet
from .models import Author, File, Paper, Paper_Author, Paper_Reviewer, Review, additionalAttribute
from .utils import get_max_order_author, get_max_order_file, reorder_authors, reorder_files

# Create your views here.

def check_role_author(user):
    if user.role == 'Author':
        return True
    else:
        raise PermissionDenied  


def upload_cover_letter(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    file = request.FILES.get('cover_letter_file')

    if file:
        paper.cover_letter_file = file
        paper.save()

    context = {
        'paper': paper 
    }
    return render(request, 'paper/submit_paper/step5.html', context)    


def show_cover_letter(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    context = {
        'paper': paper 
    }
    return render(request, 'partials/cover_letter.html', context)    



def delete_cover_letter(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.cover_letter_file = None
    paper.save()

    return render(request, 'partials/cover_letter.html')



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

    return render(request, 'partials/authors.html', {'paper_authors': paper_authors})


def search_user1(request, paper_id):
    email = request.POST.get('email')

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
         
    context = {
        'user': user,
        'author': author,
        'paper_id': paper_id
    }
    return render(request, 'partials/search_user_result1.html', context)


def search_user2(request, paper_id):
    email = request.POST.get('email')

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
         
    context = {
        'user': user,
        'author': author,
        'paper_id': paper_id
    }
    return render(request, 'partials/search_user_result2.html', context)


def add_user_as_author(request, paper_id, user_id):
    user = get_object_or_404(User, id=user_id)

    author = Author.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)[0]

    paper = Paper.objects.get(id=paper_id)
    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    context = {
        'paper': paper,
        'paper_authors': paper_authors
    }

    return render(request, 'partials/authors.html', context)


def add_author_as_author(request, paper_id, author_id):
    author = get_object_or_404(Author, id=author_id)

    paper = Paper.objects.get(id=paper_id)
    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)

    context = {
        'paper': paper,
        'paper_authors': paper_authors
    }

    return render(request, 'partials/authors.html', context)


def add_new_author(request, paper_id):
    email = request.POST.get('email').lower()
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()

    author = Author.objects.create(first_name=first_name, last_name=last_name, email=email)  
    author.save() 
        
    paper = Paper.objects.get(id=paper_id)    
    #paper.authors.add(author)
    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper_id))

    paper_authors = Paper_Author.objects.filter(paper=paper)
    context = {
        'paper_authors': paper_authors
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

    return render(request, 'partials/authors.html', {'paper_authors': paper_authors})


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

    author = get_object_or_404(Author, id=author_id)
    author.first_name = first_name
    author.last_name = last_name
    author.save()

    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)
    context = {
        'paper_authors': paper_authors
    }

    return render(request, 'partials/authors.html', context)


def coAuthored_manuscripts(request):
    try: 
        papers = Paper.objects.filter(is_submitted=True).exclude(submitter=request.user).filter(Q(authors__user=request.user))
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/co-authored_manuscripts.html', context)

              
def submitted_manuscripts(request):
    try: 
        papers = Paper.objects.filter(is_submitted=True, submitter=request.user)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/submitted_manuscripts.html', context)


def unsubmitted_manuscripts(request):
    try: 
        papers = Paper.objects.filter(is_submitted=False, submitter=request.user)
    except:
        papers = None    
    context = {
        'papers': papers,
    }
    return render(request, 'paper/unsubmitted_manuscripts.html', context)

def start_new_submission(request):
    return render(request, 'paper/start_new_submission.html')

def submit_paper_step0(request):
    paper = Paper.objects.create(submitter = request.user, journal_id="draft")

    author = Author.objects.get_or_create(user=request.user, first_name=request.user.first_name, last_name=request.user.last_name, email=request.user.email)[0]

    Paper_Author.objects.create(paper=paper, author=author, order=get_max_order_author(paper.id))
    
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
        elif next == 'step3':
            return redirect('submit_paper_step3', paper_id)
        elif next == 'step4':
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        elif next == 'step6':
            return redirect('submit_paper_step6', paper_id)
    else:
        form = PaperForm1(instance=paper)

    context = {
        'paper': paper,
        'form': form,
    }        

    return render(request, 'paper/submit_paper/step1.html', context)        


def submit_paper_step2(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)
    context = {
        'paper': paper,
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

            for form in formset:
                attribute = form.save(commit=False)
                if attribute.name != '':
                    attribute.paper = paper
                    attribute.save()

        next = request.GET.get('next')
        if next == 'step4' or 'save_and_continue' in request.POST:
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step1':
            return redirect('submit_paper_step1', paper_id)
        elif next == 'step2':
            return redirect('submit_paper_step2', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        else:
            return redirect('submit_paper_step6', paper_id)
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
    file1 = request.FILES.get('file1')
    file2 = request.FILES.get('file2')
    file3 = request.FILES.get('file3')
    if file1:
        file = File.objects.create(paper=paper, file=file1, order=get_max_order_file(paper_id))
    if file2:
        file = File.objects.create(paper=paper, file=file2, order=get_max_order_file(paper_id)) 
    if file3:
        file = File.objects.create(paper=paper, file=file3, order=get_max_order_file(paper_id)) 

    context = {
        'paper': paper
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
        if next == 'step1':
            return redirect('submit_paper_step1', paper_id)
        elif next == 'step2':
            return redirect('submit_paper_step2', paper_id)
        elif next == 'step3':
            return redirect('submit_paper_step3', paper_id)
        elif next == 'step4':
            return redirect('submit_paper_step4', paper_id)
        elif next == 'step5':
            return redirect('submit_paper_step5', paper_id)
        else:
            return redirect('submit_paper_step6', paper_id)
    else:
        form = PaperForm2(instance=paper)

    context = {
        'paper': paper,
        'form': form
    }        

    return render(request, 'paper/submit_paper/step5.html', context)   

def submit_paper_step6(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_authors = Paper_Author.objects.filter(paper=paper)
    form = PaperForm2(instance=paper)
    for field_name in ['cover_letter', 'number_of_tables', 'number_of_figures', 'word_count', 'figures_tables_published_elsewhere_desc']:  # Replace with the field names you want to make readonly
            form.fields[field_name].widget.attrs['readonly'] = True
    context = {
        'paper': paper,
        'paper_authors': paper_authors,
        'form': form
    }  
    return render(request, 'paper/submit_paper/step6.html', context)   


def submit_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    paper.is_submitted = True

    paper.journal_id = 'JAIR-' + str(paper.id)

    paper.date_submitted = datetime.now().date()

    paper.save()

    role = Role.objects.get(name='Author')
    paper.submitter.roles.add(role)

    return redirect(submitted_manuscripts)


def delete_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    authors_to_delete = paper.authors.all()
    
    for author in authors_to_delete:
        papers = Paper.objects.filter(authors=author).exclude(id=paper_id)

        if not papers:
            author.delete()

    reviewers_to_delete = paper.authors.all()
    
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

@login_required(login_url='loginAuthor')
@user_passes_test(check_role_author)
def accept_or_decline_to_review(request, paper_id):
    paper = Paper.objects.get(id=paper_id)
    context = {
        "paper": paper
    }
    return render(request, 'paper/accept_or_decline_to_review.html', context)

def decline_to_review(request, paper_id):
    paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
    paper_reviewer.status = 'declined'
    paper_reviewer.save()
  
    return redirect('myAccount')

def delete_review(request, paper_id):
    review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
    review.delete()
    return redirect('myAccount')

# def review(request, paper_id):
#     paper = Paper.objects.get(id=paper_id)

#     paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
#     paper_reviewer.status = 'accepted'
#     paper_reviewer.save()

#     try:
#         review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
#     except:
#         review = None

#     if request.method == 'POST':
#         form = ReviewForm(request.POST, instance=review)
#         review = form.save(commit=False)
#         review.paper = paper
#         review.reviewer = paper_reviewer.reviewer
#         review.save()
#         return redirect('myAccount')
#     else:
#         form = ReviewForm(instance=review)    
#     context = {
#         'form': form,
#         'paper': paper,
#         'review': review
#     }
#     return render(request, 'paper/review.html', context)


    # questions = []
    # q1 = Question.objects.create(text="What is your age?")
    # q2 = Question.objects.create(text="What is your favourite fruit?")
    # questions.append(q1, q2)

    # o1 = Option.objects.create(text="10", question=q1)
    # o2 = Option.objects.create(text="20", question=q1)

    # o1 = Option.objects.create(text="", question=q2)

def review(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    paper_reviewer = Paper_Reviewer.objects.get(paper=paper_id, reviewer__user=request.user)
    paper_reviewer.status = 'accepted'
    paper_reviewer.save()

    try:
        review = Review.objects.get(paper=paper_id, reviewer__user=request.user) 
    except:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        review = form.save(commit=False)
        review.paper = paper
        review.reviewer = paper_reviewer.reviewer
        if 'save_draft' in request.POST:
            review.is_submitted = False 
        else:
            review.is_submitted = True       
        review.save()
        return redirect('myAccount')
    else:
        form = ReviewForm(instance=review)

    # questions = Question.objects.all()    
    # formset = OptionModelFormset()

    context = {
        # 'questions': questions,
        'paper': paper,
        'form': form,
        'review': review
    }    
    return render(request, 'paper/review.html', context)


def convert_to_pdf(doc_path):
    # Function to convert various file types to PDF
    file_extension = os.path.splitext(doc_path)[-1].lower()

    print(file_extension)

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
        print(pdf_path)

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
        print(pdf_path)

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

    # Create an HttpResponse with the merged PDF as content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="merged.pdf"'

    # Write the merged PDF content to the response
    merger.write(response)
    merger.close()

    # Clean up the temporary HTML-to-PDF file
    os.remove(temp_html_pdf_path)

    return response





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