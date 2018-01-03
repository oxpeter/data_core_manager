import datetime

from django import forms

from .models import Server, Project, DC_User

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
                                label="Data Core User"
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
                                label="Project"
                                    )
    comment = forms.CharField(required=False, label="Comment")
    
    
class RemoveUserFromProjectForm(forms.Form):
    dcuser = forms.ModelChoiceField(
                                queryset=DC_User.objects.none(), 
                                label="Data Core User"
                                    )
    project = forms.ModelChoiceField(
                                queryset=Project.objects.exclude(status="CO"), 
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