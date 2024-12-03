from django import forms
from .models import Items, Marketplace, TagItem

class AddItemForm(forms.ModelForm):
    mtplace = forms.ModelChoiceField(queryset=Marketplace.objects.all(), empty_label='Маркетплейс не выбран', label='Маркетплейс')
    tags = forms.ModelMultipleChoiceField(queryset=TagItem.objects.all(), label='Тэги', required=False)

    class Meta:
        model = Items
        fields = ['mtplace', 'id_item', 'name_for_user', 'tags']