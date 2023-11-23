from datetime import datetime
import os
import time
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import resolve
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import Role, User
from paper.forms import AERecommendationForm, EICDecisionForm, ReviewForm
from paper.models import AERecommendation, AERecommendationFile, DecisionFile, EICDecision, Paper, Paper_Reviewer, PreferencePaper_Reviewer, Reviewer
from conference.utils import send_review_invitation_email, send_review_invitation_email2, send_review_withdrawal_email
from paper.utils import get_max_order_reviewer, reorder_reviewers


def select_ae(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.method == 'POST':
        selected_ae_id = request.POST.get('selected_ae')

        user = User.objects.get(id=selected_ae_id)
        paper.associate_editor = user

        paper.save() 

        AERecommendation.objects.create(paper=paper)

    context = {
        'paper': paper
    }

    return render(request, 'partials/assigned_ae.html', context) 
      


def get_papers_awaiting_rev_selection(papers):
    # papers = Paper.objects.all()
    # papers_awaiting_rev_selection = []
    # for paper in papers:
    #     paper_reviewers = Paper_Reviewer.objects.filter(Q(paper=paper) & (Q(status='') | Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted')))
    #     if paper_reviewers.count() < paper.required_reviews:
    #         papers_awaiting_rev_selection.append(paper)

    papers_awaiting_rev_selection = [
        paper for paper in papers
            if Paper_Reviewer.objects.filter(
                Q(paper=paper) & (Q(status='') | Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted'))
            ).count() < paper.required_reviews
    ]

    return papers_awaiting_rev_selection

def get_papers_awaiting_rev_invitation(papers):
    # papers = Paper.objects.all()
    # papers_awaiting_rev_invitation = []
    # for paper in papers:
    #     paper_reviewers = Paper_Reviewer.objects.filter(Q(paper=paper) & (Q(status='') | Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted')))
    #     if paper_reviewers.count() >= paper.required_reviews:
    #         paper_reviewers = paper_reviewers.filter(Q(paper=paper) & (Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted')))
    #         if paper.required_reviews > paper_reviewers:
    #             papers_awaiting_rev_invitation.append(paper)

    # papers_awaiting_rev_invitation = [
    #     paper for paper in papers
    #     if Paper_Reviewer.objects.filter(
    #         Q(paper=paper) & (Q(status='') | Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted'))
    #     ).count() >= paper.required_reviews and

    #     Paper_Reviewer.objects.filter(
    #         Q(paper=paper) & (Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted'))
    #     ).count() < paper.required_reviews
    # ]
    # return papers_awaiting_rev_invitation

    # papers_awaiting_rev_invitation = [
    # paper for paper in papers
    # if (
    #     Paper_Reviewer.objects.filter(
    #         Q(paper=paper, status__in=['', 'Agreed', 'Invited', 'Submitted'])
    #     ).count() >= paper.required_reviews
    #     and
    #     Paper_Reviewer.objects.filter(
    #         Q(paper=paper, status__in=['Agreed', 'Invited', 'Submitted'])
    #     ).count() < paper.required_reviews
    # )
    # ]
 
    papers_awaiting_rev_invitation = [
        paper for paper in papers
        if (paper_reviewers := Paper_Reviewer.objects.filter(
            Q(paper=paper) & (Q(status='') | Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted'))
        )).count() >= paper.required_reviews and

        paper_reviewers.filter(
            Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted')
        ).count() < paper.required_reviews
    ]

    return papers_awaiting_rev_invitation


def get_papers_awaiting_rev_assignment(papers):
    papers_awaiting_rev_assignment = [
        paper for paper in papers
        if (paper_reviewers := Paper_Reviewer.objects.filter(
            Q(paper=paper) & (Q(status='Agreed') | Q(status='Invited') | Q(status='Submitted'))
        )).count() >= paper.required_reviews and

        paper_reviewers.filter(
            Q(status='Submitted')
        ).count() < paper.required_reviews
    ]

    return papers_awaiting_rev_assignment

def get_papers_awaiting_ae_recommendation(papers):
    papers_awaiting_ae_recommendation = [
        paper for paper in papers
        if Paper_Reviewer.objects.filter(
            Q(paper=paper) & Q(status='Submitted')
        ).count() >= paper.required_reviews

        and

        AERecommendation.objects.get(paper=paper).date_submitted == None
    ]

    return papers_awaiting_ae_recommendation

def get_papers_submitted_ae_recommendation(papers):
    papers_submitted_ae_recommendation = [
        paper for paper in papers
        if Paper_Reviewer.objects.filter(
            Q(paper=paper) & Q(status='Submitted')
        ).count() >= paper.required_reviews

        and

        AERecommendation.objects.get(paper=paper).date_submitted != None
    ]

    return papers_submitted_ae_recommendation


def get_status_count_multiple_papers(papers):
    i = 0
    status_count = []
    for paper in papers:
        paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)
        counts = [paper_reviewers.filter(status=status).count() for status in ["", "Invited", "Agreed", "Declined", "Submitted"]]
        counts[0] = sum(counts) 
        status_count.append(counts)
        i += 1

    return status_count    



def display_papers_awaiting_reviewer_selection(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_awaiting_rev_selection(papers)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_count = get_status_count_multiple_papers(papers)

    zipped_data = zip(page_obj, status_count)

    context = {
        'type': 'papers_awaiting_reviewer_selection', 
        'zipped_data': zipped_data
    }

    return render(request, 'conference/awaiting_reviewer_selection.html', context)
   

def display_papers_awaiting_reviewer_invitation(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_awaiting_rev_invitation(papers)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_count = get_status_count_multiple_papers(papers)

    zipped_data = zip(page_obj, status_count)

    context = {
        'type': 'papers_awaiting_reviewer_invitation',
        'zipped_data': zipped_data
    }

    return render(request, 'conference/awaiting_reviewer_invitation.html', context)


def display_papers_awaiting_reviewer_assignment(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_awaiting_rev_assignment(papers)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_count = get_status_count_multiple_papers(papers)

    zipped_data = zip(page_obj, status_count)

    context = {
        'zipped_data': zipped_data,
        'type': 'papers_awaiting_reviewer_assignment',
        'page_obj': page_obj
    }

    return render(request, 'conference/awaiting_reviewer_assignment.html', context)


def display_papers_awaiting_ae_recommendation(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_awaiting_ae_recommendation(papers)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_count = get_status_count_multiple_papers(papers)

    zipped_data = zip(page_obj, status_count)

    context = {
        'zipped_data': zipped_data,
        'type': 'papers_awaiting_ae_recommendation'
    }

    return render(request, 'conference/awaiting_ae_recommendation.html', context)


def display_papers_submitted_ae_recommendation(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_submitted_ae_recommendation(papers)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_count = get_status_count_multiple_papers(papers)

    zipped_data = zip(page_obj, status_count)

    context = {
        'zipped_data': zipped_data,
        'type': 'papers_awaiting_ae_recommendation'
    }

    return render(request, 'conference/submitted_ae_recommendation.html', context)


def display_papers_awaiting_ae_selection(request):
    papers = Paper.objects.filter(associate_editor=None)

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type': 'papers_awaiting_ae_selection'
    }

    return render(request, 'conference/awaiting_ae_selection.html', context)


def display_papers_awaiting_ae_assignment(request):
    papers = Paper.objects.filter(Q(aerecommendation__date_submitted__isnull=True))

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type': 'papers_awaiting_ae_assignment'
    }

    return render(request, 'conference/awaiting_ae_assignment.html', context)


def display_papers_awaiting_eic_decision(request):
    papers = Paper.objects.filter(Q(aerecommendation__date_submitted__isnull=False) & Q(eicdecision__date_submitted__isnull=True))

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type': 'papers_awaiting_eic_decision'
    }

    return render(request, 'conference/awaiting_eic_decision.html', context)

def display_papers_submitted_eic_decision(request):
    papers = Paper.objects.filter(Q(eicdecision__date_submitted__isnull=False))

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'type': 'papers_submitted_eic_decision'
    }

    return render(request, 'conference/submitted_eic_decision.html', context)


def edit_reviewer(request, paper_id, reviewer_id):
    first_name = request.POST.get('first_name').capitalize()
    last_name = request.POST.get('last_name').capitalize()

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)
    reviewer.first_name = first_name
    reviewer.last_name = last_name
    reviewer.save()
    
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
    status_count = [paper_reviewers.filter(status=status).count() for status in ["", "Invited", "Agreed", "Declined", "Submitted"]]
    status_count[0] = sum(status_count[0:])

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


def view_review(request, paper_reviewer_id):
    paper_reviewer = get_object_or_404(Paper_Reviewer, id=paper_reviewer_id)
    review = paper_reviewer.review

    form = ReviewForm(instance=review)

    for field_name in ['what_should_be_deleted', 'comments_to_editor', 'comments_to_author']: 
            form.fields[field_name].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'review': review,
    }    
    return render(request, 'conference/view_review.html', context)


def view_recommendation(request, aerecommendation_id):
    recommendation = get_object_or_404(AERecommendation, id=aerecommendation_id)

    form = AERecommendationForm(instance=recommendation)

    for field_name in ['comments_to_eic', 'comments_to_author']: 
            form.fields[field_name].widget.attrs['readonly'] = True

    context = {
        'form': form,
        'recommendation': recommendation,
    }    
    return render(request, 'conference/view_recommendation.html', context)
    



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


def delete_reviewer(request, paper_id, reviewer_id): # from Main Reviewer list
    paper = get_object_or_404(Paper, id=paper_id)
    paper.reviewers.remove(reviewer_id)

    reorder_reviewers(paper_id)

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    papers = Paper.objects.filter(paper_reviewer__reviewer_id=reviewer)
    if not papers and not PreferencePaper_Reviewer.objects.filter(reviewer=reviewer):
        reviewer.delete()

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)  

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'paper': paper,
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper_id),
        'preferencepaper_reviewers': preferencepaper_reviewers
    }  

    return render(request, 'partials/add-remove_reviewers.html', context)

