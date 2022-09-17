from rest_framework import serializers
from .models import Font, preview
from rest_framework.validators import UniqueValidator

class PreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = preview
        fields = '__all__'


class FontSerializer(serializers.ModelSerializer):
    like_num = serializers.ReadOnlyField()
    previews = PreviewSerializer(many=True, read_only =True)
    class Meta:
        model = Font
        fields = '__all__'

class FontPublicSerializer(serializers.ModelSerializer):
    previews = PreviewSerializer(many=True, read_only =True)
    class Meta:
        model = Font
        read_only_fields = ('name', 'file')
        fields = '__all__'

class FontLookAroundSerializer(serializers.ModelSerializer):
    like_num = serializers.ReadOnlyField()
    previews = PreviewSerializer(many=True, read_only =True)
    class Meta:
        model = Font
        fields = ['like_num','name','file','like_users']

class NameUniqueCheckSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True,min_length=1, max_length=50, validators=[UniqueValidator(queryset=Font.objects.all())])

    class Meta:
        model = Font
        fields = ['name']
