from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.views import generic

from decision.models import Decision, CustomUser, Invite, Vote, Criteria_Variant


def inviteCreate(request, decision_id=None, user_id=None):
    if request.is_ajax():
        decision_id = request.POST['decision_id']
        user_id = request.POST['user_id']
    i = Invite(user=CustomUser.objects.get(pk=user_id), decision=Decision.objects.get(pk=decision_id), state="SE")
    i.save()
    if request.is_ajax():
        return HttpResponse("Invite sent")
    else:
        return HttpResponseRedirect(reverse('decision_detail', args=[decision_id]))
    
def inviteAccept(request):
    inviteId = request.POST['inviteId']
    Invite.objects.get(pk=inviteId).acceptInvite()
    
def inviteRemove(request):
    inviteId = request.POST['inviteId']
    Invite.objects.get(pk=inviteId).delete()

def voteEdit(request):
    voteId = request.POST['voteId']
    value = request.POST['value']
    vote = Vote.objects.get(pk=voteId)
    vote.value = value
    vote.save()
    return HttpResponse("Vote updated")

def voteAdd(request):
    decisionId = request.POST['decisionId']
    criteriaLeftId = request.POST['criteriaLeftId']
    criteriaRightId = request.POST['criteriaRightId']
    criteriaParentId = request.POST['criteriaParentId']
    value = request.POST['value']
    if criteriaParentId != "":
        parentCrit = Criteria_Variant.objects.get(pk=criteriaParentId)
    else:
        parentCrit = None
    vote = Vote.objects.filter(user=request.user, 
                decision=Decision.objects.get(pk=decisionId),
                critVarLeft=Criteria_Variant.objects.get(pk=criteriaLeftId),
                critVarRight=Criteria_Variant.objects.get(pk=criteriaRightId),
                parentCrit = parentCrit,)
    if len(vote) > 0:
        vote[0].value = value
        vote[0].save()
    else:
        vote = Vote(user=request.user, 
                    decision=Decision.objects.get(pk=decisionId),
                    critVarLeft=Criteria_Variant.objects.get(pk=criteriaLeftId),
                    critVarRight=Criteria_Variant.objects.get(pk=criteriaRightId),
                    parentCrit = parentCrit,
                    value=value,)
        vote.save()
    return HttpResponse("Vote saved")

class DecisionDetailView(generic.DetailView):
    model = Decision

class UserDetailView(generic.DetailView):
    model = CustomUser
    def get(self, request, *args, **kwargs):
        invites = self.get_object().getInvites()
        for i in invites:
            if i.state == "SE":
                i.setSeen()
        return generic.DetailView.get(self, request, *args, **kwargs)
    
class Index(generic.TemplateView):
    template_name = "dashboard.html"
    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['object'] = self.request.user
        context['choices'] = Vote.VOTE_CHOICES
        return context