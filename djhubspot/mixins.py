import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('vendors.dj_hubspot')


class HubspotSyncableManager(models.Manager):

    def get_by_hubspot_id(self, hubspot_id):
        return self.get(hubspot_id=hubspot_id)

    def sync_with_hubspot(self, hubspot_id, defaults=None):
        """
        Perform an `update_or_create` on the object with the given `hubspot_id`, using the given
        `defaults`.

        Parameters
        ----------
        hubspot_id
        defaults

        Returns
        -------
        tuple
        """
        return self.update_or_create(
            hubspot_id=hubspot_id,
            defaults=defaults or {},
        )


class HubspotSyncable(models.Model):

    hubspot_id = models.BigIntegerField(
        _("Hubspot ID"),
        blank=True, null=True, unique=True,
        help_text=_("The unique identifier of this object in Hubspot"),
    )

    hubspot_last_synced_at = models.DateTimeField(
        _("Hubspot last synced at"),
        blank=True, null=True, editable=False,
        help_text=_("When the model has been synced with Hubspot for the last time"),
    )

    class Meta:
        abstract = True

    def sync_from_hubspot(self):
        pass

    def sync_to_hubspot(self):
        pass
