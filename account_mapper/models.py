from django.db import models

class RawData(models.Model):
    distributor_name = models.CharField(max_length=255, null=True, blank=True)
    retailer_name = models.CharField(max_length=255)
    item_description = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.retailer_name
