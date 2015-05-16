from django.conf.urls import patterns, url, include

from decision import views
from decision.views import Index


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', Index.as_view(), name='dashboard'),
    url(r'^decision/(?P<pk>\d+)/$', views.DecisionDetailView.as_view(), name='decision_detail'),
    url(r'^decision/(?P<pk>\d+)/users/(?P<invite_id>\d+)$', views.DecisionUsersDetailView.as_view(), name='decision_detail_users'),
    url(r'^decision/(?P<pk>\d+)/info/(?P<invite_id>\d+)$', views.DecisionDashboardInfo.as_view(), name='decision_dashboard_info'),
    url(r'^decision/create/$', views.DecisionCreateView.as_view(), name='decision_create'),
    url(r'^decision/eval/(?P<pk>\d+)/$', views.DecisionEvaluateView.as_view(), name='decision_evaluate'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^invite/add/(?P<decision_id>\d+)/(?P<user_id>\d+)$', views.inviteCreate, name='invite_create'),
    url(r'^invite/add/$', views.inviteCreate, name='invite_create'),
    url(r'^invite/accept/$', views.inviteAccept, name='invite_accept'),
    url(r'^invite/remove/$', views.inviteRemove, name='invite_remove'),
    url(r'^vote/edit/$', views.voteEdit, name='vote_edit'),
    url(r'^vote/add/$', views.voteAdd, name='vote_add'),
    url(r'^registration/$', views.UserCreateView.as_view(), name='user_add'),
    url('^', include('django.contrib.auth.urls'))
)
