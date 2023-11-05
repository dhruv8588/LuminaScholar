from datetime import datetime
import time
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.core.paginator import Paginator
from django.db.models import Q, F, Count

from accounts.models import Role, User
from paper.models import Paper, Paper_Reviewer, Review, Reviewer
from conference.utils import send_review_invitation_email, send_review_invitation_email2
from paper.utils import get_max_order_reviewer, reorder_reviewers
# from .utils import send_approval_request_email

from .forms import UserModelFormset, ReviewerForm

def check_role_admin(user):
    if user.is_admin == True:
        return True
    else:
        raise PermissionDenied


def eic_dashboard(request):
    return render(request, 'conference/eic_dashboard.html')

def awaiting_ae_assignment(request):
    papers = Paper.objects.all()

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }
    return render(request, 'conference/awaiting_ae_assignment.html', context)

def select_ae(request, page_number):
    associate_editor_role = Role.objects.get(name='AE')
    
    associate_editors = User.objects.filter(roles=associate_editor_role)

    papers = Paper.objects.all()
    paginator = Paginator(papers, 1)

    page_obj = paginator.get_page(page_number)
        
    context = {
        'associate_editors': associate_editors,
        "page_obj": page_obj,
        'papers':papers,
    }
    return render(request, 'conference/assign_ae.html', context)

def assign_ae(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        selected_ae_id = request.POST.get('selected_ae')

        user = User.objects.get(id=selected_ae_id)
        print(selected_ae_id)
        paper.associate_editor = user

        paper.save() 

    context = {
        'paper': paper
    }

    return render(request, 'partials/assigned_ae.html', context)   


def ae_dashboard(request):
    return render(request, 'conference/ae_dashboard.html')



def awaiting_rev_selection(request):
    # papers = Paper.objects.all()
    # papers_awaiting_rev_selection = []
    # for paper in papers:
    #     paper_reviewers = Paper_Reviewer.objects.filter(Q(paper=paper) & (Q(status='') | Q(status='Accepted') | Q(status='Invited') | Q(status='Submitted')))
    #     if paper_reviewers.count() < paper.required_reviews:
    #         papers_awaiting_rev_selection.append(paper)

    papers_awaiting_rev_selection = [
        paper for paper in Paper.objects.all()
            if Paper_Reviewer.objects.filter(
                Q(paper=paper) & (Q(status='') | Q(status='Accepted') | Q(status='Invited') | Q(status='Submitted'))
            ).count() < paper.required_reviews
    ]

    papers = papers_awaiting_rev_selection

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }
    return render(request, 'conference/awaiting_rev.html', context)
   


def awaiting_rev_invitation(request):
    # papers = Paper.objects.all()
    # papers_awaiting_rev_invitation = []
    # for paper in papers:
    #     paper_reviewers = Paper_Reviewer.objects.filter(Q(paper=paper) & (Q(status='') | Q(status='Accepted') | Q(status='Invited') | Q(status='Submitted')))
    #     if paper_reviewers.count() >= paper.required_reviews:
    #         paper_reviewers = paper_reviewers.filter(status='Invited')
    #         if paper.required_reviews > paper_reviewers:
    #             papers_awaiting_rev_invitation.append(paper)

    papers_awaiting_rev_invitation = [
        paper for paper in Paper.objects.all()
        if Paper_Reviewer.objects.filter(
            Q(paper=paper) & (Q(status='') | Q(status='Accepted') | Q(status='Invited') | Q(status='Submitted'))
        ).count() >= paper.required_reviews and
        paper.required_reviews > Paper_Reviewer.objects.filter(paper=paper, status='Invited').count()
    ]

    papers = papers_awaiting_rev_invitation

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }

    return render(request, 'conference/awaiting_rev.html', context)


def awaiting_rev_assignment(request):
    awaiting_rev_assignment = [
        paper for paper in Paper.objects.all()
        if Paper_Reviewer.objects.filter(
            Q(paper=paper) & (Q(status='') | Q(status='Accepted') | Q(status='Invited') | Q(status='Submitted'))
        ).count() >= paper.required_reviews and
        paper.required_reviews <= Paper_Reviewer.objects.filter(paper=paper, status='Invited').count()
    ]

    papers = awaiting_rev_assignment

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }

    return render(request, 'conference/awaiting_rev.html', context)