def remove_reviewer(request, paper_reviewer_id): # from Alternate Reviewer list
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = ''
    paper_reviewer.save()

    paper = paper_reviewer.paper

    reorder_reviewers(paper.id)

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper_reviewers': paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id)
    }    

    return render(request, 'partials/reviewers+progress.html', context)

def add_alternate_reviewer(request, paper_reviewer_id):
    paper_reviewer = Paper_Reviewer.objects.get(id=paper_reviewer_id)
    paper_reviewer.status = 'Alternate'
    paper_reviewer.save()

    paper = paper_reviewer.paper
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    reorder_reviewers(paper.id)

    context = {
            "paper_reviewers": paper_reviewers,
            'paper': paper,
            'status_count': get_status_count(paper.id)
        }

    return render(request, 'partials/reviewers+progress.html', context)


def ae_affairs(request, type):
    papers = Paper.objects.all()
    if type == 'papers_awaiting_ae_selection':
        papers = Paper.objects.filter(associate_editor=None)
        if not papers:
            return redirect('awaiting_ae_selection')
    elif type == 'papers_awaiting_ae_assignment':    
        papers = Paper.objects.filter(Q(aerecommendation__date_submitted__isnull=True))
        if not papers:
            return redirect('awaiting_ae_assignment')
    elif type == 'papers_awaiting_eic_decision':
        papers = Paper.objects.filter(Q(aerecommendation__date_submitted__isnull=False))
        if not papers:
            return redirect('awaiting_eic_decision')   
    else:
        papers = Paper.objects.filter(Q(eicdecison__date_submitted__isnull=True))

    paginator = Paginator(papers, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the specific Paper object from the queryset based on the page number
    current_paper_index = (page_obj.number - 1) * paginator.per_page
    paper = papers[current_paper_index]  

    context = {
        'page_obj': page_obj,
        'type': type,
    }

    if type == 'papers_awaiting_ae_selection':
        associate_editors = User.objects.filter(roles=Role.objects.get(name='AE'))
        context['associate_editors'] = associate_editors
    elif type == 'papers_awaiting_eic_decision':
        form = EICDecisionForm(instance=EICDecision.objects.get(paper=paper))
        context.update({
            'form': form,
            'decision': paper.eicdecision,
            'paper_reviewers': Paper_Reviewer.objects.filter(paper=paper)  
        })

    return render(request, 'conference/ae_affairs.html', context)  



def rev_affairs(request, type):
    papers = Paper.objects.filter(associate_editor=request.user)
    if type == 'papers_awaiting_reviewer_selection':
        papers = get_papers_awaiting_rev_selection(papers)
        if not papers:
            return redirect('awaiting_reviewer_selection')
    elif type == 'papers_awaiting_reviewer_invitation':
        papers = get_papers_awaiting_rev_invitation(papers)
        if not papers:
            return redirect('awaiting_reviewer_invitation')
    elif type == 'papers_awaiting_reviewer_assignment':       
        papers =  get_papers_awaiting_rev_assignment(papers)
        if not papers:
            return redirect('awaiting_reviewer_assignment')
    else:
        papers = get_papers_awaiting_ae_recommendation(papers)    
    
    paginator = Paginator(papers, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the specific Paper object from the queryset based on the page number
    current_paper_index = (page_obj.number - 1) * paginator.per_page
    paper = papers[current_paper_index]
    
    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'users': get_matching_users(paper.id),
        'page_obj': page_obj,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id),
        'type': type,
        'preferencepaper_reviewers': preferencepaper_reviewers
    }

    if type == 'papers_awaiting_ae_recommendation':
        form = AERecommendationForm(instance=AERecommendation.objects.get(paper=paper))
        context['form'] = form
        context['recommendation'] = paper.aerecommendation

    return render(request, 'conference/reviewer_affairs.html', context)


