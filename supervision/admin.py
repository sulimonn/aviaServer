from django.contrib import admin

from supervision import models
from supervision.models import CheckArea, CheckMonth, Permission, OversightPeriod, Deadline
from documents.models import Checklist, Prescription, PKD, Approval, Elimination, Report, Notification
from django.utils.translation import gettext_lazy as _

from users.models import User


class InspectorGroupFilter(admin.SimpleListFilter):
    title = _('Inspector Group')
    parameter_name = 'inspector_group'

    def lookups(self, request, model_admin):
        inspectors = User.objects.filter(groups__name='ins')
        return [(inspector.pk, inspector.username) for inspector in inspectors]

    def queryset(self, request, queryset):
        print(request)
        if self.value():
            return queryset.filter(user_id=self.value())
        else:
            return queryset


class ChecklistAdmin(admin.ModelAdmin):
    list_display = ['month', 'files', 'comment', 'area', 'original', 'count']

    def get_fields(self, request, obj=None):
        if obj and obj.count == 1:
            return ['month', 'files', 'comment', 'area', 'original']
        else:
            return ['files', 'comment', 'original']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.count == 1:
            return ['count']
        else:
            return ['month', 'area', 'count']

    search_fields = ('area__title', 'month__date__month')
    list_filter = ('area', 'month')


class DeadlineAdmin(admin.ModelAdmin):
    list_display = ('user', 'until_the_deadline', 'month')
    ordering = ('until_the_deadline',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'month__month', 'month__area__title')
    list_filter = (InspectorGroupFilter, 'month')
    list_display_links = ('user', 'until_the_deadline', 'month')


admin.site.register(CheckArea)
admin.site.register(CheckMonth)
admin.site.register(OversightPeriod)
admin.site.register(Deadline, DeadlineAdmin)


admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(Prescription)
admin.site.register(Approval)
admin.site.register(PKD)
admin.site.register(Notification)
admin.site.register(Elimination)
admin.site.register(Report)
admin.site.register(Permission)
