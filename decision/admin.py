from django.contrib import admin

# Register your models here.
from decision.models import Decision, Criteria_Variant, Vote, Invite

admin.site.register(Invite)
admin.site.register(Criteria_Variant)
admin.site.register(Vote)

class CriteriaInline(admin.TabularInline):
    model = Criteria_Variant
    extra = 1


class DecisionAdmin(admin.ModelAdmin):
    inlines = [CriteriaInline]
    
admin.site.register(Decision, DecisionAdmin)