import django_tables2 as tables
from django_tables2.utils import A
from claims.models import Claim
from core.tables import CustomTextLinkColumn, TruncateTextColumn


class ClaimsTable(tables.Table):
    pk = CustomTextLinkColumn('claim_detail', args=[A('pk')], custom_text="View detail", orderable=False,
                              verbose_name="Actions")
    claim_desc = TruncateTextColumn(trunc_length=30, verbose_name="Description")

    class Meta:
        model = Claim
        attrs = {"class": "paleblue"}
        fields = (
            "claim_date", "claim_desc", "delivery_date", "item_origin", "amount", "paid_by", "vendor_claim_no",
            "customer", "order_ref", "order_invoice_num", "repair_tech")
