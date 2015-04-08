from django.conf.urls import patterns, url
from decision import views

from decision.views import Index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', Index.as_view(), name='index'),
    url(r'^decision/(?P<pk>\d+)/$', views.DecisionDetailView.as_view(), name='decision_detail'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^invite/add/(?P<decision_id>\d+)/(?P<user_id>\d+)$', views.inviteCreate, name='invite_create'),
    url(r'^invite/add/$', views.inviteCreate, name='invite_create'),
    url(r'^invite/accept/$', views.inviteAccept, name='invite_accept'),
    url(r'^invite/remove/$', views.inviteRemove, name='invite_remove'),
    url(r'^vote/edit/$', views.voteEdit, name='vote_edit'),
    url(r'^vote/add/$', views.voteAdd, name='vote_add'),
)
