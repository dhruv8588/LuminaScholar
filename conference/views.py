from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.core.paginator import Paginator

from accounts.models import Role, User
from conference.models import Editor
from paper.forms import AssignEditorForm
from paper.models import Paper, Paper_Reviewer, Review, Reviewer
from conference.utils import send_review_invitation_email
# from .utils import send_approval_request_email

from .forms import UserModelFormset, ReviewerForm

def check_role_admin(user):
    if user.is_admin == True:
        return True
    else:
        raise PermissionDenied


def view_papers(request):
    papers = Paper.objects.all().order_by('created_at')

    # paper_reviewers = Paper_Reviewer.objects.filter(paper__in=papers)
    pending_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='pending')
    accepted_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='accepted')
    declined_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='declined')
    
    pending_reviewers = []
    accepted_reviewers = []
    declined_reviewers = []

    for paper_reviewer_pair in pending_paper_reviewer_pairs:
        pending_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in accepted_paper_reviewer_pairs:
        accepted_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in declined_paper_reviewer_pairs:
        declined_reviewers.append(paper_reviewer_pair.reviewer)

    context = {
        "papers": papers,
        "pending_reviewers": pending_reviewers,
        "accepted_reviewers": accepted_reviewers,
        "declined_reviewers": declined_reviewers 
    } 

    return render(request, 'conference/view_papers.html', context)


def edit_reviewer(request, paper_id, reviewer_id):
    papers = Paper.objects.all().order_by('created_at')

    
    target_paper = Paper.objects.get(id=paper_id)
    display_edit_reviewer_modal = True

    reviewer = get_object_or_404(Reviewer, id=reviewer_id)
    if request.method == 'POST':
        form = ReviewerForm(request.POST, instance=reviewer)
        if form.is_valid():
            # code starts here
            entered_email = reviewer.email.lower()
            orig = Reviewer.objects.get(id=reviewer_id)
            if entered_email != orig.email:
                flag = 0
                other_reviewers = Reviewer.objects.exclude(id=orig.id)
                for other_reviewer in other_reviewers:
                    if other_reviewer.email == entered_email:
                        target_paper.reviewers.add(other_reviewer.id)
                        send_review_invitation_email(request, reviewer, target_paper.id)
                        other_reviewer.first_name = reviewer.first_name #
                        other_reviewer.last_name = reviewer.last_name #
                        other_reviewer.save() #
                        target_paper.reviewers.remove(orig.id)
                        flag = 1
                if flag==1:
                    delete_orig = True
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.reviewers.all():
                            delete_orig = False
                            return redirect('view_papers')
                    if delete_orig == True:
                        orig.delete()
                        return redirect('view_papers')  
                elif flag == 0:
                    flag2 = 0
                    other_papers = Paper.objects.exclude(id=paper_id)
                    for other_paper in other_papers:
                        if orig in other_paper.reviewers.all():
                            target_paper.reviewers.remove(orig.id)
                            # create a new reviewer object with a different id and the field values of reviewer object
                            new_reviewer = Reviewer.objects.create(
                                first_name = reviewer.first_name,
                                last_name = reviewer.last_name,
                                email = reviewer.email
                            )
                            users = User.objects.all()
                            for user in users:
                                if user.email == new_reviewer.email:
                                    new_reviewer.user = user
                                    break
                            new_reviewer.save()
                            target_paper.reviewers.add(new_reviewer.id)
                            send_review_invitation_email(request, reviewer, target_paper.id)
                            
                            flag2 = 1
                    if flag2 == 0:
                        reviewer.save()
                    return redirect('view_papers')          
            else:
                orig.first_name = reviewer.first_name #
                orig.last_name = reviewer.last_name #
                orig.save() #
                return redirect('view_papers')
        else:
            print(form.errors)
    else:
        form = ReviewerForm(instance=reviewer)

    #####
    pending_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='pending')
    accepted_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='accepted')
    declined_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='declined')
    
    pending_reviewers = []
    accepted_reviewers = []
    declined_reviewers = []

    for paper_reviewer_pair in pending_paper_reviewer_pairs:
        pending_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in accepted_paper_reviewer_pairs:
        accepted_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in declined_paper_reviewer_pairs:
        declined_reviewers.append(paper_reviewer_pair.reviewer)

    context = {
        'papers': papers,
        'form': form,
        'target_paper': target_paper,
        'display_edit_reviewer_modal': display_edit_reviewer_modal,
        'reviewer_id': reviewer_id,

        'pending_reviewers': pending_reviewers,
        'accepted_reviewers': accepted_reviewers,
        'declined_reviewers': declined_reviewers
    }
    return render(request, 'conference/view_papers.html', context)       


