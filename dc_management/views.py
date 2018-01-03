import os
import re

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse

from django.http import HttpResponse, Http404, FileResponse

from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404

from datetime import date

from .models import Server, Project, DC_User, Access_Log, Governance_Doc

from .forms import AddUserToProjectForm, RemoveUserFromProjectForm
from .forms import ExportFileForm, CreateDCAgreementURLForm

class IndexView(LoginRequiredMixin, generic.ListView):
    login_url='/login/'
    
    template_name = 'dc_management/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.filter(status="RU").order_by('-dc_prj_id')
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'user_list': DC_User.objects.filter(
                                        project_pi__isnull=False,
                                        ).distinct().order_by('first_name'),
            'server_list': Server.objects.filter(
                                        status="ON"
                                        ).filter(
                                            function="PR"
                                        ).order_by('node'),
        })
        return context

class AllProjectsView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/all_projects.html'
    context_object_name = 'project_list'
    
    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.all().order_by('dc_prj_id')

class AllDCUserView(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/all_users.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        """Return  all active projects."""
        return DC_User.objects.all().order_by('first_name')
   
class ProjectView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'dc_management/project.html'

class ServerView(LoginRequiredMixin, generic.DetailView):
    model = Server
    template_name = 'dc_management/server.html'

class DCUserView(LoginRequiredMixin, generic.DetailView):
    model = DC_User
    template_name = 'dc_management/dcuser.html'

class DC_UserCreate(LoginRequiredMixin, CreateView):
    model = DC_User
    fields = ['first_name', 'last_name', 'cwid', 'affiliation', 'role', 'comments']
    success_url = reverse_lazy("dc_management:index" )
    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        #self.object.post_date = datetime.now()
        self.object.save()
        return super(DC_UserCreate, self).form_valid(form)

class DC_UserUpdate(LoginRequiredMixin, UpdateView):
    model = DC_User
    fields = ['first_name', 'last_name', 'cwid', 'affiliation', 'role', 'comments']  
    #success_url = reverse('dc_management:dcuser', pk=self.pk)


#################################################
######  UPDATE USER - PROJECT RELATIONSHIP ######
#################################################

class AddUserToProject(LoginRequiredMixin, FormView):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:all_projects')
    
    print("AddUserToProject invoked")
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        
        
        
        # Check if user in project, then connect user to project
        
        prj = form.cleaned_data['project']
        newuser = form.cleaned_data['dcuser']
        oldusers = prj.users.all()
        record_author = self.request.user
        
        if newuser in oldusers:
            # report user is already added to project
            pass
        else:
            prj.users.add(newuser)
            prj.save()
            
            # save access log instance
            self.logger = Access_Log(
                        record_author=record_author,
                        date_changed=date.today(),
                        dc_user=form.cleaned_data['dcuser'],
                        prj_affected=form.cleaned_data['project'],
                        change_type="AA",
            )
            self.logger.save()
        
            # send email
            send_mail(
                'Subject: add user {} to {}'.format(newuser, str(prj)),
                'Please add {} to project {} ({}) (name: {} IP:{}).'.format(newuser, 
                                                                     str(prj),
                                                                     prj.host,
                                                                     prj.host.node,
                                                                     prj.host.ip_address,
                                                                     ),
                'from@example.com',
                ['oxpeter@gmail.com'],
                fail_silently=True,
            )
        return super(AddUserToProject, self).form_valid(form)

class AddThisUserToProject(AddUserToProject):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:all_projects')
    #chosen_user = DC_User.objects.get(pk=self.kwargs['pk'])
    #success_url = reverse_lazy('dc_management:dcuser', self.kwargs['pk'])
    
    def get_initial(self):
        initial = super(AddThisUserToProject, self).get_initial()
        # get the user from the url
        chosen_user = DC_User.objects.get(pk=self.kwargs['pk'])
        print(chosen_user)
        # update initial field defaults with custom set default values:
        initial.update({'dcuser': chosen_user, })
        return initial

class AddUserToThisProject(AddUserToProject):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:all_projects')
    #chosen_project = Project.objects.get(pk=self.kwargs['pk'])
    #success_url = reverse_lazy('dc_management:project', self.kwargs['pk'])
    
    def get_initial(self):
        initial = super(AddUserToThisProject, self).get_initial()
        # get the user from the url
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        print(chosen_project)
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

######### Removing users from projects ###########

class RemoveUserFromProject(LoginRequiredMixin, FormView):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = 'dc_management:all_projects'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        post_data = self.request.POST
        
        
        
        
        # Check if user in project, then connect user to project
        prj = form.cleaned_data['project']
        newuser = form.cleaned_data['dcuser']
        oldusers = prj.users.all()
        record_author = self.request.user
        
        if newuser not in oldusers:
            # report user is not in project
            pass
        else:
            prj.users.remove(newuser)
            prj.save()

            # save access log instance
            self.logger = Access_Log(
                        record_author=record_author,
                        date_changed=date.today(),
                        dc_user=form.cleaned_data['dcuser'],
                        prj_affected=form.cleaned_data['project'],
                        change_type="RA",
            )
            self.logger.save()

        
            # send email
            print("Sending email")
            send_mail(
                'Subject: remove user {} from {}'.format(newuser, str(prj)),
                'Please remove {} from project {} ({}) (name: {} IP:{}).'.format(newuser, 
                                                         str(prj),
                                                         prj.host,
                                                         prj.host.node,
                                                         prj.host.ip_address,
                                                         ),
                'from@example.com',
                ['oxpeter@gmail.com'],
                fail_silently=True,
            )
        return super(RemoveUserFromProject, self).form_valid(form)

class RemoveUserFromThisProject(RemoveUserFromProject):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = '/info/'

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(RemoveUserFromThisProject, self).get_form_kwargs()
        kwargs['project_users'] =   Project.objects.get(
                                                        pk=self.kwargs['pk']
                                    ).users.all()
        return kwargs

    def get_initial(self):
        initial = super(RemoveUserFromThisProject, self).get_initial()
        # get the user from the url
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

###### Onboarding views #######
class CreateDCAgreementURL(LoginRequiredMixin, FormView):
    template_name = 'dc_management/dcua_url_generator_form.html'
    form_class = CreateDCAgreementURLForm
    #success_url = reverse_lazy('dc_management/dcua_url_generator_result.html')
    success_url = reverse_lazy('dc_management:url_result')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST 
        
        # create the personalized URL:
        ticket = form.cleaned_data['ticket']
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        
        folders = ""
        folderlist = []
        for f in range(1,7,1):
            folder = "".join(["folder",str(f)])
            foldername = form.cleaned_data[ folder ]
            if foldername != "":
                folders += "&{}={}".format(folder, foldername)
                folderlist.append(foldername)
        
        qualtrics_link = "https://weillcornell.az1.qualtrics.com/jfe/form/SV_eL1OCCGkNZWnX93"
        
        qualtrics_link += "?startdate={}&enddate={}".format(startdate,enddate)
        qualtrics_link += "{}".format(folders)
        if re.search("INC\d{6,8}", ticket):
            qualtrics_link += "&ticket={}".format(ticket)
            self.request.session['ticket'] = ticket
        else:
            self.request.session['ticket'] = ""
        
        # add to session info for passing to results page
        # NB - all session info fields must be updated, otherwise old info will be passed!
        self.request.session['qualtrics_link'] = qualtrics_link
        self.request.session['startdate'] = startdate
        self.request.session['enddate'] = enddate
        self.request.session['folders'] = folderlist

        return super(CreateDCAgreementURL, self).form_valid(form)

class ViewDCAgreementURL(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/dcua_url_generator_result.html'

###### Export requests #######
class ExportRequest(LoginRequiredMixin, FormView):
    template_name = 'dc_management/export_request_form.html'
    form_class = ExportFileForm
    success_url = reverse_lazy('dc_management:all_projects')
    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        
        
        
        # Check if user in project, then connect user to project
        
        prj = form.cleaned_data['project']
        requestor = form.cleaned_data['dcuser']
        files_requested = form.cleaned_data['files_requested']
        internal_destination = form.cleaned_data['internal_destination']
        record_author = self.request.user
        
        # if internal_destination supplied, request internal transfer
        # otherwise, use transfer.med to transfer to user directly.
        if internal_destination:
            pass
        else:
            pass
            
        # save access log instance
        self.logger = Access_Log(
                    record_author=record_author,
                    date_changed=date.today(),
                    dc_user=form.cleaned_data['dcuser'],
                    prj_affected=form.cleaned_data['project'],
                    change_type="AA",
        )
        self.logger.save()
        
        # send email
        send_mail(
            'Transfer files from {} to {}'.format(newuser, str(prj)),
            'Please add {} to project {} ({}) (name: {} IP:{}).'.format(newuser, 
                                                                 str(prj),
                                                                 prj.host,
                                                                 prj.host.node,
                                                                 prj.host.ip_address,
                                                                 ),
            'from@example.com',
            ['oxpeter@gmail.com'],
            fail_silently=True,
        )
        return super(AddUserToProject, self).form_valid(form)

class ExportFromThisProject(ExportRequest):
    template_name = 'dc_management/addusertoproject.html'
    form_class = ExportFileForm
    success_url = reverse_lazy('dc_management:all_projects')
    #chosen_user = DC_User.objects.get(pk=self.kwargs['pk'])
    #success_url = reverse_lazy('dc_management:dcuser', self.kwargs['pk'])
    
    def get_initial(self):
        initial = super(AddThisUserToProject, self).get_initial()
        # get the user from the url
        chosen_user = DC_User.objects.get(pk=self.kwargs['pk'])
        print(chosen_user)
        # update initial field defaults with custom set default values:
        initial.update({'dcuser': chosen_user, })
        return initial



        
########################################
######  GOVERNANCE RELATED VIEWS  ######
########################################


@login_required()
def pdf_view(request, pk):
    gov_doc = Governance_Doc.objects.get(pk=pk)
   
    if gov_doc.documentation.name[-3:] == "pdf":
        print("recognized PDF")
        print(gov_doc.documentation.file)
        try:
            # open(gov_doc.documentation.file, 'rb')
            return FileResponse(gov_doc.documentation.file, 
                                content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()
    elif gov_doc.documentation.name[-4:] == "docx":
        try:
            print(gov_doc.documentation.file)
            print(gov_doc.documentation.name)
            print(dir(gov_doc.documentation.file))
            with open(str(gov_doc.documentation.file), 'rb') as fh:
                response = HttpResponse(fh.read(),
                                        content_type="application/vnd.ms-word")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(str(gov_doc.documentation.file))
                return response
            
        except FileNotFoundError:
            raise Http404()
    else:
        raise Http404()
    