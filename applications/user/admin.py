from django.contrib import admin
from . models import Person, CompanyUser, EmployeUser, Account
# Register your models here.
admin.site.register((Person, CompanyUser, EmployeUser, Account))
