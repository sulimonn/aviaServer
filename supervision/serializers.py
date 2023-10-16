from rest_framework import serializers
from .models import Permission
from documents.models import Checklist, Prescription, PKD, Approval, Elimination, Report, Notification


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['letter', 'fine_protocol', 'checklist']


class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = ['count', 'files', 'comment', 'id']


class PkdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PKD
        fields = ['letter', 'pkd']


class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ['approval', 'deadline']


class EliminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elimination
        fields = ['letter']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['report']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['letter']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['user', 'company', 'area']