def add_new_reviewer(request, paper_id):
    papers = Paper.objects.all().order_by('created_at')
    paper = Paper.objects.get(id=paper_id)
    display_add_new_reviewer_modal = True
    if request.method == 'POST':
        form = ReviewerForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            reviewers = Reviewer.objects.all()
            for reviewer in reviewers:
                if reviewer.email == email:
                    paper.reviewers.add(reviewer.id)

                    # send_review_invitation_email(request, reviewer, paper.id)

                    reviewer.first_name = form.cleaned_data['first_name'] #
                    reviewer.last_name = form.cleaned_data['last_name'] #
                    reviewer.save() #

                    return redirect('view_papers')
                
            reviewer = form.save(commit=False)
            users = User.objects.all()
            for user in users:
                if user.email == email:
                    reviewer.user = user
                    break
            reviewer.email = email
            form.save()

            paper.reviewers.add(reviewer.id)

            # send_review_invitation_email(request, reviewer, paper.id)

            return redirect('view_papers')
        else:
            print(form.errors)        
    else:
        form = ReviewerForm()

    #####
    pending_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='pending')
    accepted_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='accepted')
    declined_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='declined')
    
    pending_reviewers = []
    accepted_reviewers = []
    declined_reviewers = []

    for paper_reviewer_pair in pending_paper_reviewer_pairs:
        pending_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in accepted_paper_reviewer_pairs:
        accepted_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in declined_paper_reviewer_pairs:
        declined_reviewers.append(paper_reviewer_pair.reviewer)
    
    context = {
        'form': form,
        'paper': paper,
        'papers': papers,
        'display_add_new_reviewer_modal': display_add_new_reviewer_modal,

        'pending_reviewers': pending_reviewers,
        'accepted_reviewers': accepted_reviewers,
        'declined_reviewers': declined_reviewers
    }
    return render(request, 'conference/view_papers.html', context)       


