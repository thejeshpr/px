import json

from django import forms
from django.core.exceptions import ValidationError


#
# created_at = models.DateTimeField(auto_now_add=True, db_index=True)
# data = models.TextField(blank=True, null=True)
# is_bookmarked = models.BooleanField(default=False, db_index=True)
# job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='items', db_index=True)
# name = models.CharField(max_length=500, db_index=True)
# site_conf = models.ForeignKey('SiteConf', on_delete=models.CASCADE, related_name='items', db_index=True)
# unique_key = models.CharField(max_length=2500, unique=True)
# updated_at = models.DateTimeField(auto_now=True)
# url = models.URLField(blank=True, null=True, max_length=2500, db_index=True)


class ItemCreateForm(forms.Form):
    url = forms.URLField(label="URL", required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    data = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # bookmark = forms.BooleanField(required=False)
    ns = forms.BooleanField(required=False)


class SiteConfFormByJSON(forms.Form):
    json_data = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        json_data = self.cleaned_data.get("json_data")
        if json_data:
            try:
                _ = json.loads(json_data)
            except Exception as e:
                self.add_error(None, ValidationError(f"Invalid JSON Data: {e}"))
        return cleaned_data
