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
    
    