from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'dc_management'
urlpatterns = [
    # index showing all running projects:
    url(r'^$', views.IndexView.as_view(), name='index'),
    
    # index showing all users:
    url(r'^dcuser/all/$', views.AllDCUserView.as_view(), name='all_users'),
    url(r'^project/all/$', views.AllProjectsView.as_view(), name='all_projects'),
    
    # detail views of projects, nodes and users:
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectView.as_view(), name='project'),
    url(r'^node/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='node'),
    url(r'^dcuser/(?P<pk>[0-9]+)/$', views.DCUserView.as_view(), name='dcuser'),
    url(r'^govdoc/(?P<pk>[0-9]+)/$', views.pdf_view, name='govdoc'),
    # forms for updating users:
    url(r'^dcuser/add/$', views.DC_UserCreate.as_view(), name='dc_user-add'),
    url(r'^dcuser/update/(?P<pk>[0-9]+)/$', 
        views.DC_UserUpdate.as_view(), 
        name='dc_user-update',
    ),
    url(r'^dcuser/(?P<pk>[0-9]+)/connect$', 
        views.AddThisUserToProject.as_view(), 
        name='thisusertoproject-add',
    ),
    url(r'^dcuser/any/connect$', 
        views.AddUserToProject.as_view(), 
        name='usertoproject-add',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


