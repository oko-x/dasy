from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import generic

from decision.models import Decision, CustomUser, Invite, Vote, Criteria_Variant
from mysite.forms import DecisionForm, CriteriaVariantFormSet


@login_required
def inviteCreate(request, decision_id=None, user_id=None):
    if request.is_ajax():
        decision_id = request.POST['decision_id']
        user_id = request.POST['user_id']
        user_weight = request.POST['user_weight']
    if user_id == str(request.user.id):
        state = "AC"
    else:
        state = "SE"
    i = Invite(user=CustomUser.objects.get(pk=user_id),
               weight=user_weight,
               decision=Decision.objects.get(pk=decision_id),
               state=state)
    i.save()
    if request.is_ajax():
        return HttpResponse("Invite sent")
    else:
        return HttpResponseRedirect(reverse('decision_detail', args=[decision_id]))
    
@login_required
def inviteAccept(request):
    inviteId = request.POST['inviteId']
    Invite.objects.get(pk=inviteId).acceptInvite()
    return HttpResponse("Invite accepted")
    
@login_required
def inviteRemove(request):
    inviteId = request.POST['inviteId']
    Invite.objects.get(pk=inviteId).delete()
    return HttpResponse("Invite declined")

@login_required
def voteEdit(request):
    voteId = request.POST['voteId']
    value = request.POST['value']
    vote = Vote.objects.get(pk=voteId)
    vote.value = value
    vote.save()
    decision = vote.decision
    decision.voteChange = True
    decision.save()
    return HttpResponse("Vote updated")

@login_required
def voteAdd(request):
    decisionId = request.POST['decisionId']
    criteriaLeftId = request.POST['criteriaLeftId']
    criteriaRightId = request.POST['criteriaRightId']
    criteriaParentId = request.POST['criteriaParentId']
    order = request.POST['order']
    value = request.POST['value']

    invite = Invite.objects.filter(decision__id=decisionId, user=request.user)
    weight = invite[0].weight
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
                    value=value,
                    userWeight=weight,
                    order=order,)
        vote.save()
    return HttpResponse("Vote saved")

class DecisionDetailView(generic.DetailView):
    model = Decision
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionDetailView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DecisionDetailView, self).get_context_data(**kwargs)
        context['weights'] = Invite.WEIGHT_CHOICES
        context['wasInvited'] = self.object.invite_set.filter(user=self.request.user, state="AC")
        return context
    
class DecisionCreateView(generic.CreateView):
    model = Decision
    form_class = DecisionForm
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        crit_form = CriteriaVariantFormSet(prefix="criterias")
        var_form = CriteriaVariantFormSet(prefix="variants")
        return self.render_to_response(
            self.get_context_data(form=form,
                                  crit_form=crit_form,
                                  var_form=var_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        crit_form = CriteriaVariantFormSet(self.request.POST, self.request.FILES, prefix="criterias")
        var_form = CriteriaVariantFormSet(self.request.POST, self.request.FILES, prefix="variants")
        if (form.is_valid() and crit_form.is_valid() and var_form.is_valid()):
            return self.form_valid(form, crit_form, var_form, request)
        else:
            return self.form_invalid(form, crit_form, var_form)

    def form_valid(self, form, crit_form, var_form, request):
        """
        Called if all forms are valid. and then redirects to a
        success page.
        """
        self.object = form.save(commit=False)
        self.object.creator = request.user
        self.object.save()
        crit_form.instance = self.object
        crit_form.save()
        var_form.instance = self.object
        for variant_form in var_form:
            cd = variant_form.cleaned_data
            if 'name' in cd:
                name = cd.get('name')
                description = cd.get('description')
                image = cd.get('image')
                crit_var = True
                decision = self.object
                variant = Criteria_Variant(name = name,
                                           description = description,
                                           image = image,
                                           crit_var = crit_var,
                                           decision = decision,)
                variant.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, crit_form, var_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  crit_form=crit_form,
                                  var_form=var_form))
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionCreateView, self).dispatch(*args, **kwargs)

class UserDetailView(generic.DetailView):
    model = CustomUser
    
    def get(self, request, *args, **kwargs):
        invites = self.get_object().getInvites()
        for i in invites:
            if i.state == "SE":
                i.setSeen()
        return generic.DetailView.get(self, request, *args, **kwargs)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserDetailView, self).dispatch(*args, **kwargs)
 
class DecisionEvaluateView(generic.TemplateView):
    template_name = "decision_eval.html"
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionEvaluateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DecisionEvaluateView, self).get_context_data(**kwargs)
        context['object'] = self.request.user
        context['choices'] = Vote.VOTE_CHOICES
        decision = Decision.objects.get(pk=kwargs['pk'])
        context['decision'] = decision
        context['votes'] = decision.vote_set.filter(user=self.request.user).select_related('critVarLeft', 'critVarRight', 'parentCrit').order_by('order')
        return context

class Index(generic.TemplateView):
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['object'] = self.request.user
        context['choices'] = Vote.VOTE_CHOICES
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)
    