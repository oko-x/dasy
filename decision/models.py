# -*- coding: utf-8 -*-

import re
from timeit import itertools

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields import CharField, BooleanField, DateField, IntegerField, \
    FloatField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.utils.timezone import now

from mysite.utils import calcCriteriaWeight, calcVariantsWeightRespectToCriteria, \
    calcCriteriasWeightRespectToVariant, nCr
import numpy as np


# Create your models here.
class CustomUser(AbstractUser):
    image = ImageField(null=True, blank=True, upload_to="pics/avatars")
    def getInvites(self):
        return self.invite_set.all()
    def getUnrespondedInvites(self):
        return self.invite_set.filter(state__in=["SE","SN"])
    def getDecisionsInvited(self):
        return self.invite_set.filter(state="AC").select_related('decision')
    def getDecisionsCreated(self):
        return self.decision_set.all()
    
class Invite(models.Model):
    SENT = 'SE'
    SEEN = 'SN'
    ACCEPTED = 'AC'
    DECLINED = 'DC'
    STATE_CHOICES = (
        (SENT, u'Poslaná'),
        (SEEN, u'Prečítaná'),
        (ACCEPTED, u'Akceptovaná'),
        (DECLINED, u'Odmietnutá'),
    )
    ROOKIE = 2
    TRAINEE = 4
    EDUCATED = 6
    PROFFESIONAL = 8
    EXPERT = 10
    WEIGHT_CHOICES = (
        (ROOKIE, u'Začiatočník'),
        (TRAINEE, u'Učeň'),
        (EDUCATED, u'Vyučený'),
        (PROFFESIONAL, u'Profesionál'),
        (EXPERT, u'Expert'),
    )
    weight = IntegerField(choices=WEIGHT_CHOICES)
    user = ForeignKey(CustomUser)
    decision = ForeignKey('Decision')
    state = CharField(max_length=2, choices=STATE_CHOICES, default="SE")
    def acceptInvite(self):
        self.state = "AC"
        self.save()
    def setSeen(self):
        self.state = "SN"
        self.save()
    def __unicode__(self):
        return "_".join([self.decision.name,
                         self.user.username,
                         self.get_weight_display()])
    
class Decision(models.Model):
    LIMIT_MATRIX_DECIMAL_PRECISION = 0.000001
    NEW = 'NE'
    STAGE_ONE = 'SO'
    STAGE_TWO = 'ST'
    FINISHED = 'FI'
    STATE_CHOICES = (
        (NEW, u'Nové'),
        (STAGE_ONE, u'Prvá fáza'),
        (STAGE_TWO, u'Druhá fáza'),
        (FINISHED, u'Dokončené'),
    )
    name = CharField(max_length=200)
    description = CharField( max_length=200, blank=True)
    creator = ForeignKey(CustomUser)
    image = ImageField(null=True, blank=True, upload_to="pics/decision")
    state = CharField(max_length=2, choices=STATE_CHOICES, default="NE")
    published = DateField(default=now)
    stage_one_date = DateField(null=True, blank=True)
    stage_two_date = DateField(null=True, blank=True)
    lastVotesCount = IntegerField(null=True, blank=True)
    lastCompleteness = IntegerField(null=True, blank=True)
    lastResult = CharField(max_length=2000, null=True, blank=True)
    def get_absolute_url(self):
        return reverse('decision_detail', kwargs={'pk': self.pk})
    def getCompleteness(self):
        votes = self.vote_set.all()
        if len(votes) == self.lastVotesCount and self.lastCompleteness is not None:
            print "cached"
            return self.lastCompleteness
        criterias = self.criteria_variant_set.filter(crit_var=False).order_by('name')
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
        criteriasLen = len(criterias)
        variantsLen = len(variants)
        if criteriasLen < 2 or variantsLen < 2:
            return
        votesLen = len(votes)
        pairwiseCount = nCr(criteriasLen, 2)
        pairwiseCount += criteriasLen * nCr(variantsLen, 2)
        pairwiseCount += variantsLen * nCr(criteriasLen, 2)
        members = self.invite_set.filter(state="AC")
        self.lastCompleteness = votesLen
        self.save()
        decisionValue = DecisionValue(decision=self, votes=votesLen)
        decisionValue.save()
        return [pairwiseCount * len(members), self.lastCompleteness]
         
    def getVotes(self):
        return self.vote_set.all().select_related('critVarLeft', 'critVarRight', 'parentCrit').order_by('order')
    def getPairwiseComparison(self):
        criterias = self.criteria_variant_set.filter(crit_var=False).order_by('name')
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
        array = []
        #         pairwise criteria
        array.append([None, itertools.combinations(criterias, 2)])
        #         pairwise variants with respect to criteria
        for criteria in criterias:
            array.append([criteria, itertools.combinations(variants, 2)])
        #         pairwise variant to criteria
        for variant in variants:
            array.append([variant, itertools.combinations(criterias, 2)])
        return array
    def getCriterias(self):
        return self.criteria_variant_set.filter(crit_var=False)
    def getVariants(self):
        return self.criteria_variant_set.filter(crit_var=True)
    def getInvited(self):
        return self.invite_set.filter(state__in=["SE","SN"])
    def getMembers(self):
        return self.invite_set.filter(state="AC")
    def getUninvited(self):
        return CustomUser.objects.exclude(invite__decision=self)
    def evaluate(self):
        votes = self.vote_set.all().select_related('critVarLeft', 'critVarRight', 'user').order_by('id')
        if len(votes) == self.lastVotesCount:
            print "cached"
            return
        criterias = self.criteria_variant_set.filter(crit_var=False).order_by('name')
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
        criteriasLength = len(criterias)
        variantsLength = len(variants)
        supermatrix = np.eye(1+criteriasLength+variantsLength)
        for i, weight in enumerate(calcCriteriaWeight(criterias, votes)):
            supermatrix[i + 1, 0] = weight
        for j, criteria in enumerate(criterias):
            for i, weight in enumerate(calcVariantsWeightRespectToCriteria(variants, votes, criteria)):
                supermatrix[1+criteriasLength+i,j+1] = weight
