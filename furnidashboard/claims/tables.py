import django_tables2 as tables
from django.utils import formats
from django_tables2.utils import A
from claims.models import Claim
from core.tables import CustomTextLinkColumn, TruncateTextColumn


class ClaimsTable(tables.Table):
	pk = CustomTextLinkColumn('claim_detail', args=[A('pk')], custom_text="View detail", orderable=False,
                              verbose_name="Actions")
	claim_desc = TruncateTextColumn(trunc_length=30, verbose_name="Description")
	claim_date = tables.TemplateColumn('{{ record.claim_date|date:\'m/d/Y\'}}', verbose_name="Claim Date")
	status = tables.Column(verbose_name="Current Status", empty_values=())
	status_date = tables.Column(verbose_name="Status Date", empty_values=())

	def render_status(self, record):
		status = ''
		status_records = list(record.claimstatus_set.all())
		if len(status_records):
			status = status_records[0].get_status_display()
		return "%s" % status

	def render_status_date(self, record):
		status_date = ''
		status_records = list(record.claimstatus_set.all())
		if len(status_records):
			status_date = formats.date_format(status_records[0].date, 'DATE_FORMAT_STANDARD')
		return "%s" % status_date

	class Meta:
		model = Claim
		attrs = {"class": "paleblue"}
		fields = (
			"claim_date", "customer", "claim_desc", "item_origin", "amount", "paid_by", "vendor_claim_no",
			 "order_ref", "status", "status_date")
