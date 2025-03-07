from django.db import models
import uuid
from django.template.defaultfilters import slugify
from django.urls import reverse


class FishType(models.Model):  # Category -> FishType
    name = models.CharField(max_length=50, unique=True, db_index=True)  # name -> name
    slug = models.SlugField(max_length=50, unique=True, db_index=True)  # slug -> slug

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        super(FishType, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('fishing:fish-type-list', kwargs={})


class FisherMan(models.Model):  # SiteConf -> FisherMan
    active = models.BooleanField(default=True, db_index=True)  # enabled -> active
    additional_data = models.TextField(blank=True, null=True, default="{}")  # extra_data_json -> additional_data
    base_url = models.CharField(max_length=2500, blank=True, null=True, db_index=True)
    joined_at = models.DateTimeField(auto_now_add=True, db_index=True)  # created_at -> created_at
    fish_type = models.ForeignKey('FishType', on_delete=models.SET_NULL, related_name='fishers', blank=True,
                                  null=True, db_index=True)
    is_dangerous = models.BooleanField(default=False, db_index=True)  # ns_flag -> is_dangerous
    is_docked = models.BooleanField(default=False, db_index=True)
    is_fishing = models.BooleanField(default=False, db_index=True)  # is_locked -> is_restricted
    last_successful_catch = models.DateTimeField(blank=True, null=True)  # last_successful_sync -> last_successful_catch
    name = models.CharField(max_length=50, unique=True, db_index=True)  # name -> method_name
    notes = models.TextField(blank=True, null=True)  # notes -> notes
    slug = models.SlugField(max_length=50, unique=True, db_index=True)  # slug -> slug
    store_catching_info = models.BooleanField(default=True)  # store_raw_data -> store_catching_info
    strategy = models.CharField(max_length=25, blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)  # updated_at -> updated_at

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        super(FisherMan, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('fleet:fisherman-detail', kwargs={'slug': self.slug})


class Ship(models.Model):  # JobQueue -> Ship
    STATUS_CHOICES = (
        ('WAITING', 'WAITING'),
        ('SAILING', 'SAILING'),
        ('RETURNED', 'RETURNED'),  # COMPLETED -> RETURNED
        ('DAMAGED', 'DAMAGED'),  # ERROR -> DAMAGED
    )
    departure_time = models.DateTimeField(blank=True, null=True)  # processed_at -> arrival_time
    docked_time = models.DateTimeField(auto_now_add=True, db_index=True)  # created_at -> departure_time
    is_dangerous = models.BooleanField(default=False)  # ns_flag -> is_dangerous
    name = models.CharField(max_length=100, db_index=True)  # name -> name
    problem = models.TextField(blank=True, null=True)  # error -> problem
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')  # status -> status
    time_spent = models.IntegerField(blank=True, null=True)  # elapsed_time -> time_spent

    def __str__(self):
        return f'Ship:{self.name}[{self.pk}]'

    def __repr__(self):
        return f'Ship:{self.name}[{self.pk}]'


class Net(models.Model):  # Job -> Net
    STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('CAST', 'CAST'),  # WAITING -> CAST
        ('IN-USE', 'IN-USE'),  # RUNNING -> IN USE
        ('FISHED', 'FISHED'),  # SUCCESS -> FISHED
        ('DAMAGED', 'DAMAGED'),  # ERROR -> DAMAGED
        ('EMPTY', 'EMPTY')  # NO-ITEM -> EMPTY
    )
    deployed_at = models.DateTimeField(auto_now_add=True, db_index=True)  # created_at -> deployed_at
    fishing_info = models.TextField(blank=True, null=True)  # raw_data -> raw_data
    fish_type = models.ForeignKey('FishType', on_delete=models.SET_NULL, related_name='nets',
                                  blank=True, null=True, db_index=True)
    is_dangerous = models.BooleanField(default=False)  # ns_flag -> is_dangerous
    problem = models.TextField(blank=True, null=True)  # error -> problem
    ship = models.ForeignKey('Ship', on_delete=models.CASCADE, blank=True, null=True, db_index=True,
                             related_name="nets")  # queue -> ship
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW", db_index=True)  # status -> status
    fisherman = models.ForeignKey('Fisherman', on_delete=models.CASCADE, related_name='nets',
                                 db_index=True)  # site_conf -> fishing_method
    time_in_water = models.IntegerField(blank=True, null=True)  # elapsed_time -> time_in_water

    def __str__(self):
        return f"Net:{self.pk}"

    def __repr__(self):
        return f"Net:{self.pk}"


class Fish(models.Model):  # Item -> Fish
    additional_info = models.TextField(blank=True, null=True)  # data -> characteristics
    caught_at = models.DateTimeField(auto_now_add=True, db_index=True)  # created_at -> caught_at
    net = models.ForeignKey('Net', on_delete=models.CASCADE, related_name='fishes', db_index=True, blank=True, null=True)  # job -> caught_in_net
    fisherman = models.ForeignKey('Fisherman', on_delete=models.CASCADE, related_name='fishes', db_index=True)  # site_conf -> fishing_method
    fish_type = models.ForeignKey('FishType', on_delete=models.SET_NULL, related_name='fishes', blank=True, null=True, db_index=True)  # category -> species
    is_dangerous = models.BooleanField(default=False)  # ns_flag -> is_dangerous
    link = models.URLField(blank=True, null=True, max_length=2500, db_index=True)  # url -> link
    name = models.CharField(max_length=500, db_index=True)  # name -> name
    ship = models.ForeignKey('Ship', on_delete=models.CASCADE, related_name='fishes', db_index=True, blank=True, null=True)  # queue -> ship
    tagged = models.BooleanField(default=False, db_index=True)  # is_bookmarked -> tagged
    tracking_id = models.CharField(max_length=2500, unique=True)  # unique_key -> tracking_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class ShipConfig(models.Model):  # ConfigValues -> ShipConfig
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # created_at -> created_at
    key = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)  # key -> config_key
    slug = models.SlugField(max_length=50, unique=True, db_index=True)  # slug -> slug
    updated_at = models.DateTimeField(auto_now=True)  # updated_at -> updated_at
    val = models.CharField(max_length=250, blank=True, null=True)  # val -> config_value

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.key

    def save(self, *args, **kwargs):
        self.key = self.key.lower()
        self.slug = slugify(self.key)
        super(ShipConfig, self).save(*args, **kwargs)