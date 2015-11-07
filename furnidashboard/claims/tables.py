import django_tables2 as tables
from django_tables2.utils import A #accessor
from claims.models import Claim
from core.tables import CustomTextLinkColumn

class ClaimsTable(tables.Table):
  pk = CustomTextLinkColumn('claim_detail', args=[A('pk')], custom_text="Open", orderable=False, verbose_name="Actions")

  class Meta:
    model = Claim
    attrs = {"class":"paleblue"}
    fields = ("claim_date", "claim_desc", "delivery_date", "item_origin", "amount") 
