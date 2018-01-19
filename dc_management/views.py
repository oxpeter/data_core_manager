import os
import re
from datetime import date
import time

from dal import autocomplete

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail

from django.urls import reverse_lazy, reverse

from django.http import HttpResponse, Http404, FileResponse

from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404

from django.db.models import Q, Max, Sum

from dc_management.authhelper import get_signin_url, get_token_from_code, get_access_token
from dc_management.outlookservice import get_me, send_message

from .models import Server, Project, DC_User, Access_Log, Governance_Doc
from .models import Software, Software_Log, Storage_Log
from .models import UserCost, SoftwareCost, StorageCost, DCUAGenerator

from .forms import AddUserToProjectForm, RemoveUserFromProjectForm
from .forms import ExportFileForm, CreateDCAgreementURLForm
from .forms import AddSoftwareToProjectForm, ProjectForm, ProjectUpdateForm
from .forms import StorageChangeForm

#################################
#### Basic information views ####
#################################



####################################
######  AUTOCOMPLETE  VIEWS   ######
####################################

class DCUserAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = DC_User.objects.all()

        if self.q:
            qs = qs.filter(
                            Q(cwid__istartswith=self.q) | 
                            Q(first_name__istartswith=self.q) |
                            Q(last_name__istartswith=self.q)
                            )
            #qs = qs.filter(cwid__istartswith=self.q)

        return qs

class ProjectAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Project.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(dc_prj_id__icontains=self.q) | 
                            Q(nickname__icontains=self.q) 
                            )
        return qs

class SoftwareAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Software.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(name__icontains=self.q) | 
                            Q(vendor__icontains=self.q) |
                            Q(version__icontains=self.q)
                            )
        return qs

class NodeAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Server.objects.all()

        if self.q:
            qs =  qs.filter(
                            Q(node__icontains=self.q) | 
                            Q(ip_address__icontains=self.q) |
                            Q(comments__icontains=self.q)
                            )
        return qs

#######################
#### Outlook views ####
#######################

