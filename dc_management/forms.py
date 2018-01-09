import datetime

from dal import autocomplete

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Server, Project, DC_User, Software, Software_Log, Project

class CommentForm(forms.Form):
    name = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    topics = forms.ModelMultipleChoiceField(queryset=Project.objects.all())
    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
        
class AddUserToProjectForm(forms.Form):
    dcuser = forms.ModelChoiceField(
                                queryset=DC_User.objects.all(), 
                                label="Data Core User",
                                widget=autocomplete.ModelSelect2(
                                                    url='dc_management:autocomplete-user'
                                                                ),
                                )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Project",
                                widget=autocomplete.ModelSelect2(
                                                url='dc_management:autocomplete-project'
                                                                ),
                                )
    comment = forms.CharField(required=False, label="Comment",)
    class Meta:
        widgets =  {'dcuser' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        )
                    }
    
class RemoveUserFromProjectForm(forms.Form):
    dcuser = forms.ModelChoiceField(
                                queryset=DC_User.objects.none(), 
                                label="Data Core User"
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.all(), 
                                label="Project"
                                    )
    comment = forms.CharField(required=False, label="Comment")
    
    
    # the project_users list is now available, add it to the instance data
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('project_users')
        super(RemoveUserFromProjectForm, self).__init__(*args, **kwargs)
        self.fields['dcuser'].queryset = qs

class ExportFileForm(forms.Form):
    dcuser = forms.ModelChoiceField(
                                queryset=DC_User.objects.all(), 
                                label="Data Core User"
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Project"
                                    )
    internal_destination = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Internal transfer",
                                required=False,
                                    )
    files_requested = forms.CharField(required=False, label="Location of requested files")
    comment = forms.CharField(required=False, label="Comment")
    
    # the project_users list is now available, add it to the instance data
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('project_users')
        super(ExportFileForm, self).__init__(*args, **kwargs)
        self.fields['dcuser'].queryset = qs

class CreateDCAgreementURLForm(forms.Form):
    ticket = forms.CharField(required=False, 
                              label="SN Ticket",
                            )
    startdate = forms.CharField(required=True, 
                                label="Start Date", 
                                initial=datetime.datetime.now().strftime("%m/%d/%Y"),
                                )
    enddate = forms.CharField(required=True, 
                            label="End Date",
                            initial=(datetime.datetime.now() + 
                                     datetime.timedelta(days=365)
                                        ).strftime("%m/%d/%Y"),
                                )
    folder1 = forms.CharField(required=True, 
                              label="Folder 1",
                              initial="dcore-prj00XX-SOURCE",)
    folder2 = forms.CharField(required=False, 
                              label="Folder 2",
                              initial="dcore-prj00XX-SHARE",)
    folder3 = forms.CharField(required=False, 
                              label="Folder 3",
                              initial="WorkArea-<user CWID>",)
    folder4 = forms.CharField(required=False, label="Folder 4")
    folder5 = forms.CharField(required=False, label="Folder 5")
    folder6 = forms.CharField(required=False, label="Folder 6")
    folder7 = forms.CharField(required=False, label="Folder 7")

class ProjectForm(forms.ModelForm):
    
    class Meta:
        model = Project
        fields = [  'dc_prj_id',
                    'title', 
                    'nickname', 
                    'fileshare_storage', 
                    'direct_attach_storage', 
                    'backup_storage',
                    'requested_ram', 
                    'requested_cpu', 
                    'users',
                    'pi',
                    'software_requested',
                    'env_type',
                    'env_subtype',
                    'expected_completion',
                    'status',
                    'sn_tickets',
                    'predata_ticket',
                    'predata_date',
                    'postdata_ticket',
                    'postdata_date',
                    'completion_ticket',
                    'completion_date',
                    'host',
                    'db',
                    'comments',
                ]

        widgets =  {'users' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'pi' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                    'host' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'db' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'software_requested' : autocomplete.ModelSelect2Multiple(
                                        url='dc_management:autocomplete-software'
                                        ),
                                    
                    }
    
class AddSoftwareToProjectForm(forms.ModelForm):
    
    class Meta:
        model = Software_Log
        fields = [  'software_changed',
                    'applied_to_prj',
                    'applied_to_node',
                    'applied_to_user',
                    'change_type',
                ]
        labels = {
            'software_changed': _('Software'),
            'applied_to_prj': _('Project applied to'),
            'applied_to_node': _('Node applied to'),
            'applied_to_user': _('User applied to'),
            'change_type': _('Add or remove?'),            
        }
        help_texts = {
            'applied_to_node': _('Only select this if you are not applying directly to a project.'),
        }
        widgets =  {'software_changed' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-software'
                                        ),
                    'applied_to_prj' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-project'
                                        ),
                    'applied_to_node' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-node'
                                        ),
                    'applied_to_user' : autocomplete.ModelSelect2(
                                        url='dc_management:autocomplete-user'
                                        ),
                                    
                    }
    
    