def add_reviewer(request, paper_id):
    papers = Paper.objects.all().order_by('created_at')
    paper = Paper.objects.get(id=paper_id)
    display_add_reviewer_modal = True
    if request.method == 'POST':
        formset = UserModelFormset(request.POST)
        
        for form in formset:
            user = form.save(commit=False)
            is_invited = form.cleaned_data.get('is_invited')

            flag = 0
            if is_invited == True:
                reviewers = Reviewer.objects.all()
                for reviewer in reviewers:
                    if reviewer.user == user:
                        paper.reviewers.add(reviewer.id)
                        send_review_invitation_email(request, reviewer, paper.id)
                        flag = 1
                if flag == 0:
                    reviewer = Reviewer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
                    reviewer.save()
                    paper.reviewers.add(reviewer)  
                    send_review_invitation_email(request, reviewer, paper.id)
                
        return redirect('view_papers')
    else:
        # id_list = []
        # reviewers = paper.reviewers.all()
        # for reviewer in reviewers:
        #     if reviewer.user:
        #         id_list.append(reviewer.user.id)     
        # users = User.objects.exclude(id__in=id_list)
    
        # formset = UserModelFormset(queryset=users)

        # only filter(), all() and exclude() methods on User.objects will return the queryset; get() method won't
        keywords = paper.keywords.all()
        users = User.objects.filter(role='Author')
        id_list = []

        for user in users:
            research_areas_names = []
            for research_area in user.research_areas.all():
                research_areas_names.append(research_area.name)
            for keyword in keywords:                  
                if any(keyword.name.replace(" ", "").lower() == research_area_name.replace(" ", "").lower() for research_area_name in research_areas_names):    
                       id_list.append(user.id)
                       break

        reviewers = paper.reviewers.all()
        for reviewer in reviewers:
            if reviewer.user:
                if reviewer.user.id in id_list:
                    id_list.remove(reviewer.user.id)       

        users = User.objects.filter(id__in=id_list)
        formset = UserModelFormset(queryset=users)

    #####
    pending_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='pending')
    accepted_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='accepted')
    declined_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='declined')
    
    pending_reviewers = []
    accepted_reviewers = []
    declined_reviewers = []

    for paper_reviewer_pair in pending_paper_reviewer_pairs:
        pending_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in accepted_paper_reviewer_pairs:
        accepted_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in declined_paper_reviewer_pairs:
        declined_reviewers.append(paper_reviewer_pair.reviewer)

    context = {
        'formset': formset,
        'paper': paper,
        'papers': papers,
        'display_add_reviewer_modal': display_add_reviewer_modal,

        'pending_reviewers': pending_reviewers,
        'accepted_reviewers': accepted_reviewers,
        'declined_reviewers': declined_reviewers
    }
    return render(request, 'conference/view_papers.html', context)


def reviewer_info(request, paper_id, reviewer_id):
    paper = Paper.objects.get(id=paper_id)
    papers = Paper.objects.all().order_by('created_at')
    display_reviewer_info_modal = True
    reviewer = Reviewer.objects.get(id=reviewer_id)

    try:
        review = Review.objects.get(paper=paper, reviewer=reviewer)
    except:
        review = None    

    #####
    pending_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='pending')
    accepted_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='accepted')
    declined_paper_reviewer_pairs = Paper_Reviewer.objects.filter(paper__in=papers, status='declined')
    
    pending_reviewers = []
    accepted_reviewers = []
    declined_reviewers = []

    for paper_reviewer_pair in pending_paper_reviewer_pairs:
        pending_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in accepted_paper_reviewer_pairs:
        accepted_reviewers.append(paper_reviewer_pair.reviewer)

    for paper_reviewer_pair in declined_paper_reviewer_pairs:
        declined_reviewers.append(paper_reviewer_pair.reviewer)

    context = {
        "papers": papers,
        "display_reviewer_info_modal": display_reviewer_info_modal,
        "reviewer": reviewer,
        "review": review,

        'pending_reviewers': pending_reviewers,
        'accepted_reviewers': accepted_reviewers,
        'declined_reviewers': declined_reviewers
    } 
    return render(request, 'conference/view_papers.html', context)


def delete_reviewer(request, paper_id, reviewer_id):
    paper = Paper.objects.get(id=paper_id)
    paper.reviewers.remove(reviewer_id)

    reviewer = Reviewer.objects.get(id=reviewer_id)
    papers = Paper.objects.all()

    flag = 0
    for paper in papers:
        if reviewer in paper.reviewers.all():
            flag = 1

    if flag == 0:
        reviewer.delete()

    return redirect('view_papers')    



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
    associate_editor_role = Role.objects.get(name='Associate Editor')
    
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


def awaiting_reviewer_selection(request):
    papers = Paper.objects.all()

    paginator = Paginator(papers, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'papers':papers,
        "page_obj": page_obj,
    }
    return render(request, 'conference/awaiting_rev_selection.html', context)


def awaiting_reviewer_invitation():
    pass

def awaiting_reviewer_assignment():
    pass