def awaiting_ae_recommendation(request):
    awaiting_ae_recommendation = [
        paper for paper in Paper.objects.all()
        if Paper_Reviewer.objects.filter(
            Q(paper=paper) & Q(status='Submitted')
        ).count() >= paper.required_reviews
    ]

    papers = awaiting_ae_recommendation

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }

    return render(request, 'conference/awaiting_rev.html', context)


def edit_reviewer(request, paper_id, reviewer_id):
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()
    print(first_name)

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)
    print(reviewer)
    reviewer.first_name = first_name
    reviewer.last_name = last_name
    reviewer.save()
    # print(reviewer)
    paper = get_object_or_404(Paper, id=paper_id)
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper_reviewers': paper_reviewers,
        'paper': paper,
    }  

    return render(request, 'partials/reviewers.html', context)


def get_status_count(paper_id):
    paper = Paper.objects.get(id=paper_id)
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
    status_count = [paper_reviewers.filter(status=status).count() for status in ["Invited", "Agreed", "Declined"]]
    return status_count



def change_req_reviews(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        required_reviews = request.POST.get('required_reviews')
        paper.required_reviews = required_reviews
        paper.save()

    context = {
        'paper': paper,
        'status_count': get_status_count(paper.id),
        'changed': True
    }    

    return render(request, 'partials/progress.html', context)


def agree_to_review(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = "Agreed"
    paper_reviewer.save()

    send_review_invitation_email2(request, paper_reviewer)

    return render(request, 'accounts/login.html')

def decline_to_review(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = "Declined"
    paper_reviewer.save()

    return render(request, 'accounts/login.html')




def invite_rev(request, paper_rev_id):
    paper_reviewer = get_object_or_404(Paper_Reviewer, id=paper_rev_id)    

    paper_reviewer.status = "Invited"
    paper_reviewer.invite_sent_date = datetime.now().date()
    paper_reviewer.save()

    # send_review_invitation_email(request, paper_reviewer)
    time.sleep(5)

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper_reviewer.paper)
    paper = Paper.objects.get(id=paper_reviewer.paper.id)

    context = {
        "paper_reviewers": paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id)
    }

    return render(request, 'partials/reviewers+progress.html', context)
    

def invite_rev_all(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    # paper_reviewers.update(status='Invited')

    for paper_reviewer in paper_reviewers:
        if paper_reviewer.status == '':
            paper_reviewer.status = 'Invited'
            paper_reviewer.invite_sent_date = datetime.now().date()
            paper_reviewer.save()
            # send_review_invitation_email(request, paper_reviewer)
            time.sleep(3)

    context = {
        "paper_reviewers": paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id)
    }

    return render(request, 'partials/reviewers+progress.html', context)
        

def get_matching_users(paper_id):
    paper = Paper.objects.get(id=paper_id)

    matching_users = User.objects.filter(researchAreas__in=paper.attributes.all())

    users = User.objects.all()
    additionalAttributes = paper.additionalAttributes.all()
    id_list = []

    for user in users:
        research_areas_names = []
        for additionalResearchArea in user.additionalResearchAreas.all():
            research_areas_names.append(additionalResearchArea.name)
        for additionalAttribute in additionalAttributes:
            if any(additionalAttribute.name.replace(" ", "").lower() == research_area_name.replace(" ", "").lower() for research_area_name in research_areas_names):
                id_list.append(user.id)
                break

    matching_users = (User.objects.filter(id__in=id_list) | matching_users).distinct().exclude(reviewer__in=paper.reviewers.all())  

    return matching_users  


def delete_reviewer(request, paper_id, reviewer_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.reviewers.remove(reviewer_id)

    reorder_reviewers(paper_id)

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    papers = Paper.objects.filter(paper_reviewer__reviewer_id=reviewer)
    if not papers:
        reviewer.delete()

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)  

    context = {
        'paper': paper,
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper_id)
    }  

    return render(request, 'partials/add-remove_reviewers.html', context)


