from django_extensions.db.models import TimeStampedModel
from audit_log.models import AuthStampedModel

class Claim(TimeStampedModel, AuthStampedModel):
    """
    A model class representing the Claim information for sold orders/items
    """
    
    CLAIM_STATUSES = (
                      ('NEW', 'New'),
                      ('SUBMITTED', 'Submitted'),
                      ('AUTHORIZED', 'Authorized'),
                      ('FUNDED', 'Funded'),
                      ('RECEIVED', 'Received'),
                      ('CANCELLED', 'Cancelled'),
                      
                    )
    
    PAID_BY_CHOICES = (
                       ('NTZ', 'Natuzzi'),
                       ('FURN', 'Furnitalia'),
                       ('CUST', 'Customer'),
                    )
    