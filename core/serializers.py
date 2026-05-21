from unicodedata import name

from rest_framework import serializers

from core.models import Department


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ['code','name','description']

    # name = serializers.CharField(max_length=120, required=True)
    # code = serializers.CharField(max_length=10, required=True)
    # description = serializers.CharField(max_length= 255,required =False)



