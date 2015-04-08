# -*- coding: utf-8 -*-

from timeit import itertools

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import CharField, BooleanField, DateField, IntegerField,\
    FloatField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.utils.timezone import now

import numpy as np
from mysite.utils import calcCriteriaWeight


# Create your models here.
class CustomUser(AbstractUser):
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
    image = ImageField(null=True, blank=True, upload_to="pics/avatars")
    weight = IntegerField(choices=WEIGHT_CHOICES)
    def getInvites(self):
        return self.invite_set.all()
    def getDecisions(self):
        return self.invite_set.filter(state="AC").select_related('decision')
    
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
    user = ForeignKey(CustomUser)
    decision = ForeignKey('Decision')
    state = CharField(max_length=2, choices=STATE_CHOICES, default="SE")
    def acceptInvite(self):
        self.state = "AC"
        self.save()
    def setSeen(self):
        self.state = "SN"
        self.save()
    
class Decision(models.Model):
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
    image = ImageField(null=True, blank=True, upload_to="pics/decision")
    state = CharField(max_length=2, choices=STATE_CHOICES, default="NE")
    published = DateField(default=now)
    stage_one_date = DateField(null=True, blank=True)
    stage_two_date = DateField(null=True, blank=True)
    def getVotes(self):
        return self.vote_set.all().select_related('critVarLeft', 'critVarRight')
    def getPairwiseComparison(self):
        criterias = self.criteria_variant_set.filter(crit_var=False)
        variants = self.criteria_variant_set.filter(crit_var=True)
        array = []
        #         pairwise criteria
        array.append(["pairwise criteria", itertools.combinations(criterias, 2)])
        #         pairwise variants with respect to criteria
        for criteria in criterias:
            array.append([criteria, itertools.combinations(variants, 2)])
        #         pairwise variant to criteria
        array.append(["pairwise variant to criteria", itertools.product(variants, criterias)])
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
        criterias = self.criteria_variant_set.filter(crit_var=False).order_by('id')
        variants = self.criteria_variant_set.filter(crit_var=True).order_by('id')
        votes = self.vote_set.all().select_related('critVarLeft', 'critVarRight', 'user').order_by('id')
        print calcCriteriaWeight(criterias, votes)
        return
    def __unicode__(self):
        return self.get_state_display() + "_" + self.name
    
class Criteria_Variant(models.Model):
    decision = ForeignKey(Decision)
    name = CharField(max_length=200)
    description = CharField(max_length=200, blank=True)
    image = ImageField(null=True, blank=True, upload_to="pics/critvar")
    crit_var = BooleanField(default=None)
    def __unicode__(self):
        return self.decision.__unicode__()+"_"+("Variant_" if self.crit_var else "Criteria_") +self.name
    
class Vote(models.Model):
    DEFINETLY_LEFT = 9
    LEFT = 7
    PROBABLY_LEFT = 5
    MORE_LEFT = 3
    SAME = 1
    MORE_RIHT = 0.333333
    PROBABLY_RIGHT = 0.2
    RIGHT = 0.142857
    DEFINETLY_RIGHT = 0.111111
    VOTE_CHOICES = (
        (DEFINETLY_LEFT, u'Jednoznačne Ľavé'),
        (LEFT, u'Ľavé'),
        (PROBABLY_LEFT, u'Skôr Ľavé'),
        (MORE_LEFT, u'Asi Ľavé'),
        (SAME, u'Ľavé'),
        (MORE_RIHT, u'Asi pravé'),
        (PROBABLY_RIGHT, u'Skôr pravé'),
        (RIGHT, u'Pravé'),
        (DEFINETLY_RIGHT, u'Jednoznačne pravé'),
    )
    user = ForeignKey(CustomUser)
    decision = ForeignKey(Decision)
    parentCrit = ForeignKey(Criteria_Variant, related_name='critVar_parent', default=None, null=True, blank=True)
    critVarLeft = ForeignKey(Criteria_Variant, related_name='critVar_left', default=None)
    critVarRight = ForeignKey(Criteria_Variant, related_name='critVar_right', default=None)
    value = FloatField(choices=VOTE_CHOICES)
    def __unicode__(self):
        return self.critVarLeft.__unicode__() + "_" + self.critVarRight.__unicode__() + "_" + self.user.__unicode__() + "_" + self.get_value_display()
    