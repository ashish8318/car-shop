from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q

from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import InvalidValue

from ninja import Query, Body, File, Form
from ninja.files import UploadedFile
from ninja.router import Router

import string
import random

from .request import TestDrivePostSChema, TestDriveSchema, UserSignInSchema, UserSchema, UserLoginSchema, \
    UserChangePassword, GoogleSocialAuthSchema, UserUpdateSchema
from utils import AuthBearer, create_access_token, send_mail
from car_shop.settings import GOOGLE_CLIENT_ID
from user.models import TestDrive, UserImage
from car_shop.response import ResponseSchema
from car_shop.logger import logger

router = Router(tags=["User"])

@router.post("test_drive", response = ResponseSchema, auth = AuthBearer())
async def add_test_drive_request(request,
                                payload: TestDrivePostSChema):
    """
    **DB Query to add a request for test drive**
    """
    response: ResponseSchema = ResponseSchema()
    user = await User.objects.filter(username = payload.username, email = payload.email).afirst()
    if user is None:
        response.status_code = 404
        response.description = "nothing found record"
        return response
    test_drive: TestDrive = TestDrive(username = payload.username,
                                      email = payload.email)
    await test_drive.asave()
    response.data.append({'username': test_drive.username, 'email': test_drive.email})
    response.description = "Test Drive Request done."
    response.status_code = 201
    return response

@router.get("test_drive", response = ResponseSchema, auth = AuthBearer())
async def get_test_drive(request,
                         query_filter: TestDriveSchema = Query(...)):
    """
    **DB Query to filter test_drive based on query_filter and Returns records**
    """
    response: ResponseSchema = ResponseSchema()
    data = await response.dict_data(schema_model = TestDriveSchema,
                                    data = TestDrive.objects.filter(**query_filter.clean_null()).all())
    response.data.extend(data)
    return response

@router.patch("test_drive", response = ResponseSchema, auth = AuthBearer())
async def update_test_drive(request,
                            query_filter: TestDriveSchema = Query(...),
                            payload: TestDriveSchema = Body(...)):
    """
    **DB Query to update Test Drive records based on query filter**
    """
    response = ResponseSchema()
    test_drive = TestDrive.objects.filter(**query_filter.clean_null()).all()
    count = await test_drive.aupdate(**payload.dict())
    data = await response.dict_data(schema_model = TestDriveSchema,
                                    data = TestDrive.objects.filter(**query_filter.clean_null()).all())
    response.data.extend(data)
    response.description = f'Total {count} records updated'
    return response

@router.delete("test_drive", response = ResponseSchema, auth = AuthBearer())
async def delete_test_drive(request,
                            query_filter: TestDriveSchema = Query(...)):
    """
    **DB Query to delete test drive based on query filter**
    """
    response = ResponseSchema()
    result = await TestDrive.objects.filter(**query_filter.clean_null()).all().adelete()
    response.description = f'Total {result[0]} record deleted'
    logger.warning(f'Total {result[0]} record deleted')
    return response

@router.post("sign_in", response=ResponseSchema)
async def create_user_account(request,
                              payload: UserSignInSchema = Body(...)):
    """Sign in user

    **DB query to create user account**
    """
    response = ResponseSchema()
    password_reset_token_obj = PasswordResetTokenGenerator()
    payload = payload.dict()
    existing_user = await User.objects.filter(Q(username=payload["username"]) | \
                                              Q(email = payload["email"])).afirst()
    if existing_user is not None:
        response.error.update({"user": "user already exists"})
        response.description = "user already exists"
        response.status_code = 200
        return response
    
    try:
        validate_email(payload["email"])
    except ValidationError as e:
        response.error.update({"email": e.message})
        response.status_code = 400
        return response
    
    user = User(
        username = payload["username"],
        email = payload["email"],
        password = make_password(payload["password"]),
        is_active = False
    )
    await user.asave()
    # Sending email to user to verify email
    mail_status = send_mail(
        subject="Email Verification Link",
        to=[user.email],
        template_message = render_to_string("email_link.html", {
            "uid": urlsafe_base64_encode(force_bytes(user.id)),
            "token": password_reset_token_obj.make_token(user),
            "user": user,
            "domain": get_current_site(request).domain
        })
    )

    if mail_status != 1:
        await user.adelete()
        response.description = "Failed to send verification mail"
        response.error.update({"mail": "Failed to send verification mail"})
        return response
    else:
        data = await response.dict_data(schema_model=UserSchema,
                                        data=User.objects.aget(id=user.id))
        response.data.extend(data)
        response.status_code = 201
        response.description = "user account created"
        return response

@router.post("login", response=ResponseSchema)
async def user_login(request,
                     payload: UserLoginSchema = Body(...)):
    """Login User
    
    **DB query to login user**
    """
    response = ResponseSchema()
    user = await User.objects.filter(email = payload.email).afirst()
    if user is not None:
        if check_password(payload.password, user.password):
            if user.is_active:
                token_payload = {
                    "username": user.username,
                    "email": user.email
                }
                response.data.append(
                    {
                        "accress_token": create_access_token(payload=token_payload),
                        "refresh_token": create_access_token(payload=token_payload,
                                                            type="refresh")
                    }
                )
                return response
            else:
                response.error.update({"is_active": "Please click on verification email link to activate your account"})
                return response
        else:
            response.error.update({"password": "Invalid password provided"})
            return response
    else:
        response.error.update({"email": "Invalid email provided"})
        return response
    
