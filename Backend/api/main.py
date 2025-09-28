from fastapi import FastAPI, Depends, Form, Security, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from .repository.schemas.keycloak import TokenResponse, UserInfo
from .core.controller import AuthController
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger("rbac_keycloak")
logging.basicConfig(level=logging.INFO)


# Define OAuth2 password flow for OpenAPI so Swagger UI can use the /login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Initialize the FastAPI app 
app = FastAPI()

# CORS: allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)



@app.get("/")
async def read_root():
    """
    Root endpoint that provides a welcome message and documentation link.
    """
    return AuthController.read_root()



@app.post("/login", response_model=TokenResponse)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to authenticate the user and return an access token.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The password of the user.

    Returns:
        TokenResponse: Contains the access token upon successful authentication.
    """
    
    token_resp = AuthController.login(form_data.username, form_data.password)
  
    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
    )
    return token_resp


@app.post("/login/json", response_model=TokenResponse)
async def login_json(response: Response, payload: dict):
    """Login endpoint that accepts JSON {username, password} for SPA clients."""
    username = payload.get("username")
    password = payload.get("password")
    token_resp = AuthController.login(username, password)
    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
    )
    return token_resp



async def get_token(request: Request) -> str:
    """Try to get token from Authorization header, fallback to cookie or query param."""
  
    try:
        token = await oauth2_scheme(request)
        return token
    except Exception:
      
        token = request.cookies.get("access_token")
        if token:
            return token
       
        token = request.query_params.get("access_token")
        if token:
            return token
   
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/protected", response_model=UserInfo)
async def protected_endpoint(
    request: Request,
    token: str = Depends(get_token),
):
    """
    Protected endpoint that requires a valid token for access.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token provided via HTTP Authorization header.

    Returns:
        UserInfo: Information about the authenticated user.
    """
  
    auth_header = request.headers.get("authorization")
    logger.info(f"Protected endpoint called. Authorization header: {auth_header}")
    logger.info(f"Resolved token from dependency: {token[:30]}{'...' if len(token) > 30 else ''}")

    return AuthController.protected_endpoint(token)