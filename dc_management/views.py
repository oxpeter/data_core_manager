from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy, reverse

from django.http import HttpResponse
from django.http import Http404

from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404

from datetime import date

from .models import Server, Project, DC_User, Access_Log
from .forms import AddUserToProjectForm


class IndexView(generic.ListView):
    template_name = 'dc_management/index.html'
    context_object_name = 'running_projects_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.filter(status="RU").order_by('-dc_prj_id')
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'user_list': DC_User.objects.order_by('first_name'),
            'server_list': Server.objects.all(),
        })
        return context
        
class DCUserView(generic.ListView):
    template_name = 'dc_management/all_users.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        """Return  all active projects."""
        return DC_User.objects.all().order_by('first_name')
   

class ProjectView(generic.DetailView):
    model = Project
    template_name = 'dc_management/project.html'


class ServerView(generic.DetailView):
    model = Server
    template_name = 'dc_management/server.html'

   
class DCUserView(generic.DetailView):
    model = DC_User
    template_name = 'dc_management/dcuser.html'
    
class DC_UserCreate(CreateView):
    model = DC_User
    fields = ['first_name', 'last_name', 'cwid', 'affiliation', 'role', 'comments']
    success_url = reverse_lazy("dc_management:index" )
    def form_valid(self, form):
        self.object = form.save(commit=False)
        #self.object.user = self.request.user
        #self.object.post_date = datetime.now()
        self.object.save()
        return super(DC_UserCreate, self).form_valid(form)
            
class DC_UserUpdate(UpdateView):
    model = DC_User
    fields = ['first_name', 'last_name', 'cwid', 'affiliation', 'role', 'comments']  
    
class AddUserToProject(FormView):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = '/info/'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        post_data = self.request.POST
        
        # save access log instance
        self.logger = Access_Log(
                    date_changed=date.today(),
                    dc_user=form.cleaned_data['dcuser'],
                    prj_affected=form.cleaned_data['project'],
                    change_type="AA",
        )
        self.logger.save()
        
        # connect user to project
        prj = form.cleaned_data['project']
        prj.users.add(form.cleaned_data['dcuser'])
        prj.save()
        
        # send email
        print("Sending email")
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['oxpeter@gmail.com'],
            fail_silently=True,
        )
        return super(AddUserToProject, self).form_valid(form)