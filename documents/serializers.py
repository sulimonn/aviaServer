from rest_framework import serializers
from documents.models import Checklist, LANGUAGE_CHOICES, STYLE_CHOICES


class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = '__all__'

    def create(self, validated_data):
        return Checklist.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.count = validated_data.get('count', instance.count)
        instance.month = validated_data.get('month', instance.month)
        instance.files = validated_data.get('files', instance.files)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.area = validated_data.get('area', instance.area)
        instance.original = validated_data.get('original', instance.original)
        instance.save()
        return instance
