#admin.py
from django.contrib import admin

# Register your models here.
from products.models import KindOfActivity, Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'kind_of_activity', 'code', 'status', 'validity']

    fields = ['name', 'number', 'code', 'validity', 'status', 'address', 'first_phone', 'email', 'second_phone', 'user', 'password']


admin.site.register(KindOfActivity)
admin.site.register(Company, CompanyAdmin)

