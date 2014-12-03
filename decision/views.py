from django.views.generic import View
from django.http import HttpResponse
from django.views import generic
from decision.models import Decision, CustomUser, Invite
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse

def inviteCreate(request, decision_id=None, user_id=None):
    if request.is_ajax():
        print request
        decision_id = request.POST['decision_id']
        user_id = request.POST['user_id']
    i = Invite(user=CustomUser.objects.get(pk=user_id), decision=Decision.objects.get(pk=decision_id), state="SE")
    i.save()
    if request.is_ajax():
        return HttpResponse("Invite sent")
    else:
        return HttpResponseRedirect(reverse('decision_detail', args=[decision_id]))

class DecisionDetailView(generic.DetailView):
    model = Decision

class UserDetailView(generic.DetailView):
    model = CustomUser

class Index(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('django 1.7 on Openshift')