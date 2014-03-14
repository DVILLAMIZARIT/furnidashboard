from django.db import models
from django.conf import settings

class Profile(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL)
  first_name = models.CharField(max_length=200, blank=False)
  last_name = models.CharField(max_length=200, blank=True)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)

  def __unicode__(self):
    return "{0} {1}".format(self.first_name, self.last_name)

