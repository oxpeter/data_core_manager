from django.conf.urls import url

from . import views

app_name = 'dc_management'
urlpatterns = [
    # index showing all running projects:
    url(r'^$', views.IndexView.as_view(), name='index'),
    # index showing all users:
    url(r'^dcuser/all/$', views.DCUserView.as_view(), name='all_users'),
    # detail views of projects, nodes and users:
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectView.as_view(), name='project'),
    url(r'^node/(?P<pk>[0-9]+)/$', views.ServerView.as_view(), name='node'),
    url(r'^dcuser/(?P<pk>[0-9]+)/$', views.DCUserView.as_view(), name='dcuser'),
    # forms for updating users:
    url(r'^dcuser/add/$', views.DC_UserCreate.as_view(), name='dc_user-add'),
    url(r'^dcuser/update/(?P<pk>[0-9]+)/$', 
        views.DC_UserUpdate.as_view(), 
        name='dc_user-update',
    ),
    url(r'^dcuser/(?P<pk>[0-9]+)/connect$', 
        views.AddUserToProject.as_view(), 
        name='usertoproject-add',
    )
    
]


