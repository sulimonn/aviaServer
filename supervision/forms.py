from datetime import datetime

from dateutil.relativedelta import relativedelta
from django import forms
from supervision.models import CheckMonth, OversightPeriod
from documents.models import Checklist, Prescription, PKD, Approval, Elimination, Report, Notification, Moved


class ChecklistForm(forms.ModelForm):
    month = forms.IntegerField(required=False)
    area = forms.IntegerField(required=False)

    class Meta:
        model = Checklist
        fields = ['month', 'files', 'comment']
        widgets = {
            'files': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class CheckMonthForm(forms.ModelForm):
    class Meta:
        model = CheckMonth
        fields = ['checking']
        widgets = {
            'checking': forms.CheckboxInput(attrs={'class': 'absol'})
        }


class PrescriptionForm(forms.ModelForm):

    class Meta:
        model = Prescription
        fields = ['letter', 'fine_protocol']
        widgets = {
            'letter': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'fine_protocol': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'})
        }


class PKDForm(forms.ModelForm):

    class Meta:
        model = PKD
        fields = ['letter', 'pkd']
        widgets = {
            'letter': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'pkd': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class ApprovalForm(forms.ModelForm):

    class Meta:
        model = Approval
        fields = ['approval', 'deadline']
        widgets = {
            'approval': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'deadline': forms.DateInput(
                                format=('%Y-%m-%d'),
                                attrs={'class': 'form-control',
                                       'type': 'date'
                                      }),
        }


class EliminationForm(forms.ModelForm):

    class Meta:
        model = Elimination
        fields = ['letter']
        widgets = {
            'letter': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['report']
        widgets = {
            'report': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ['letter']
        widgets = {
            'letter': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class MovedForm(forms.ModelForm):
    class Meta:
        model = Moved
        fields = ['raport']
        widgets = {
            'raport': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        }


class OversightPeriodForm(forms.ModelForm):
    current = datetime.today().date()
    start = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(current.year, current.year + 10)
        )
    )

    class Meta:
        model = OversightPeriod
        fields = ['start']

    def __init__(self, *args, **kwargs):
        super(OversightPeriodForm, self).__init__(*args, **kwargs)
        self.fields['start'].initial = datetime.today().date()
