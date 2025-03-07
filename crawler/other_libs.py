from .models import ConfigValues


def check_if_ns_enabled(request):
    sns = ConfigValues.objects.filter(key="sns").first()

    if sns and sns.val.lower() == "true":
        try:
            agent = request.META['HTTP_SEC_CH_UA_PLATFORM'].replace('"', '').lower()
        except Exception as e:
            agent = "none"

        if agent == "windows":
            return False
        else:
            return True
    else:
        return False