def ae_recommendation(request):
    papers = Paper.objects.filter(associate_editor=request.user)
    papers = get_papers_submitted_ae_recommendation(papers)   

    paginator = Paginator(papers, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the specific Paper object from the queryset based on the page number
    current_paper_index = (page_obj.number - 1) * paginator.per_page
    paper = papers[current_paper_index]

    recommendation = AERecommendation.objects.get(paper=paper)

    form = AERecommendationForm(instance=recommendation)
    for field_name in ['recommendation', 'comments_to_eic', 'comments_to_author']:  
            form.fields[field_name].widget.attrs['readonly'] = True

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    context = {
        'paper': paper,
        'form': form,
        'page_obj': page_obj,
        'paper_reviewers': paper_reviewers,
        'recommendation': recommendation
    }  
    return render(request, 'conference/ae_recommendation.html', context)   

def eic_decision(request):
    papers = Paper.objects.filter(Q(eicdecision__date_submitted__isnull=False))

    paginator = Paginator(papers, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the specific Paper object from the queryset based on the page number
    current_paper_index = (page_obj.number - 1) * paginator.per_page
    paper = papers[current_paper_index]

    decision = EICDecision.objects.get(paper=paper)

    form = EICDecisionForm(instance=decision)
    for field_name in ['decision', 'comments']:  
            form.fields[field_name].widget.attrs['readonly'] = True

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)        

    context = {
        'paper': paper,
        'form': form,
        'page_obj': page_obj,
        'paper_reviewers': paper_reviewers,
        'decision': decision
    }  
    return render(request, 'conference/eic_decision.html', context)   



def sort_reviewers(request):
    reviewer_pks_order = request.POST.getlist('reviewer_order')
    paper_reviewers = []
    for idx, reviewer_pk in enumerate(reviewer_pks_order, start=1):
        paper_reviewer = Paper_Reviewer.objects.get(pk=reviewer_pk)
        paper_reviewer.order = idx
        paper_reviewer.save()
        paper_reviewers.append(paper_reviewer)

    paper = Paper.objects.get(id=paper_reviewers[0].paper.id)  

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

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

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id),
        'preferencepaper_reviewers': preferencepaper_reviewers
    }
    return render(request, 'partials/add-remove_reviewers.html', context)