#         AHP
#         np.linalg.matrix_power(supermatrix, 2)
#         rank in bottom left
        for j, variant in enumerate(variants):
            for i, weight in enumerate(calcCriteriasWeightRespectToVariant(criterias, votes, variant)):
                supermatrix[1+i,j+1+criteriasLength] = weight
        i = 1
        diff = True
        priorities = np.array([])
        old_priorities = None
        while diff:
            supermatrix_pow = np.linalg.matrix_power(supermatrix, 2*i)
            for j in range(0, variantsLength):
                priorities = np.append(priorities, supermatrix_pow.item(1+j+criteriasLength,0))
            priorities = priorities / np.linalg.norm(priorities, 1)
            if old_priorities is not None:
                difference = priorities - old_priorities
                newDiff = False
                for k in difference:
                    if abs(k) > self.LIMIT_MATRIX_DECIMAL_PRECISION:
                        newDiff = True
                diff = newDiff
            old_priorities = priorities
            priorities = np.array([])
            i += 1
        self.lastResult = ";".join(str(x) for x in old_priorities)
        self.lastVotesCount = len(votes)
        self.save()
#         print old_priorities
    def __unicode__(self):
        return self.get_state_display() + "_" + self.name
    
class DecisionValue(models.Model):
    decision = ForeignKey(Decision)
    date = DateField(default=now)
    votes = IntegerField()
    
class Criteria_Variant(models.Model):
    decision = ForeignKey(Decision)
    name = CharField(max_length=200)
    description = CharField(max_length=200, blank=True)
    image = ImageField(null=True, blank=True, upload_to="pics/critvar")
    crit_var = BooleanField(default=None)
    def __unicode__(self):
        return re.sub(r'[_ -]*','',self.name)
    
class Vote(models.Model):
    DEFINETLY_LEFT = 9
    LEFT = 7
    SEST = 6
    PROBABLY_LEFT = 5
    STYRI = 4
    MORE_LEFT = 3
    DVA = 2
    SAME = 1
    POLOVICA = 0.5
    MORE_RIHT = 0.333333
    STVRTINA = 0.25
    PROBABLY_RIGHT = 0.2
    SESTINA = 0.166666
    RIGHT = 0.142857
    DEFINETLY_RIGHT = 0.111111
    VOTE_CHOICES = (
        (DEFINETLY_LEFT, u'Jednoznačne Ľavé'),
        (LEFT, u'Ľavé'),
        (SEST, u'SEST'),
        (PROBABLY_LEFT, u'Skôr Ľavé'),
        (STYRI, u'STYRI'),
        (MORE_LEFT, u'Asi Ľavé'),
        (DVA, u'DVA'),
        (SAME, u'Rovnaké'),
        (POLOVICA, u'POLOVICA'),
        (MORE_RIHT, u'Asi pravé'),
        (STVRTINA, u'STVRTINA'),
        (PROBABLY_RIGHT, u'Skôr pravé'),
        (SESTINA, u'SESTINA'),
        (RIGHT, u'Pravé'),
        (DEFINETLY_RIGHT, u'Jednoznačne pravé'),
    )
    ROOKIE = 2
    TRAINEE = 4
    EDUCATED = 6
    PROFFESIONAL = 8
    EXPERT = 10
    WEIGHT_CHOICES = (
        (ROOKIE, u'Začiatočník'),
        (TRAINEE, u'Učeň'),
        (EDUCATED, u'Vyučený'),
        (PROFFESIONAL, u'Profesionál'),
        (EXPERT, u'Expert'),
    )
    order = IntegerField()
    userWeight = IntegerField(choices=WEIGHT_CHOICES)
    user = ForeignKey(CustomUser)
    decision = ForeignKey(Decision)
    parentCrit = ForeignKey(Criteria_Variant, related_name='critVar_parent', default=None, null=True, blank=True)
    critVarLeft = ForeignKey(Criteria_Variant, related_name='critVar_left', default=None)
    critVarRight = ForeignKey(Criteria_Variant, related_name='critVar_right', default=None)
    value = FloatField(choices=VOTE_CHOICES)
    def __unicode__(self):
        return (self.parentCrit.__unicode__() + "_" if self.parentCrit is not None else "") + self.critVarLeft.__unicode__() + "-" + self.critVarRight.__unicode__()
    