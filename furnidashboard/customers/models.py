from django.db import models
from django.conf import settings

class Customer(models.Model):
  """
  A model class representing customer information
  """

  # save this for later
  #user = models.OneToOneField(settings.AUTH_USER_MODEL)

  first_name = models.CharField(max_length=200, blank=False)
  last_name = models.CharField(max_length=200, blank=True)
  phone = models.CharField(max_length=30, blank=True, null=True)
  email  = models.EmailField(blank=True, null=True)
  address  = models.TextField(blank=True, null=True)
  
  @property
  def full_name(self):
    return self.first_name + " " + self.last_name
  

  class Meta:
    db_table = "customers"

  def __unicode__(self):
    return "{0} {1}".format(self.first_name, self.last_name)

