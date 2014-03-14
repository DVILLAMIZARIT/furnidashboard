from django.db import models

class Store(models.Model):
  """
  A class model representing the store information
  """
  name = models.TextField(max_length=125)

  class Meta:
    db_table = "stores"

  def __unicode__(self):
    return self.name

