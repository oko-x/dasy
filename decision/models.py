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
    calcCriteriasWeightRespectToVariant, nCr, calculatePercentageFromVector
import numpy as np
from StringIO import StringIO

# Create your models here.
class CustomUser(AbstractUser):
    image = ImageField(null=True, blank=True, upload_to="pics/avatars", default = 'pics/no-img.png')
    def getInvites(self):
        return self.invite_set.all()
    def getUnrespondedInvites(self):
        return self.invite_set.filter(state__in=["SE","SN"]).select_related('decision')
    def getDecisionsInvited(self):
        return self.invite_set.filter(state="AC").select_related('decision')
    def getDecisionsCreated(self):
        return self.decision_set.exclude(invite__state__in=["AC"])
    
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
    description = CharField( max_length=2000, blank=True)
    creator = ForeignKey(CustomUser)
    image = ImageField(null=True, blank=True, upload_to="pics/decision", default = 'pics/no-img.png')
    state = CharField(max_length=2, choices=STATE_CHOICES, default="NE")
    published = DateField(default=now)
    stage_one_date = DateField(null=True, blank=True)
    stage_two_date = DateField(null=True, blank=True)
    lastVotesCount = IntegerField(null=True, blank=True)
    lastMembersCount = IntegerField(null=True, blank=True)
    lastCompleteness = IntegerField(null=True, blank=True)
    lastSupermatrix = CharField(max_length=10000, null=True, blank=True)
    fullCompleteness = IntegerField(null=True, blank=True)
    pairwiseCount = IntegerField(null=True, blank=True)
    lastResult = CharField(max_length=2000, null=True, blank=True)
    def get_absolute_url(self):
        return reverse('decision_detail', kwargs={'pk': self.pk})
    def getDetailGraphData(self):
        criterias = self.criteria_variant_set.filter(crit_var=False).order_by('name')
        critLen = len(criterias)
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
        supermatrixTxt = re.sub(r'[[\]]*','',self.lastSupermatrix)
        supermatrix = np.loadtxt(StringIO(supermatrixTxt))
        print supermatrix
        critChart = []
        varChart = []
        variantWRTCritChart = []
        criteriaWRTVariantChart = []
        for i, criteria in enumerate(criterias):
            critChart.append([criteria.name,round(supermatrix[1+i][0]*100,1)])
            variantDataArray = []
            for j, variant in enumerate(variants):
                variantDataArray.append([variant.name, round(supermatrix[1+critLen+j][1+i]*100,1)])
            variantWRTCritChart.append([criteria, variantDataArray])
        for i, variant in enumerate(variants):
            criteriaDataArray = []
            for j, criteria in enumerate(criterias):
                criteriaDataArray.append([criteria.name, round(supermatrix[1+j][1+critLen+i]*100,1)])
            criteriaWRTVariantChart.append([variant, criteriaDataArray])
        return [critChart, variantWRTCritChart, criteriaWRTVariantChart, varChart]
    def getDecisionDetailData(self):
        completeness = self.getCompleteness()
        percentualCompleteness = round((completeness[1]/float(completeness[0])*100),1)
        currentCompleteness = completeness[1]
        completenessRemainder = completeness[0] - completeness[1]
        completenessHistory = self.decisionvalue_set.all().order_by('date')
        return [completenessRemainder, currentCompleteness, completenessHistory, percentualCompleteness]
    def getCompleteness(self):
        votes = self.vote_set.all()
        votesLen = len(votes)
        members = self.invite_set.filter(state="AC")
        membersLen = len(members)
        if votesLen == self.lastVotesCount and membersLen == self.lastMembersCount and self.lastCompleteness is not None and self.fullCompleteness is not None:
            print self.name + " cached"
            percentualCompleteness = round((self.lastCompleteness/float(self.fullCompleteness)*100),1)
            return [self.fullCompleteness, self.lastCompleteness, percentualCompleteness]
        if self.pairwiseCount is None:
            criterias = self.criteria_variant_set.filter(crit_var=False).order_by('name')
            variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
            criteriasLen = len(criterias)
            variantsLen = len(variants)
            if criteriasLen < 2 or variantsLen < 2:
                return
            pairwiseCount = nCr(criteriasLen, 2)
            pairwiseCount += criteriasLen * nCr(variantsLen, 2)
            pairwiseCount += variantsLen * nCr(criteriasLen, 2)
            self.pairwiseCount = pairwiseCount
        pairwiseCount = self.pairwiseCount
        self.evaluate()
        self.lastCompleteness = votesLen
        self.fullCompleteness = pairwiseCount * membersLen
        self.lastMembersCount = membersLen
        self.save()
        decisionValue = DecisionValue.objects.filter(decision=self, date=now)
        if not decisionValue:
            decisionValue = DecisionValue(decision=self, votes=votesLen, lastResult=self.lastResult)
        else:
            decisionValue = decisionValue[0]
            decisionValue.votes = votesLen
            decisionValue.lastResult = self.lastResult
        decisionValue.save()
        percentualCompleteness = round((self.lastCompleteness/float(self.fullCompleteness)*100),1)
        return [self.fullCompleteness, self.lastCompleteness, percentualCompleteness]
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
        return self.criteria_variant_set.filter(crit_var=False).order_by('name')
    def getVariants(self):
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('name')
        result = calculatePercentageFromVector(self.lastResult)
        resultArray = []
        for i, variant in enumerate(variants):
            resultArray.append([variant, result[i]])
        return resultArray
    def getInvited(self):
        return self.invite_set.all()
    def getMembers(self):
        return self.invite_set.filter(state="AC")
    def getUninvited(self):
        return CustomUser.objects.exclude(invite__decision=self)
    def evaluate(self):
        votes = self.vote_set.all().select_related('critVarLeft', 'critVarRight', 'user').order_by('id')
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
        self.lastSupermatrix = supermatrix
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
    lastResult = CharField(max_length=2000, null=True, blank=True)
    def __unicode__(self):
        return str(self.date) + "_" + str(self.votes) + "_" + str(self.lastResult)
    
class Criteria_Variant(models.Model):
    decision = ForeignKey(Decision)
    name = CharField(max_length=200)
    description = CharField(max_length=2000, blank=True)
    image = ImageField(null=True, blank=True, upload_to="pics/critvar", default = 'pics/no-img.png')
    crit_var = BooleanField(default=None)
    def __unicode__(self):
        return re.sub(r'[_ -]*','',self.name)
    
class Vote(models.Model):
    DEFINETLY_LEFT = 9
    OSEM = 8
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
    OSMINA = 0.125
    DEFINETLY_RIGHT = 0.111111
    VOTE_CHOICES = (
        (DEFINETLY_LEFT, u'Jednoznačne ľav'),
        (OSEM, u'OSEM'),
        (LEFT, u'Ľav'),
        (SEST, u'SEST'),
        (PROBABLY_LEFT, u'Skôr ľav'),
        (STYRI, u'STYRI'),
        (MORE_LEFT, u'Asi ľav'),
        (DVA, u'DVA'),
        (SAME, u'Sú rovnaké'),
        (POLOVICA, u'POLOVICA'),
        (MORE_RIHT, u'Asi prav'),
        (STVRTINA, u'STVRTINA'),
        (PROBABLY_RIGHT, u'Skôr prav'),
        (SESTINA, u'SESTINA'),
        (RIGHT, u'Prav'),
        (OSMINA, u'OSMINA'),
        (DEFINETLY_RIGHT, u'Jednoznačne prav'),
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
    