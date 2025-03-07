import json

from django import forms
from django.core.exceptions import ValidationError

from .models import FisherMan, FishType, Ship, Net


class FishAddForm(forms.Form):
    link = forms.URLField(label="link", required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    additional_info = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_dangerous = forms.BooleanField(required=False)


class FishermanCreateByJSONForm(forms.Form):
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


def get_fish_type_choices():
    fish_types = FishType.objects.values_list('slug', 'slug').distinct()
    fish_type_choices = [('', 'All Fishes')] + list(fish_types)
    return fish_type_choices


def get_fishers(show_dangerous):
    if show_dangerous and show_dangerous == "yes":
        fishers = FisherMan.objects.filter(is_dangerous=True).values_list('slug', 'slug').distinct()
        return [('', 'All Fishers')] + list(fishers)

    else:
        fishers = FisherMan.objects.values_list('slug', 'slug').distinct()
        return [('', 'All Fishers')] + list(fishers)


class FishermanFilterForm(forms.Form):
    fish_type = forms.ChoiceField(choices=[], required=False)
    strategy = forms.ChoiceField(choices=[], required=False)
    active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'yes'), ('false', 'no')],
        required=False
    )
    is_fishing = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'yes'), ('false', 'no')],
        required=False
    )
    dangerous = forms.BooleanField(required=False, widget=forms.HiddenInput())
    never_fished = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # fetch fish types dynamically
        # fish_types = FishType.objects.values_list('slug', 'slug').distinct()
        # fish_type_choices = [('', 'All Fishes')] + list(fish_types)
        self.fields['fish_type'].choices = get_fish_type_choices()

        # Fetch fisherman strategies dynamically
        unique_strategies = FisherMan.objects.values_list('strategy', flat=True).distinct()
        unique_strategies = [(strategy, strategy) for strategy in unique_strategies if strategy]
        unique_strategies.insert(0, ('', 'All Strategies'))  # Default option
        self.fields['strategy'].choices = unique_strategies

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


class NetFilterForm(forms.Form):
    fish_type = forms.ChoiceField(choices=[], required=False)
    fisherman = forms.ChoiceField(choices=[], required=False)
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Net.STATUS_CHOICES),
        required=False
    )
    deployed_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    dangerous = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        show_dangerous = "no"
        if 'show_dangerous' in kwargs:
            show_dangerous = kwargs.pop('show_dangerous')

        super().__init__(*args, **kwargs)

        self.fields['fish_type'].choices = get_fish_type_choices()
        print('------------>', get_fishers(show_dangerous))
        self.fields['fisherman'].choices = get_fishers(show_dangerous)

        # Populate category choices using slug
        # fish_types = FishType.objects.values_list('slug', 'slug').distinct()

        # category_choices = [('', 'All Categories')] + list(categories)

        # # Populate site_conf choices using slug
        # if site_conf:
        #     self.fields['site_conf'].choices = site_conf
        # else:
        #     site_confs = SiteConf.objects.values_list('slug', 'slug').distinct()
        #     site_conf_choices = [('', 'All Site Configs')] + list(site_confs)
        #     self.fields['site_conf'].choices = site_conf_choices


class FishFilterForm(forms.Form):
    fish_type = forms.ChoiceField(choices=[], required=False)
    fisherman = forms.ChoiceField(choices=[], required=False)
    tagged = forms.BooleanField(required=False, label="Show Tagged Fishes Only")
    caught_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    dangerous = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        show_dangerous = "no"
        if 'show_dangerous' in kwargs:
            show_dangerous = kwargs.pop('show_dangerous')

        super().__init__(*args, **kwargs)

        self.fields['fish_type'].choices = get_fish_type_choices()
        self.fields['fisherman'].choices = get_fishers(show_dangerous)


        # fisherman = None
        # if 'fisherman' in kwargs:
        #     fisherman = kwargs.pop('fisherman')
        #
        # super().__init__(*args, **kwargs)
        #
        # # Populate category choices using slug
        # fish_types = FishType.objects.values_list('slug', 'slug').distinct()
        # self.fields['fish_type'].choices = [('', 'All Fishes')] + list(fish_types)
        #
        # # Populate Fishers choices using slug
        # if fisherman:
        #     self.fields['fisherman'].choices = fisherman
        # else:
        #     fishers = FisherMan.objects.values_list('slug', 'slug').distinct()
        #     self.fields['fisherman'].choices = [('', 'All Fishers')] + list(fishers)

        # Populate status choices dynamically from model
        # status_choices = Item.objects.values_list('status', 'status').distinct()
        # self.fields['status'].choices = [('', 'All Statuses')] + list(status_choices)


class BulkCreateForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        data = self.cleaned_data.get("data")
        if data:
            try:
                _ = json.loads(data)
            except Exception as e:
                self.add_error(None, ValidationError(f"Invalid JSON Data: {e}"))
        return cleaned_data


class ShipFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Ship.STATUS_CHOICES),
        required=False
    )
    departure_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    dangerous = forms.BooleanField(required=False, widget=forms.HiddenInput())
