from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

class Lead(models.Model):
  """
  A class model representing the lead information
  """

  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  first_name = models.CharField(max_length=200, blank=False)
  last_name = models.CharField(max_length=200, blank=True)
  email  = models.EmailField(blank=True)
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, blank=True, null=True)

  class Meta:
    ordering = ["-created","-modified"]
  
  def __unicode__(self):
    return "{0}, {1}".format(self.first_name, self.last_name)

  def get_absolute_url(self):
    return reverse("lead_detail", kwargs={"pk":self.pk})
