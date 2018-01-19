from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from . import views

app_name = 'dc_management'
urlpatterns = [
    # index showing all running projects:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # autocomplete functions:
    url(r'autocomplete-user/$', 
        views.DCUserAutocomplete.as_view(), 
        name='autocomplete-user',
        ),
    url(r'autocomplete-project/$', 
        views.ProjectAutocomplete.as_view(),
        name='autocomplete-project',
        ),
    url(r'autocomplete-node/$', 
        views.NodeAutocomplete.as_view(),
        name='autocomplete-node',
        ),

    url(r'autocomplete-software/$', 
        views.SoftwareAutocomplete.as_view(),
        name='autocomplete-software',
        ),
    # outlook email:
    url(r'outlook/$', views.OutlookConnection.as_view(), name='outlook'),
    url(r'outlook/gettoken/$', views.GetToken.as_view(), name='gettoken'),
    url(r'outlook/sendtest/$', views.SendMail.as_view(), name='sendtest'),
    url(r'outlook/reset/$', views.ResetOutlookTokens.as_view(), name='reset-outlook'),
    
    # index showing all users:
    url(r'^dcuser/all/$', views.AllDCUserView.as_view(), name='all_users'),
    url(r'^project/all/$', views.AllProjectsView.as_view(), name='all_projects'),
    
    # detail views of projects, nodes and users:
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectView.as_view(), name='project'),
    url(r'^node/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='node'),
    url(r'^dcuser/(?P<pk>[0-9]+)/$', views.DCUserView.as_view(), name='dcuser'),
    url(r'^govdoc/(?P<pk>[0-9]+)/$', views.pdf_view, name='govdoc'),
    # add, modify, remove user
    url(r'^dcuser/add/$', views.DC_UserCreate.as_view(), name='dc_user-add'),
    url(r'^dcuser/update/(?P<pk>[0-9]+)/$', 
        views.DC_UserUpdate.as_view(), 
        name='dc_user-update',
    ),
  
    # views related to onboarding:
    url(r'onboarding/dcua_generator/$', views.CreateDCAgreementURL.as_view(), 
        name='url_generator',
    ),
    path('onboarding/dcua_url/<int:pk>', views.ViewDCAgreementURL.as_view(), 
        name='url_result',
    ),
    path('project/add/', views.ProjectCreate.as_view(), name='project-add'),
    path('project/update/<int:pk>/', 
            views.ProjectUpdate.as_view(), 
            name='project-update'
    ),
    path('project/<int:ppk>/storage/change/',
            views.StorageChange.as_view(),
            name='storage-change'),
    
    # forms for adding user - project relationship:
    url(r'^dcuser/(?P<pk>[0-9]+)/connect$', 
        views.AddThisUserToProject.as_view(), 
        name='thisusertoproject-add',
    ),
    url(r'^dcuser/any/connect$', 
        views.AddUserToProject.as_view(), 
        name='usertoproject-add',
    ),
    
    # removing user - project relationship:
    url(r'^project/(?P<pk>[0-9]+)/userconnect$', 
        views.AddUserToThisProject.as_view(), 
        name='usertothisproject-add',
    ),
    url(r'^project/(?P<pk>[0-9]+)/userremove$', 
        views.RemoveUserFromThisProject.as_view(), 
        name='usertothisproject-remove',
    ),

    # software views:
    url(r'^software/$', views.UpdateSoftware.as_view(), name='change_software'),
    url(r'^software/email/$', 
        views.EmailResults.as_view(), 
        name='email_results'),
        
    # finance views:
    url(r'finances/$', views.ActiveProjectFinances.as_view(), name='finances-active'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


