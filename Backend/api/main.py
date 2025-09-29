from fastapi import FastAPI, Depends, Form, Security, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from .routers import auth_routes
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

app.include_router(auth_routes.router)