def add_preference_reviewer(request, paper_reviewer_id):
    paper_reviewer = PreferencePaper_Reviewer.objects.get(id=paper_reviewer_id)
    paper = paper_reviewer.paper
    reviewer = paper_reviewer.reviewer

    Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, preference=paper_reviewer.preference, order=get_max_order_reviewer(paper.id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'users': get_matching_users(paper.id),
        'paper_reviewers': paper_reviewers,
        'paper': paper,
        'status_count': get_status_count(paper.id),
        'preferencepaper_reviewers': preferencepaper_reviewers
    }
    return render(request, 'partials/add-remove_reviewers.html', context)


def add_user_as_reviewer(request, paper_id, user_id):
    user = get_object_or_404(User, id=user_id)
    user.roles.add(Role.objects.get(name='REV'))

    reviewer = Reviewer.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)[0]

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'users': get_matching_users(paper_id),
        'paper': paper,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id),
        'preferencepaper_reviewers': preferencepaper_reviewers
    }

    return render(request, 'partials/add-remove_reviewers.html', context)


def add_reviewer_as_reviewer(request, paper_id, reviewer_id):
    reviewer = get_object_or_404(Reviewer, id=reviewer_id)

    paper = Paper.objects.get(id=paper_id)

    if not Paper_Reviewer.objects.filter(paper=paper, reviewer=reviewer).exists():
        Paper_Reviewer.objects.create(paper=paper, reviewer=reviewer, order=get_max_order_reviewer(paper_id))

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper)

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'paper': paper,
        'users': get_matching_users(paper_id),
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id),
        'preferencepaper_reviewers': preferencepaper_reviewers
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

    preferencepaper_reviewers = PreferencePaper_Reviewer.objects.filter(paper=paper).exclude(reviewer__in=paper.reviewers.all())  

    context = {
        'users': get_matching_users(paper_id),
        'paper': paper,
        'paper_reviewers': paper_reviewers,
        'status_count': get_status_count(paper.id),
        'preferencepaper_reviewers': preferencepaper_reviewers
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


def upload_ae_files(request, recommendation_id):
    recommendation = get_object_or_404(AERecommendation, id=recommendation_id)

    duplicate_files = []
    
    saved_files = AERecommendationFile.objects.filter(aerecommendation=recommendation)
    file_list = []
    for file in saved_files:
        file_list.append(os.path.basename(file.file.name))

    files = request.FILES.getlist('ae_files[]')   

    for file in files:
        if file.name in file_list:
            duplicate_files.append(file.name)
        else: 
            file_list.append(file.name)      
            AERecommendationFile.objects.create(file=file, aerecommendation=recommendation)  

    context = {
        'recommendation': recommendation,
        'duplicate_files': duplicate_files,
    }

    return render(request, 'partials/conference/ae_files.html', context) 

def delete_ae_file(request, recommendation_id, file_id):
    recommendation = get_object_or_404(AERecommendation, id=recommendation_id)

    file = get_object_or_404(AERecommendationFile, id=file_id)
    # file.file.delete(save=False)
    file.delete()

    context = {
        'recommendation': recommendation,
    }
    return render(request, 'partials/conference/ae_files.html', context) 


def save_recommendation(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    recommendation = AERecommendation.objects.get(paper=paper)

    form = AERecommendationForm(request.POST, instance=recommendation)
    recommendation = form.save(commit=False)
    recommendation.save()

    context = {
        'paper': paper,
        'form': form,
        'recommendation': recommendation,
    }    

    return render(request, 'partials/conference/ae_form.html', context)

def submit_recommendation(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    recommendation = AERecommendation.objects.get(paper=paper)
    recommendation.date_submitted = datetime.now()
    recommendation.save()

    EICDecision.objects.create(paper=paper)

    return redirect('submitted_ae_recommendation')
    

def save_decision_files(request, decision_id):
    decision = get_object_or_404(EICDecision, id=decision_id)

    duplicate_files = []
    
    saved_files = DecisionFile.objects.filter(decision=decision)
    file_list = []
    for file in saved_files:
        file_list.append(os.path.basename(file.file.name))

    files = request.FILES.getlist('eic_files[]')   

    for file in files:
        if file.name in file_list:
            duplicate_files.append(file.name)
        else: 
            file_list.append(file.name)      
            DecisionFile.objects.create(file=file, decision=decision) 

    context = {
        'decision': decision,
        'duplicate_files': duplicate_files,
    }

    return render(request, 'partials/conference/eic_files.html', context) 


def delete_decision_file(request, decision_id, file_id):
    decision = get_object_or_404(EICDecision, id=decision_id)

    file = get_object_or_404(DecisionFile, id=file_id)
    # file.file.delete(save=False)
    file.delete()

    context = {
        'decision': decision,
    }
    return render(request, 'partials/conference/eic_files.html', context) 


def save_decision(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    decision = EICDecision.objects.get(paper=paper)

    form = EICDecisionForm(request.POST, instance=decision)
    decision = form.save(commit=False)
    decision.save()

    context = {
        'paper': paper,
        'form': form,
        'decision': decision,
    }    

    return render(request, 'partials/conference/eic_form.html', context)


    

def submit_decision(request, paper_id):
    paper = Paper.objects.get(id=paper_id)

    decision = EICDecision.objects.get(paper=paper)
    decision.date_submitted = datetime.now()
    decision.save()

    paper_reviewers = Paper_Reviewer.objects.filter(paper=paper, status__in = ['Invited', 'Agreed'])
    for paper_reviewer in paper_reviewers:
        paper_reviewer.status = ''
        paper_reviewer.invite_sent_date = None
        paper_reviewer.save()
        send_review_withdrawal_email(paper_reviewer)
        if paper_reviewer.review:
            paper_reviewer.review.delete()


    return redirect('submitted_eic_decisions')
        