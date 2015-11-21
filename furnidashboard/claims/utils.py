from itertools import chain

from django.db.models import Q, F, Max
from claims.models import Claim, ClaimStatus


def get_claims_by_latest_status(status_str=''):
	return Claim.objects.annotate(max_status_dt=Max('claimstatus__date')).filter(
		Q(claimstatus__date=F('max_status_dt')) & Q(claimstatus__status=status_str))


def filter_claims_by_latest_status(qs=None, status_str=''):
	if qs is None:
		qs = Claim.objects.all()
	return qs.annotate(max_status_dt=Max('claimstatus__date')).filter(
		Q(claimstatus__date=F('max_status_dt')) & Q(claimstatus__status=status_str))


def get_claims_with_missing_status():
	claims_no_status = Claim.objects.filter(claimstatus__isnull=True)
	claims_no_status_upd = Claim.objects.annotate(max_status_dt=Max('claimstatus__date')).filter(
		Q(claimstatus__date=F('max_status_dt')) & Q(claimstatus__status='NEW'))
	return list(chain(claims_no_status, claims_no_status_upd))


def get_claim_latest_status_and_date(claim):
	latest_status = claim.claimstatus_set.all()[0]
	return latest_status.status, latest_status.date