def rev_affairs(request):
    #paper = get_object_or_404(Paper, id=paper_id)

    # papers = Paper.objects.all().order_by('created_at')

    papers = Paper.objects.annotate(
        num_matching_reviewers=Count('reviewers', 
            filter=Q(reviewers__paper_reviewer__status__in=['', 'Invited', 'Agreed']))
    ).filter( 
        num_matching_reviewers__lt=F('required_reviews')
    ).order_by('created_at')

    paginator = Paginator(papers, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the specific Paper object from the queryset based on the page number
    current_paper_index = (page_obj.number - 1) * paginator.per_page
    paper = papers[current_paper_index]
  
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'users': get_matching_users(paper.id),
        'page_obj': page_obj,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id)
    }
    return render(request, 'conference/assign_rev.html', context)



def sort_reviewers(request):
    reviewer_pks_order = request.POST.getlist('reviewer_order')
    paper_reviewers = []
    for idx, reviewer_pk in enumerate(reviewer_pks_order, start=1):
        paper_reviewer = Paper_Reviewer.objects.get(pk=reviewer_pk)
        paper_reviewer.order = idx
        paper_reviewer.save()
        paper_reviewers.append(paper_reviewer)

    paper = Paper.objects.get(id=paper_reviewers[0].paper.id)    

    context = {
        'paper_reviewers': paper_reviewers,
        'paper': paper
    }    

    return render(request, 'partials/reviewers.html', context)


# def upload_file(request):




def select_rev(request, user_id, paper_id):
    user = User.objects.get(id=user_id)
    paper = Paper.objects.get(id=paper_id)

    reviewer = Reviewer.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)[0]
    reviewer.save()
                    
    Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id)
    }
    return render(request, 'partials/add-remove_reviewers.html', context)


def add_user_as_reviewer(request, paper_id, user_id):
    user = get_object_or_404(User, id=user_id)

    reviewer = Reviewer.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)[0]

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'users': get_matching_users(paper_id),
        'paper': paper,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id)
    }

    return render(request, 'partials/add-remove_reviewers.html', context)


def add_reviewer_as_reviewer(request, paper_id, reviewer_id):
    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper': paper,
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id)
    }

    return render(request, 'partials/add-remove_reviewers.html', context)



def add_new_reviewer(request, paper_id):
    email = request.POST.get('email').lower()
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()

    reviewer = Reviewer.objects.create(first_name=first_name, last_name=last_name, email=email)  
    reviewer.save() 
        
    paper = Paper.objects.get(id=paper_id)    
    Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'users': get_matching_users(paper_id),
        'paper': paper,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id)
    }

    return render(request, 'partials/add-remove_reviewers.html', context)


def search_user_rev(request, paper_id):
    email = request.POST.get('email')

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
        'paper_id': paper_id
    }
    return render(request, 'partials/search_user_rev_result.html', context)


# # case-sensitive and space-sensitive matching query
# additional_attributes = paper.additionalAttributes.values_list('name', flat=True)
# matching_users = User.objects.filter(
#         additionalResearchAreas__name__in=additional_attributes).distinct()


# # case-insensitive matching query not working
# matching_users = User.objects.filter(
#     additionalResearchAreas__name__icontains__in=additional_attributes
# )


# # case-insensitive matching query
# additional_attributes = [attr.name for attr in paper.additionalAttributes.all()]

# # Initialize a Q object for dynamic OR queries
# queries = Q()

# # Build OR queries for each attribute in additional_attributes
# for attribute in additional_attributes:
#     queries |= Q(additionalResearchAreas__name__icontains=attribute)  # instead of icontains, iexact could also be used

# matching_users = User.objects.filter(queries).distinct()




    # Filter in Python to handle space removal and case insensitivity
    # matching_users = [user for user in users if any(attr in user.additionalResearchAreas.values_list('name', flat=True).replace(" ", "").lower() for attr in additional_attributes)]

    # 'matching_users' now contains the users whose additionalResearchAreas names match any of the modified names in 'additional_attributes' list, case-insensitive and space-insensitive.

    # additional_attributes = [attr.name.replace(" ", "").lower() for attr in paper.additionalAttributes.all()]
    # matching_users = User.objects.filter(
    #     additionalResearchAreas__name__icontains=[attr.replace(" ", "").lower() for attr in additional_attributes]
    # ).distinct()