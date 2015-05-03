from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from decision.models import Decision, Criteria_Variant, Vote, Invite, CustomUser,\
    DecisionValue
from mysite.forms import UserCreationForm


# Register your models here.
admin.site.register(Invite)
admin.site.register(Criteria_Variant)
admin.site.register(Vote)
admin.site.register(DecisionValue)

class CriteriaInline(admin.TabularInline):
    model = Criteria_Variant
    extra = 1


class DecisionAdmin(admin.ModelAdmin):
    inlines = [CriteriaInline]
    
class CustomUserAdmin(UserAdmin):
    model = CustomUser

#     add_form = UserCreationForm
#     list_display = ("username",)
#     ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('image',)}),
    )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active')}
#             ),
#         )
# 
#     filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Decision, DecisionAdmin)