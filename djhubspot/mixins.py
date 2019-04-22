import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('vendors.dj_hubspot')


class HubspotSyncableManager(models.Manager):

    def get_by_hubspot_id(hubspot_id):
        return self.get(hubspot_id=hubspot_id)


class HubspotSyncable(models.Model):

    hubspot_id = models.IntegerField(_("Hubspot ID"),
        blank=True, null=True,
        help_text=_("The unique identifier of this object in Hubspot"),
    )

    class Meta:
        abstract = True

    def sync_from_hubspot(self):
        pass

    def sync_to_hubspot(self):
        pass
