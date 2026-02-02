"""
Auth API Endpoints
Handles HTTP requests for authentication operations
"""
from fastapi import APIRouter, HTTPException, status

from services.auth.src.core.dependencies import DBSession
from services.auth.src.domain.user import (
    DomainError, ValidationError, InvalidEmail, WeakPassword,
    UserExists, InvalidCredentials, UserNotFound, VerificationFailed
)
from services.auth.src.schemas import (
    UserRegister, UserLogin, VerifyEmail, RefreshTokenRequest,
    RegisterResponse, LoginResponse, VerifyEmailResponse, TokenResponse, UserOut
)
from services.auth.src.services import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


def user_orm_to_schema(user_orm) -> UserOut:
    """Convert UserORM to UserOut schema"""
    return UserOut(
        id=user_orm.id,
        email=user_orm.email,
        role=user_orm.role,
        is_verified=user_orm.is_verified,
        created_at=user_orm.created_at,
        updated_at=user_orm.updated_at,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create new user account and send verification email",
)
def register(
    data: UserRegister,
    db: DBSession,
):
    """
    Register a new user account.

    **Request body:**
    - `email`: Valid email address
    - `password`: Min 8 chars, must include uppercase, lowercase, and digit
    - `role`: "user" or "partner" (default: "user")

    **Response:**
    - User details
    - Verification email sent (check inbox and spam folder)

    **Errors:**
    - 400: Invalid email or weak password
    - 409: User with this email already exists
    """
    try:
        service = AuthService(db)
        user_orm, message = service.register(
            email=data.email.lower(),
            password=data.password,
            role=data.role,
        )

        return RegisterResponse(
            user=user_orm_to_schema(user_orm),
            message=message,
        )

    except UserExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except (InvalidEmail, WeakPassword, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return tokens",
)
def login(
    data: UserLogin,
    db: DBSession,
):
    """
    Login with email and password.

    **Request body:**
    - `email`: User's email
    - `password`: User's password

    **Response:**
    - User details
    - Access token (15 min expiry)
    - Refresh token (7 day expiry)

    **Errors:**
    - 401: Invalid credentials
    """
    try:
        service = AuthService(db)
        user_orm, access_token, refresh_token = service.login(
            email=data.email.lower(),
            password=data.password,
        )

        return LoginResponse(
            user=user_orm_to_schema(user_orm),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=15 * 60,  # 15 minutes in seconds
            ),
        )

    except InvalidCredentials as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email address",
    description="Confirm email with verification token sent to inbox",
)
def verify_email(
    data: VerifyEmail,
    db: DBSession,
):
    """
    Verify user's email address using token from verification email.

    **Request body:**
    - `token`: Verification token from email link

    **Response:**
    - Confirmation message
    - Updated user details

    **Errors:**
    - 400: Invalid or expired token
    """
    try:
        service = AuthService(db)
        user_orm = service.verify_email(data.token)

        return VerifyEmailResponse(
            message="Email verified successfully",
            user=user_orm_to_schema(user_orm),
        )

    except VerificationFailed as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
def refresh_token(
    data: RefreshTokenRequest,
    db: DBSession,
):
    """
    Get new access token using refresh token.

    Use this when access token expires to get a new one without re-logging in.

    **Request body:**
    - `refresh_token`: Refresh token from login/register

    **Response:**
    - New access token
    - Refresh token (may be rotated)

    **Errors:**
    - 401: Invalid or expired refresh token
    """
    try:
        service = AuthService(db)
        new_access_token, new_refresh_token = service.refresh_access_token(
            data.refresh_token
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=15 * 60,  # 15 minutes in seconds
        )

    except InvalidCredentials as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get authenticated user's profile",
)
def get_current_user_profile(
    db: DBSession,
):
    """
    Get current authenticated user's profile.

    **Headers required:**
    - `Authorization: Bearer <access_token>`

    **Response:**
    - User profile details

    **Errors:**
    - 401: Missing or invalid token
    """
    # This endpoint would require auth, but for now it's a placeholder
    # The actual auth check is done by FastAPI dependencies
    raise HTTPException(
        status_code=501,
        detail="This endpoint requires auth dependency to be integrated"
    )
