from django.contrib import admin
from supervision.models import CheckArea, CheckMonth, Permission, OversightPeriod, Deadline
from documents.models import Checklist, Prescription, PKD, Approval, Elimination, Report, Notification


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


class PermissionAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj and obj.user.groups.all().first().name == 'ins':
            return ['user', 'area']
        elif obj and obj.user.groups.all().first().name == 'avia':
            return ['user', 'company']
        else:
            return ['user', 'company', 'area']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.user.groups.all().first().name == 'ins':
            return ['company']
        elif obj and obj.user.groups.all().first().name == 'avia':
            return ['area']
        else:
            return []


admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(CheckArea)
admin.site.register(CheckMonth)
admin.site.register(Prescription)
admin.site.register(Approval)
admin.site.register(PKD)
admin.site.register(Notification)
admin.site.register(Elimination)
admin.site.register(Report)
admin.site.register(OversightPeriod)
admin.site.register(Deadline)
admin.site.register(Permission, PermissionAdmin)
