import os
import jwt
import datetime
from ninja.errors import HttpError
from ninja.security import HttpBearer

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            decoded_data = jwt.decode(jwt=token,
                           key=os.environ.get("JWT_SECRET_KEY"),
                           algorithms=os.environ.get("JWT_ALGORITHM"))
        except jwt.DecodeError:
            raise HttpError(status_code=400, message=f"failed to decode token")
        except jwt.ExpiredSignatureError:
            raise HttpError(status_code=400, message="token expire please try again")
        return decoded_data

def get_token(payload: dict):
    """returns token"""
    
    return jwt.encode(
            payload=payload,
            key=os.environ.get("JWT_SECRET_KEY"),
            algorithm=os.environ.get("JWT_ALGORITHM")
        )

def create_access_token(payload: dict,
                        type: str = "access"):
    """
    Genetare JWT access token
    """
    if type == "access":
        payload["exp"] = datetime.datetime.utcnow() + \
                            datetime.timedelta(seconds=int(os.environ.get("JWT_EXPIRES")))
        payload["type"] = "access"
        return get_token(payload=payload)
    else:
        payload["type"] = "refresh"
        payload["exp"] = datetime.datetime.utcnow() + \
                            datetime.timedelta(seconds=int(os.environ.get("JWT_EXPIRES")) + \
                            int(os.environ.get("REFRESH_EXPIRE")))
        return get_token(payload=payload)
    
def send_mail(subject: str,
              to: list,
              cc: list = None,
              bcc: list = None,
              template_message: str = None,
              body_message: str = None)-> int:
    """
    Send mail helper functions
    """
    mail = EmailMessage(
        subject=subject,
        to=to,
        cc= cc if cc is not None else None,
        bcc= bcc if bcc is not None else None,
        body= template_message if template_message is not None else body_message,
    )

    mail_status: int = mail.send(
        fail_silently=True
    )
    return mail_status