class ResetOutlookTokens(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_reset.html'
    def get_context_url(self, **kwargs):
        self.request.session['outlook_access_token'] = ""
        self.request.session['outlook_user_email'] = ""
        self.request.session['outlook_token_expires'] = ""
        self.request.session['outlook_refresh_token'] = ""
        context = super(ResetOutlookTokens, self).get_context_data(**kwargs)
        context.update({'reset':"TRUE"})
        return context
        
class OutlookConnection(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_outlook.html'
    
    
    def get_context_data(self, **kwargs):
        redirect_uri = self.request.build_absolute_uri(reverse('dc_management:gettoken'))
        sign_in_url = get_signin_url(redirect_uri)
                
        context = super(OutlookConnection, self).get_context_data(**kwargs)
        context.update({'sign_in_url': sign_in_url,
                        'redirect_uri': redirect_uri,
        })
        return context

class GetToken(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_token.html'
    def get_context_data(self, **kwargs):
        auth_code = self.request.GET['code']
        redirect_uri = self.request.build_absolute_uri(reverse('dc_management:gettoken'))
        token = get_token_from_code(auth_code, redirect_uri)
        access_token = token['access_token']
        user = get_me(access_token)
        
        # get token refresh details
        refresh_token = token['refresh_token']
        expires_in = token['expires_in']

        # expires_in is in seconds
        # Get current timestamp (seconds since Unix Epoch) and
        # add expires_in to get expiration time
        # Subtract 5 minutes to allow for clock differences
        expiration = int(time.time()) + expires_in - 300


        # Save the token in the session
        self.request.session['outlook_access_token'] = access_token
        self.request.session['outlook_user_email'] = user['mail']
        self.request.session['outlook_token_expires'] = expiration
        self.request.session['outlook_refresh_token'] = refresh_token

        context = super(GetToken, self).get_context_data(**kwargs)
        context.update({'gettoken': "Get Token",
                        'auth_code': auth_code,
                        'user': user,
                        'email': user['mail'],
        })
        return context

class SendMail(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_result.html'
    def get_context_data(self, **kwargs):
        access_token = get_access_token(
                            self.request,
                            self.request.build_absolute_uri(
                                        reverse('dc_management:gettoken'))
                                        )
        user_email = self.request.session['outlook_user_email']
        payload = {
                  "Message": {
                    "Subject": self.request.session['email_sbj'],
                    "Body": {
                      "ContentType": "Text",
                      "Content": self.request.session['email_msg']
                    },
                    "ToRecipients": [
                      {
                        "EmailAddress": {
                          "Address": "oxpeter@gmail.com"
                        }
                      }
                    ],
                    #"Attachments": [
                    #  {
                    #    "@odata.type": "#Microsoft.OutlookServices.FileAttachment",
                    #    "Name": "menu.txt",
                    #    "ContentBytes": "bWFjIGFuZCBjaGVlc2UgdG9kYXk="
                    #  }
                    #]
                  },
                  "SaveToSentItems": "true"
                  }

        context = super(SendMail, self).get_context_data(**kwargs)
        context.update({'gettoken': access_token,
                        'sendtest': send_message(access_token,user_email,payload),
        })
        return context

#######################
#### Basic views ####
#######################
 
class IndexView(LoginRequiredMixin, generic.ListView):
    login_url='/login/'
    
    template_name = 'dc_management/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.filter(status="RU").order_by('dc_prj_id')
    
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
    def get_context_data(self, **kwargs):
        server_users =  DC_User.objects.filter(project__host=self.kwargs['pk']
                        ).order_by('first_name')
        
        context = super(ServerView, self).get_context_data(**kwargs)
        context.update({'server_users': server_users,
        })
        return context
    
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

#############################
######  PROJECT VIEWS  ######
#############################

class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    
    #success_url = reverse_lazy("dc_management:index" )
    # default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(ProjectCreate, self).form_valid(form)

class ProjectUpdate(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    #success_url = reverse_lazy("dc_management:index" )
    #default success_url should be to the object page defined in model.
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(ProjectUpdate, self).form_valid(form)

class StorageChange(LoginRequiredMixin, CreateView):
    model = Storage_Log
    template_name = 'dc_management/storage_change_form.html'
    form_class = StorageChangeForm
        
    """
    # keeping this in case I need it somewhere else later
    # pass the project pk from the url to the form's kwargs for queryset populating
    def get_form_kwargs(self):
        kwargs = super(StorageChange, self).get_form_kwargs()
        kwargs.update({'ppk': self.kwargs['ppk']})  
    return kwargs
    """
    
    def get_initial(self):
        initial = super(StorageChange, self).get_initial()
        # get the project from the url
        chosen_project = Project.objects.get(pk=self.kwargs['ppk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST 
        log = form.save(commit=False)
        
        log.record_author = self.request.user
        
        # update the project storage:
        project = log.project
        
        # match storage type to project (this needs to be more robust)
        s_type = log.storage_type.storage_type
        if re.search('direct', s_type.lower()):
            project.direct_attach_storage = log.storage_amount
        elif re.search('backup', s_type.lower()):
            project.backup_storage = log.storage_amount
        elif re.search('share', s_type.lower()):
            project.fileshare_storage = log.storage_amount
        else:
            pass # may want to add an error message here.
        
        project.save()
        log.save()
        ## TODO: 
        # send email requesting change:
        
        return super(StorageChange, self).form_valid(form)

###############################
######  UPDATE SOFTWARE  ######
###############################

class UpdateSoftware(LoginRequiredMixin, FormView):
    template_name = 'dc_management/updatesoftwareform.html'
    form_class = AddSoftwareToProjectForm
    #success_url = reverse_lazy('dc_management:email_results')
    success_url = reverse_lazy('dc_management:sendtest')

    def email_change_project_software(self, changestr, prj, sw):
        """
        send request to add/remove software to node:
        """
        sbj_str = '{} software {} to {}'
        body_str = 'Please {} {} for project {} (node {}, {}).'
        sbj_msg  = sbj_str.format(changestr, sw, prj.dc_prj_id)
        body_msg = body_str.format(changestr,
                                     sw, 
                                     prj.dc_prj_id,
                                     prj.host.node,
                                     prj.host.ip_address,
                                    )
        """
        send_mail(
            sbj_msg,
            body_msg,
            'from@example.com',     # set reply_to address?
            ['oxpeter@gmail.com'],  # to field
            fail_silently=True,
        )
        """
        self.request.session['email_sbj'] = sbj_msg
        self.request.session['email_msg'] = body_msg
    
    def email_change_node_software(self, changestr, node, sw):
        """
        send request to add/remove software to node:
        """
        sbj_str = '{} software {} to {}'
        body_str = 'Please install {} on node {} ({}).'
        sbj_msg  = sbj_str.format(changestr, sw, node.node)
        body_msg = body_str.format(sw, 
                             node.node,
                             node.ip_address,
                            )
        """
        send_mail(
                sbj_msg,
                body_msg,
                'from@example.com',     # set reply_to address?
                ['oxpeter@gmail.com'],  # to field
                fail_silently=True,
        )
        """
        self.request.session['email_sbj'] = sbj_msg
        self.request.session['email_msg'] = body_msg

    def form_valid(self, form):
        self.request.session['email_sbj'] = "n/a"
        self.request.session['email_msg'] = "n/a"
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        
        # Check if user in project, then connect user to project
        sw = form.cleaned_data['software_changed']
        prj = form.cleaned_data['applied_to_prj']
        user = form.cleaned_data['applied_to_user']
        node = form.cleaned_data['applied_to_node']
        change = form.cleaned_data['change_type']
        
        form.instance.record_author = self.request.user
        
        if change == "AA":
            changestr = "install" # set language for emails:
            
            # if project specified, and not already installed:
            if prj and prj.host and not sw in prj.software_installed.all():
                # add sw to prj
                prj.software_installed.add(sw)
                prj.software_requested.add(sw)

                self.email_change_project_software(changestr, prj, sw)
            
            
                # add to node if not already:
                qs = Software_Log.objects.all()
                qs_node = qs.filter(Q(applied_to_node=prj.host) &
                             Q(software_changed=sw)
                             ).order_by('-change_date')
                
                if len(qs_node) == 0:  
                    node = prj.host
                    form.instance.applied_to_node = node
                elif qs_node[0].change_type == "RA":
                    # this is same as above, but put as elif statement to prevent
                    # breakage for null sets looking for [-1]
                    node = prj.host
                    form.instance.applied_to_node = node
                    
                    
            # if node specified (and not a project), and not already on node:
            if node and not prj:
                qs = Software_Log.objects.all()
                qs_node = qs.filter(Q(applied_to_node=node) &
                                    Q(software_changed=sw)
                                    ).order_by('-change_date')
                if len(qs_node) == 0:                    
                    self.email_change_node_software(changestr, node, sw)
                elif qs_node[0].change_type == "RA":
                    self.email_change_node_software(changestr, node, sw)
        
        elif change == "RA":
            changestr = "uninstall" # set language for emails:
            # if project specified, and not already uninstalled:
            if prj and prj.host and sw in prj.software_installed.all():
                # remove sw to prj
                prj.software_installed.remove(sw)
                prj.software_requested.remove(sw)

                self.email_change_project_software(changestr, prj, sw)
            
                # remove from node if not already:
                qs = Software_Log.objects.all()
                qs_node = qs.filter(Q(applied_to_node=prj.host) &
                                        Q(software_changed=sw)
                                        ).order_by('-change_date')
                                        
                if qs_node and qs_node[0].change_type == "AA":  
                    node = prj.host
                    form.instance.applied_to_node = node
        
            # if node specified (and not a project), and sw still on node:
            if node and not prj:
                qs = Software_Log.objects.all()
                qs_node = qs.filter(Q(applied_to_node=node) &
                                    Q(software_changed=sw)
                                     ).order_by('-change_date')
                if qs_node[0].change_type == "AA":
                    self.email_change_node_software(changestr, node, sw)


        else:
            changestr = "confirm presence of" # innocuous, not intended to be used.
                
            
        form.save()                
                
        return super(UpdateSoftware, self).form_valid(form)    

class EmailResults(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dc_management/email_result.html'
    
#################################################
######  UPDATE USER - PROJECT RELATIONSHIP ######
#################################################

class AddUserToProject(LoginRequiredMixin, FormView):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        self.request.session['email_sbj'] = "n/a"
        self.request.session['email_msg'] = "n/a"
             
        # Check if user in project, then connect user to project
        
        prj = form.cleaned_data['project']
        newusers = form.cleaned_data['dcusers']
        email_comment = form.cleaned_data['email_comment']
        oldusers = prj.users.all()
        record_author = self.request.user
        
        userlist = []
        for newuser in newusers:
            if newuser in oldusers:
                # report user is already added to project
                pass
            else:
                prj.users.add(newuser)
                userlist.append(newuser)
                
                # save access log instance
                self.logger = Access_Log(
                            record_author=record_author,
                            date_changed=date.today(),
                            dc_user=newuser,
                            prj_affected=prj,
                            change_type="AA",
                )
                self.logger.save()
        
        # send email
        if prj.host:
            node = prj.host.node
            ip = prj.host.ip_address
        else:
            node = "not mounted"
            ip = ""
        subject_str = 'Add users to {}'
        body_str = '''Dear OPs, 
        
This ticket refers to SOP "HowTo: Add or remove a user to a Data Core project"
https://nexus.weill.cornell.edu/display/ops/HowTo%3A+Add+or+remove+a+user+to+a+Data+Core+project+group

For the following {4} users, please add them to the AD group for project {0} ({1}, {2}) and create their corresponding fileshare directory "WorkArea-<CWID>":

{3}

{6}

Kind regards,
{5}'''
        subj_msg = subject_str.format(str(prj))
        body_msg = body_str.format(prj.dc_prj_id,
                            node,
                            ip,
                            '\n'.join([str(u) for u in userlist]),
                            len(userlist),
                            self.request.user,
                            email_comment,
                            )
        
        self.request.session['email_sbj'] = subj_msg
        self.request.session['email_msg'] = body_msg
        
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
        # update initial field defaults with custom set default values:
        initial.update({'dcuser': chosen_user, })
        return initial

class AddUserToThisProject(AddUserToProject):
    template_name = 'dc_management/addusertoproject.html'
    form_class = AddUserToProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def get_initial(self):
        initial = super(AddUserToThisProject, self).get_initial()
        # get the user from the url
        chosen_project = Project.objects.get(pk=self.kwargs['pk'])
        # update initial field defaults with custom set default values:
        initial.update({'project': chosen_project, })
        return initial

######### Removing users from projects ###########

class RemoveUserFromProject(LoginRequiredMixin, FormView ):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST
        self.request.session['email_sbj'] = "n/a"
        self.request.session['email_msg'] = "n/a"
                
        # Check if user in project, then connect user to project
        prj = form.cleaned_data['project']
        newusers = form.cleaned_data['dcusers']
        oldusers = prj.users.all()
        record_author = self.request.user
        email_comment = form.cleaned_data['email_comment']
        
        userlist = []
        for newuser in newusers:
            if newuser not in oldusers:
                # report user is not in project
                pass
            else:
                prj.users.remove(newuser)
                userlist.append(newuser)
                
                # save access log instance
                self.logger = Access_Log(
                            record_author=record_author,
                            date_changed=date.today(),
                            dc_user=newuser,
                            prj_affected=prj,
                            change_type="RA",
                )
                self.logger.save()

        # send email
        if prj.host:
            node = prj.host.node
            ip = prj.host.ip_address
        else:
            node = "not mounted"
            ip = ""

        subject_str = 'Remove users from {}'
        body_str = '''Dear OPs, 
        
This ticket refers to SOP "HowTo: Add or remove a user to a Data Core project"
https://nexus.weill.cornell.edu/display/ops/HowTo%3A+Add+or+remove+a+user+to+a+Data+Core+project+group

Please remove the following users from project {0} ({1}, {2}):

{3}

{5}

Kind regards,
{4}'''
        subj_msg = subject_str.format(str(prj))
        body_msg = body_str.format(prj.dc_prj_id,
                            node,
                            ip,
                            '\n'.join([str(u) for u in userlist]),
                            self.request.user,
                            email_comment,
                            )
        

        self.request.session['email_sbj'] = subj_msg
        self.request.session['email_msg'] = body_msg

        return super(RemoveUserFromProject, self).form_valid(form)

class RemoveUserFromThisProject(RemoveUserFromProject):
    template_name = 'dc_management/removeuserfromproject.html'
    form_class = RemoveUserFromProjectForm
    success_url = reverse_lazy('dc_management:sendtest')
    
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

class CreateDCAgreementURL(LoginRequiredMixin, CreateView):
    model = DCUAGenerator
    template_name = 'dc_management/dcua_url_generator_form.html'
    form_class = CreateDCAgreementURLForm
    #success_url = reverse_lazy('dc_management/dcua_url_generator_result.html')
    #success_url = reverse_lazy('dc_management:url_result')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        post_data = self.request.POST 
        link_object = form.save(commit=False)
        
        
        # create the personalized URL:
        ticket = form.cleaned_data['ticket']
        startdate = form.cleaned_data['startdate']
        enddate = form.cleaned_data['enddate']
        
        # create a string of folders:
        folders = ""
        folderlist = []
        for f in range(1,7,1):
            folder = "".join(["folder",str(f)])
            foldername = form.cleaned_data[ folder ]
            if foldername and foldername != "":
                folders += "&{}={}".format(folder, foldername)
                folderlist.append(foldername)
        
        # create the qualtrics link with embedded data:
        qualtrics_link = "https://weillcornell.az1.qualtrics.com/jfe/form/SV_eL1OCCGkNZWnX93"
        
        qualtrics_link += "?startdate={}&enddate={}".format(startdate,enddate)
        qualtrics_link += "{}".format(folders)
        if re.search("INC\d{6,8}", ticket):
            qualtrics_link += "&ticket={}".format(ticket)
        
        # add qualtrics link to model instance and save:
        link_object.url = qualtrics_link
        link_object.save()
        
        return super(CreateDCAgreementURL, self).form_valid(form)

    # the following has been deprecated. Being maintained during bug testing.
    def form_valid_old(self, form):
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

class ViewDCAgreementURL(LoginRequiredMixin, generic.DetailView):
    template_name = 'dc_management/dcua_url_generator_result.html'
    model = DCUAGenerator

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
        try:
            # open(gov_doc.documentation.file, 'rb')
            return FileResponse(gov_doc.documentation.file, 
                                content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()
    elif gov_doc.documentation.name[-4:] == "docx":
        try:
            with open(str(gov_doc.documentation.file), 'rb') as fh:
                response = HttpResponse(fh.read(),
                                        content_type="application/vnd.ms-word")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(str(gov_doc.documentation.file))
                return response
            
        except FileNotFoundError:
            raise Http404()
    else:
        raise Http404()


###############################
######  FINANCE  VIEWS   ######
###############################

class ActiveProjectFinances(LoginRequiredMixin, generic.ListView):
    template_name = 'dc_management/finances_global.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """Return  all active projects."""
        return Project.objects.all().order_by('dc_prj_id')
    
    def get_context_data(self, **kwargs):
        all_prjs = Project.objects.all().order_by('dc_prj_id')
        user_costs = UserCost.objects.all()
        sw_costs = SoftwareCost.objects.all()
        storage_costs = StorageCost.objects.all()
        
        # lists for passing to template:
        sw_list = []
        compute_list = []
        
        for prj in all_prjs:
            # Fileshare and replication
            try:
                fs_rate = storage_costs.get(
                                storage_type__icontains="share"
                                            ).st_cost_per_gb
            except ObjectDoesNotExist:
                fs_rate = 0          
            if prj.fileshare_storage:
                fss = prj.fileshare_storage
            else:
                fss = 0
            prj.fileshare_cost = fss * fs_rate

            # backup
            try:
                bkp_rate = storage_costs.get(
                                storage_type__icontains="backup"
                                            ).st_cost_per_gb
            except ObjectDoesNotExist:
                bkp_rate = 0          
        
            if prj.backup_storage:
                bs = prj.backup_storage
            else:
                bs = 0
            prj.backup_cost = bs * bkp_rate
            
            # completed projects only have storage costs:
            if prj.status == 'CO':
                prj.direct_attach_cost = 0
                prj.user_cost = 0
                prj.software_cost = 0
                prj.db_cost = 0
                prj.host_cost = 0
                sw_list.append([]) # to keep the sw list in sync
                compute_list.append(((0, 'CPUs', 0.0), (0, 'GB RAM', 0.0)))
            else:
                # get cost for users.
                user_num = len(prj.users.all())
                try:
                    ucost = user_costs.get(user_quantity=user_num).user_cost
                except ObjectDoesNotExist:
                    #maxquant = user_costs.aggregate(Max('user_quantity'))
                    max_rego = user_costs.order_by('-user_quantity')[0]
                    set_cost = max_rego.user_cost
                    set_cnt = max_rego.user_quantity
                    try:
                        xtr_cost = user_costs.get(user_quantity=0).user_cost    
                    except ObjectDoesNotExist:
                        xtr_cost = 0
                    
                    ucost = set_cost + xtr_cost * set_cnt
                
                prj.user_cost = ucost
            
                    
                # get cost for storage
                # direct attach
                try:
                    direct_rate = storage_costs.get(
                                    storage_type__icontains="direct"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    direct_rate = 0          
            
                if not prj.direct_attach_storage:
                    das = 0
                else:
                    das = prj.direct_attach_storage
                prj.direct_attach_cost = das * direct_rate
            
                
            
                # get costs for software:
                prj_sw_list = []
                prj_sw_total = 0
                for sw in prj.software_installed.all():
                    try:
                        sw_cost = sw_costs.get(software=sw).software_cost
                    except ObjectDoesNotExist:
                        sw_cost = 0
                    prj_sw_list.append((sw.name, sw_cost * user_num))
                    prj_sw_total += sw_cost * user_num
                prj.software_cost = prj_sw_total
                sw_list.append(prj_sw_list)
            
            
                # db cost
                try:
                    db_rate = storage_costs.get(
                                    storage_type__icontains="db"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    db_rate = 0          
            
                if prj.db:
                    db_size = prj.db.processor_num / 2
                else:
                    db_size = 0
                            
                prj.db_cost = db_size * db_rate

                # server cost
                try:
                    server_CPU_rate = storage_costs.get(
                                    storage_type__icontains="CPU"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    server_CPU_rate = 0
                try:
                    server_RAM_rate = storage_costs.get(
                                    storage_type__icontains="RAM"
                                                ).st_cost_per_gb
                except ObjectDoesNotExist:
                    server_RAM_rate = 0          
            
                if prj.host and prj.requested_cpu:
                    xtra_cpu = prj.requested_cpu - 4
                    if xtra_cpu < 0:
                        xtra_cpu = 0
                else:
                    xtra_cpu = 0
                if prj.host and prj.requested_ram:
                    xtra_ram = prj.requested_ram - 16
                    if xtra_ram < 0:
                        xtra_ram = 0
                    total_xtra_ram = xtra_ram
                    xtra_ram = xtra_ram - xtra_cpu * 4 
                else: 
                    xtra_ram = 0
                    total_xtra_ram = 0
                prj.host_cost = (   xtra_cpu / 2 * 
                                    server_CPU_rate + 
                                    xtra_ram / 8 * 
                                    server_RAM_rate
                                )
                compute_list.append(((  xtra_cpu, 
                                        "CPUs", 
                                        xtra_cpu / 2 * server_CPU_rate
                                        ),
                                    (total_xtra_ram, 
                                    "GB RAM", 
                                    xtra_ram / 8 * server_RAM_rate),
                                    )
                )
                
            # update total cost:
            prj.project_total_cost = (  prj.backup_cost + 
                                         prj.fileshare_cost +
                                         prj.direct_attach_cost +
                                         prj.user_cost +
                                         prj.software_cost +
                                         prj.db_cost +
                                         prj.host_cost
            )
            
            #### SAVE ####
            
            prj.save()
           
        prj_data = list(zip(all_prjs, sw_list, compute_list))
        grand_total = list(Project.objects.all().aggregate(
                                            Sum('project_total_cost')
                        ).values())[0]   
        context = super(ActiveProjectFinances, self).get_context_data(**kwargs)
        context.update({
            'prj_data': prj_data,
            'grand_total_cost': grand_total,
        })
        return context


