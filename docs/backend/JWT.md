# JWT (JSON Web Tokens): Autenticación y Autorización

## ¿Qué es JWT?

JWT (JSON Web Tokens) es un estándar abierto (RFC 7519) que define una forma compacta y autónoma para transmitir 
información de manera segura entre partes como un objeto JSON. Esta información puede ser verificada y confiable 
porque está firmada digitalmente. Los JWT pueden ser firmados usando un secreto (con algoritmo HMAC) o un par de 
claves pública/privada (usando RSA o ECDSA).

## ¿Por qué usar JWT?

- **Autocontenido**: Contiene toda la información necesaria sin consultar la base de datos
- **Compacto**: Puede ser enviado a través de URL, parámetros POST o en cabeceras HTTP
- **Seguro**: Firmado digitalmente para garantizar integridad
- **Stateless**: Ideal para arquitecturas sin estado como las APIs REST
- **Interoperable**: Funciona bien entre diferentes lenguajes y frameworks

## Estructura de un JWT

Un JWT consta de tres partes separadas por puntos:
`xxxxx.yyyyy.zzzzz`

1. **Header**: Contiene el tipo de token y el algoritmo de firma
2. **Payload**: Contiene las claims (información del usuario y metadatos)
3. **Signature**: La firma que verifica la autenticidad del token

```
header.payload.signature
```

## Implementación en nuestro proyecto FastAPI

### 1. Configuración básica

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 2. Creación de dependencias para autenticación

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return current_user
```

### 3. Endpoints de autenticación

```python
# app/api/endpoints/auth.py
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
        db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Obtiene un token de acceso JWT usando credenciales de usuario.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email o contraseña incorrectos",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email o contraseña incorrectos",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
```

### 4. Esquemas Pydantic para autenticación

```python
# app/schemas/token.py
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
```

## Protección de rutas en FastAPI

Una vez implementado JWT, podemos proteger nuestras rutas:

```python
# app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_active_user, get_current_admin_user
from app.db.database import get_db
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Product, ProductCreate, ProductUpdate

router = APIRouter()


@router.get("/", response_model=List[Product])
def get_products(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user)  # Requiere usuario autenticado
):
    """
    Obtener lista de productos.
    """
    product_repo = ProductRepository(db)
    return product_repo.get_multi(skip=skip, limit=limit)


@router.post("/", response_model=Product)
def create_product(
        *,
        db: Session = Depends(get_db),
        product_in: ProductCreate,
        current_user: User = Depends(get_current_admin_user)  # Requiere usuario administrador
):
    """
    Crear nuevo producto (solo admin).
    """
    product_repo = ProductRepository(db)
    return product_repo.create(obj_in=product_in)
```

## Integración con React Frontend

### 1. Configuración de autenticación en el frontend

```tsx
// src/services/auth.ts
import axios from 'axios';
import { API_URL } from '../config';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  // FormData para compatibilidad con OAuth2PasswordRequestForm en FastAPI
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await axios.post<AuthResponse>(`${API_URL}/auth/login`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  // Guardar token en localStorage
  localStorage.setItem('token', response.data.access_token);
  
  return response.data;
};

export const logout = (): void => {
  localStorage.removeItem('token');
};

export const getToken = (): string | null => {
  return localStorage.getItem('token');
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};
```

### 2. Cliente Axios con interceptor para JWT

```tsx
// src/services/api.ts
import axios from 'axios';
import { getToken } from './auth';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor para añadir token JWT a todas las solicitudes
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redireccionar a login si el token es inválido o ha expirado
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Consideraciones de seguridad

1. **Almacenamiento seguro**:
    - El secreto JWT (`SECRET_KEY`) debe ser complejo y mantenerse seguro
    - No almacenar información sensible en el payload (visible para cualquiera)

2. **Configuración de expiración**:
    - Establecer tiempos de expiración cortos (minutos a horas, no días)
    - Implementar rotación de tokens con refresh tokens para sesiones prolongadas

3. **Protección contra ataques**:
    - Usar HTTPS para evitar interceptación
    - Implementar lista negra de tokens revocados (con Redis)
    - Validar claims como `iss` (emisor) y `aud` (audiencia)

4. **Consideraciones de almacenamiento en frontend**:
    - Preferir `httpOnly cookies` sobre `localStorage` cuando sea posible
    - Implementar protección XSS en la aplicación React

## Mejores prácticas

1. **Estructura de tokens**:
    - Mantener tokens pequeños (menos información en payload)
    - Incluir solo información relevante (ID de usuario, roles, etc.)

2. **Gestión de tokens**:
    - Implementar revocación de tokens (lista negra con Redis)
    - Considerar tokens de refresco para experiencias de usuario prolongadas

3. **Autorización granular**:
    - Incluir roles/permisos en el token para decisiones de autorización rápidas
    - Crear middlewares/dependencias específicas para diferentes niveles de acceso

4. **Manejo de errores**:
    - Proporcionar mensajes de error claros pero no revelar información sensible
    - Responder con códigos HTTP apropiados (401, 403)

## Ejemplo completo de flujo de autenticación

1. **Usuario inicia sesión**: Frontend envía credenciales al endpoint `/auth/login`
2. **Backend verifica credenciales**: Comprueba usuario/contraseña y genera JWT
3. **Frontend almacena token**: Guarda JWT en localStorage o cookie
4. **Frontend incluye token**: Añade JWT en header Authorization en cada solicitud
5. **Backend valida token**: Verifica firma y claims en cada solicitud protegida
6. **Backend autoriza acceso**: Permite o deniega acceso basado en permisos del usuario