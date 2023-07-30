from ninja import Schema
from enum import Enum

class BaseQueryFilter(Schema):
    def clean_null(self)-> dict:
        """ 
        null value cleaner
        """
        result: dict = {key: value for (key, value) in self.dict().items() if value is not None}
        return {key: value.name if isinstance(value, Enum) else value for key, value in result.items()}        

    
class Color(Enum):
    """ 
    `All available colors options`
    """
    red: str = "Read"
    black: str = "Black"
    green: str = "Green"
    blue: str = "Blue"
    white: str = "White"

class FuelType(Enum):
    """ 
    `All available fuel type options`
    """
    petrol: str = "Petrol"
    diesel: str = "Diesel"

class PaymentMethod(Enum):
    """
    `All available payment options`
    """
    upi = 'UPI'
    cash = 'Cash'
    netbanking = 'NetBanking'

class PaymentStatus(Enum):
    """
    `All available payment status options`
    """
    pending = 'Pending'
    complete = 'Complete'
    failed = 'Failed'