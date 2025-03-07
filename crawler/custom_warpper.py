import base64
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps

from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator

from .models import ConfigValues


def custom_required(view_func):
    """
    Decorator to check a custom condition and redirect if it fails.
    Works with both function-based views and class-based views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if condition(request):  # Replace with your condition
            return redirect(reverse_lazy('crawler:q-list'))  # Change to your redirect page
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def condition(request) -> bool:
    """
    Define your custom condition logic.
    Example: Allow only staff users.
    """
    cfg = ConfigValues.objects.filter(key="range").first()
    if cfg:
        val = base64.b64decode(cfg.val.encode("utf-8")).decode("utf-8")
        drange = datetime.strptime(val, "%Y:%m:%d-%H:%M:%S%Z%z")
        now = timezone.now()
        print(now > drange)
        return now > drange
    else:
        return False

# Decorator for class-based views
def custom_required_class_based(view):
    decorator = method_decorator(custom_required)

    if hasattr(view, 'dispatch'):
        view.dispatch = decorator(view.dispatch)
    return view