@router.post("refresh_token", response=ResponseSchema, auth=AuthBearer())
async def get_refresh_token(request):
    """Get refresh token

    **DB query to get refresh token**
    """
    response = ResponseSchema()
    if request.auth["type"] == "refresh":
        payload = {
            "username": request.auth["username"],
            "email": request.auth["email"]
        }
        response.data.append(
            {
                "access_token": create_access_token(payload=payload),
                "refresh_token": create_access_token(payload=payload, type="refresh")
            }
        )
        return response
    else:
        response.error.update({"token": "please provide refresh token"})
        return response

@router.post("change_password", response=ResponseSchema)
async def chnage_password(request,
                          payload: UserChangePassword = Body(...)):
    """Change user password
    
    **DB query to change user password**
    """

    response = ResponseSchema()
    user = await User.objects.filter(email = payload.email).afirst()
    if user is not None:
        if payload.password == payload.conform_password:
            user.password = make_password(payload.password)
            await user.asave()
            response.description = "password changed"
            return response
        response.error.update({"password": "password and conform password should be same"})
        return response
    else:
        response.error.update({"email": "Invalid email provided"})
        return response

@router.post("sign/google", response=ResponseSchema)
async def google_sign(request,
                      payload: GoogleSocialAuthSchema = Body(...)):
    """Sign with Google
    
    **Operstion Procress**
    - Takes  access token in post payload
    - Validate access token
    - Get user details from google
    - Returns access_token and refresh_token after successfull google authentication  
    """
    response = ResponseSchema()
    try:
        token_info = id_token.verify_token(payload.token, requests.Request(), GOOGLE_CLIENT_ID)
        # Validating client id
        if GOOGLE_CLIENT_ID == token_info.get("aud"):
            existing_user = await User.objects.filter(Q(username=token_info.get("name")) |
                                            Q(email=token_info.get("email"))).afirst()
            if existing_user is None:
                user = User(
                    username = token_info.get("name"),
                    email = token_info.get("email"),
                    password = make_password(''.join(random.choices(string.ascii_lowercase, k=5)))
                )
                await user.asave()
                existing_user = user
                response.status_code = 201
                response.description = "User successfully sign in with google"

            # Creating token and token payload
            if response.description is None:
                response.description = "User already exist"
            payload = {
                    "username": existing_user.username,
                    "email": existing_user.email
                }
            response.data.append(
                {
                    "access_token": create_access_token(payload=payload),
                    "refresh_token": create_access_token(payload=payload, type="refresh")
            })
            return response
        
        # if client_id not match
        response.description = "oops! who are you"
        return response

    except InvalidValue:
        response.error.update({"token": "token expire please try again"})
        response.description = "token expire"
        return response
    
@router.post("/user", response=ResponseSchema, auth = AuthBearer())
async def update_user_details(request,
                              email: str,
                              payload: UserUpdateSchema = Form(...),
                              avatar: UploadedFile = File(default=None)):
    """Update user details
    
    **DB query to update user details | avatar based on query email provided**
    """
    response = ResponseSchema()
    existing_user = await User.objects.filter(email = email).afirst()
    clean_payload = payload.clean_empty()
    if existing_user is not None:
        if len(clean_payload) != 0:
            if "password" in clean_payload:
                clean_payload["password"] = make_password(clean_payload["password"])
            existing_user.__dict__.update(**clean_payload)
            await existing_user.asave()
        if avatar is not None:
            try:
                user_image = await UserImage.objects.aget(user=existing_user)
                user_image.avatar = avatar
                await user_image.asave()
            except UserImage.DoesNotExist:
                user_image = UserImage(user=existing_user,
                                       avatar=avatar)
                await user_image.asave()
        response.description = "User successfully updated"
        return response
    else:
        response.description = "Nothing find to update user"
        return response
    
@router.get("/user", response=ResponseSchema, auth=AuthBearer())
async def get_user_details(request):
    """Get current logged user details
    
    **DB Query to get current logged user details**
    """
    response = ResponseSchema()
    existing_user = await User.objects.aget(email=request.auth["email"])
    res_dict = dict()
    try:
        user_image = await UserImage.objects.aget(user=existing_user)
        res_dict.update({"url": f"{request.get_host()}{user_image.avatar.url}"})
    except UserImage.DoesNotExist:
        pass

    res_dict.update({
        "user_name": existing_user.username,
        "email": existing_user.email
    })
    response.data.append(res_dict)
    return response

@router.get("/email_verification/{uidb64}/{token}", url_name="email_verification")
async def email_verification(request,
                             uidb64,
                             token):
    """Email Verification link

    **Validate the email after click on verification link on email**
    """
    password_reset_token_obj = PasswordResetTokenGenerator()
    try:
        uuid = force_str(urlsafe_base64_decode(uidb64))
        user = await User.objects.aget(pk = uuid)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        return render(request, "email_verification.html", {"error": True, "message": "Invalid verification link"})
    if password_reset_token_obj.check_token(token=token, user=user):
        user.is_active = True
        await user.asave()
        return render(request, "email_verification.html", {"user": user, "error": False, "message": "Success"})
    else:
        return render(request, "email_verification.html", {"error": True, "message": "Invalid Token given"})
    