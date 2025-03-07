import logging
from .models import ShipConfig

logger = logging.getLogger(__name__)

def show_dangerous_fish(request):
    logger.debug("checking if dangerous fish should be shown")
    sdf = ShipConfig.objects.filter(key="sdf").first()

    if sdf and sdf.val.lower() == "yes":
        logger.debug("showing dangerous fish is enabled")
        try:
            logger.debug("checking agent")
            agent = request.META['HTTP_SEC_CH_UA_PLATFORM'].replace('"', '').lower()
            logger.debug(f'agent is {agent}')
        except Exception as e:
            logger.error("failed to find agent")
            logger.exception(e)
            agent = "NONE"

        if agent in ["", "NONE"]:
            logger.debug("not showing dangerous fish")
            return False
        else:
            logger.debug("showing dangerous fish")
            return True
    else:
        logger.debug("not showing dangerous fish")
        return False
