import json

from django import forms
from django.core.exceptions import ValidationError

from crawler.models import Category, SiteConf, Job, Item


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


class BulJobForm(forms.Form):
    site_confs = forms.CharField(widget=forms.Textarea, required=True)
    ns = forms.BooleanField(required=False, widget=forms.HiddenInput())


# class SiteConfFilterForm(forms.Form):
#     category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())

class SiteConfFilterForm(forms.Form):
    # category = forms.ModelChoiceField(
    #     queryset=Category.objects.all(), required=False, empty_label="All Categories"
    # )
    category = forms.ChoiceField(choices=[], required=False)
    scraper_name = forms.ChoiceField(choices=[], required=False)
    enabled = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Enabled'), ('false', 'Disabled')],
        required=False
    )
    is_locked = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Locked'), ('false', 'Unlocked')],
        required=False
    )
    ns = forms.BooleanField(required=False, widget=forms.HiddenInput())
    never_synced = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # fetch categories
        categories = Category.objects.values_list('slug', 'slug').distinct()
        category_choices = [('', 'All Categories')] + list(categories)
        self.fields['category'].choices = category_choices

        # Fetch unique scraper names dynamically
        unique_scrapers = SiteConf.objects.values_list('scraper_name', flat=True).distinct()
        unique_scrapers = [(scraper, scraper) for scraper in unique_scrapers if scraper]
        unique_scrapers.insert(0, ('', 'All Scrapers'))  # Default option
        self.fields['scraper_name'].choices = unique_scrapers

    # commented below because its not working as expected in views

    # def clean_enabled(self):
    #     """Convert enabled field to Boolean."""
    #     value = self.cleaned_data.get('enabled')
    #     if value == 'true':
    #         return True
    #     elif value == 'false':
    #         return False
    #     return None  # For 'All' option
    #
    # def clean_is_locked(self):
    #     """Convert is_locked field to Boolean."""
    #     value = self.cleaned_data.get('is_locked')
    #     if value == 'true':
    #         return True
    #     elif value == 'false':
    #         return False
    #     return None  # For 'All' option



class JobFilterForm(forms.Form):
    category = forms.ChoiceField(choices=[], required=False)
    site_conf = forms.ChoiceField(choices=[], required=False)
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Job.JOB_STATUS),
        required=False
    )
    created_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    ns = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        site_conf = None
        if 'site_conf' in kwargs:
            site_conf = kwargs.pop('site_conf')

        super().__init__(*args, **kwargs)

        # Populate category choices using slug
        categories = Category.objects.values_list('slug', 'slug').distinct()
        category_choices = [('', 'All Categories')] + list(categories)
        self.fields['category'].choices = category_choices

        # Populate site_conf choices using slug
        if site_conf:
            self.fields['site_conf'].choices = site_conf
        else:
            site_confs = SiteConf.objects.values_list('slug', 'slug').distinct()
            site_conf_choices = [('', 'All Site Configs')] + list(site_confs)
            self.fields['site_conf'].choices = site_conf_choices


class ItemSearchForm(forms.Form):
    category = forms.ChoiceField(choices=[], required=False)
    site_conf = forms.ChoiceField(choices=[], required=False)
    # status = forms.ChoiceField(choices=[], required=False)
    # status = forms.ChoiceField(
    #     choices=[('', 'All Statuses')] + list(Item.I),
    #     required=False
    # )
    # is_bookmarked = forms.ChoiceField(
    #     choices=[('', 'All'), ('1', 'Yes'), ('0', 'No')],
    #     required=False
    # )
    is_bookmarked = forms.BooleanField(required=False, label="Show Bookmarked Items")
    created_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    ns = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        site_conf = None
        if 'site_conf' in kwargs:
            site_conf = kwargs.pop('site_conf')

        super().__init__(*args, **kwargs)

        # Populate category choices using slug
        categories = Category.objects.values_list('slug', 'slug').distinct()
        self.fields['category'].choices = [('', 'All Categories')] + list(categories)

                # Populate site_conf choices using slug
        if site_conf:
            self.fields['site_conf'].choices = site_conf
        else:
            site_confs = SiteConf.objects.values_list('slug', 'slug').distinct()
            self.fields['site_conf'].choices = [('', 'All Site Configs')] + list(site_confs)

        # Populate status choices dynamically from model
        # status_choices = Item.objects.values_list('status', 'status').distinct()
        # self.fields['status'].choices = [('', 'All Statuses')] + list(status_choices)
