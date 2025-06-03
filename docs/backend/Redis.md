# Redis: Almacenamiento en Caché para Aplicaciones de Alto Rendimiento

## ¿Qué es Redis?

Redis (Remote Dictionary Server) es una estructura de datos en memoria de código abierto que funciona como base de 
datos, caché y broker de mensajes. Es extremadamente rápido debido a su naturaleza en memoria y soporta diversos 
tipos de estructuras de datos como strings, hashes, listas, conjuntos, conjuntos ordenados, bitmaps, hyperloglogs, 
streams y más.

## ¿Por qué usar Redis?

- **Velocidad superior**: Operaciones en microsegundos por estar en memoria
- **Estructuras de datos versátiles**: Va más allá del simple par clave-valor
- **Persistencia opcional**: Puede guardar datos en disco para recuperación
- **Replicación y alta disponibilidad**: Mediante Redis Sentinel o Redis Cluster
- **Atomicidad**: Operaciones atómicas que evitan condiciones de carrera
- **Ampliamente adoptado**: Comunidad activa y múltiples clientes para diversos lenguajes

## Estructura en nuestro proyecto

```
app/
├── core/
│   └── cache.py      # Configuración y utilidades de Redis
├── services/
│   └── cache_service.py  # Servicio para manejar operaciones de caché
```

## Configuración básica

```python
# app/core/cache.py
import json
from typing import Any, Optional, Union

import redis
from fastapi import Depends

from app.core.config import settings

# Crear el pool de conexiones Redis
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def get_redis_client():
    """Dependencia para obtener un cliente Redis"""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        # No es necesario cerrar la conexión ya que se gestiona mediante el pool
        pass

class RedisCache:
    def __init__(self, client: redis.Redis = Depends(get_redis_client)):
        self.client = client
        self.default_expiry = 3600  # 1 hora por defecto

    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Almacena un valor en caché con tiempo de expiración opcional"""
        expiry = expire if expire is not None else self.default_expiry
        
        if not isinstance(value, (str, bytes, int, float)):
            value = json.dumps(value)
            
        return self.client.set(key, value, ex=expiry)

    def get(self, key: str) -> Optional[Any]:
        """Recupera un valor de la caché"""
        value = self.client.get(key)
        
        if value is None:
            return None
            
        try:
            # Intentar deserializar JSON
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            # Si no es JSON, devolver como está
            return value

    def delete(self, key: str) -> int:
        """Elimina una clave de la caché"""
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Verifica si una clave existe en la caché"""
        return bool(self.client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """Establece el tiempo de expiración de una clave"""
        return self.client.expire(key, seconds)
```

## Implementación del servicio de caché

```python
# app/services/cache_service.py
from typing import Any, Dict, List, Optional, TypeVar, Generic
from fastapi import Depends

from app.core.cache import RedisCache

T = TypeVar('T')

class CacheService(Generic[T]):
    """Servicio genérico para gestionar caché por dominio"""
    
    def __init__(
        self, 
        cache: RedisCache = Depends(),
        prefix: str = "cache",
        expiry: int = 3600
    ):
        self.cache = cache
        self.prefix = prefix
        self.expiry = expiry
    
    def _get_key(self, key: str) -> str:
        """Genera una clave con prefijo para el dominio específico"""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> Optional[T]:
        """Obtiene un objeto de la caché"""
        return self.cache.get(self._get_key(key))
    
    def set(self, key: str, value: T, expire: int = None) -> bool:
        """Almacena un objeto en la caché"""
        return self.cache.set(
            self._get_key(key),
            value,
            expire or self.expiry
        )
    
    def delete(self, key: str) -> bool:
        """Elimina un objeto de la caché"""
        return bool(self.cache.delete(self._get_key(key)))
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalida todas las claves que coincidan con el patrón"""
        keys = self.cache.client.keys(f"{self.prefix}:{pattern}")
        if not keys:
            return 0
        return self.cache.client.delete(*keys)
```

## Integrando Redis con el patrón Repository

Redis se puede integrar con nuestro patrón Repository para cachear consultas frecuentes:

```python
# app/repositories/product_repository.py
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(
            self,
            db: Session = Depends(get_db),
            cache: CacheService = Depends(lambda: CacheService(prefix="product"))
    ):
        super().__init__(Product, db)
        self.cache = cache

    def get(self, id: int) -> Optional[Product]:
        # Intentar obtener de caché primero
        cache_key = f"id:{id}"
        cached_product = self.cache.get(cache_key)

        if cached_product:
            # Convertir diccionario cacheado a objeto SQLAlchemy
            return self.model(**cached_product)

        # Si no está en caché, obtener de la base de datos
        product = super().get(id)

        if product:
            # Cachear para futuras consultas
            self.cache.set(cache_key, product.__dict__)

        return product

    def get_by_name(self, name: str) -> Optional[Product]:
        cache_key = f"name:{name}"
        cached_product = self.cache.get(cache_key)

        if cached_product:
            return self.model(**cached_product)

        product = self.db.query(self.model).filter(self.model.name == name).first()

        if product:
            self.cache.set(cache_key, product.__dict__)

        return product

    def create(self, *, obj_in: ProductCreate) -> Product:
        product = super().create(obj_in=obj_in)
        # Invalidar caché de listas
        self.cache.invalidate_by_pattern("list:*")
        return product

    def update(self, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        product = super().update(db_obj=db_obj, obj_in=obj_in)
        # Invalidar caché individual y listas
        self.cache.delete(f"id:{product.id}")
        self.cache.delete(f"name:{product.name}")
        self.cache.invalidate_by_pattern("list:*")
        return product

    def remove(self, *, id: int) -> Product:
        product = super().remove(id=id)
        # Invalidar caché
        self.cache.delete(f"id:{id}")
        self.cache.delete(f"name:{product.name}")
        self.cache.invalidate_by_pattern("list:*")
        return product

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[Product]:
        cache_key = f"list:skip{skip}:limit{limit}"
        cached_list = self.cache.get(cache_key)

        if cached_list:
            # Convertir lista de diccionarios a objetos
            return [self.model(**item) for item in cached_list]

        products = super().get_multi(skip=skip, limit=limit)

        if products:
            # Cachear lista de productos
            self.cache.set(
                cache_key,
                [product.__dict__ for product in products]
            )

        return products
```

## Casos de uso con Redis en el sistema de inventario

### 1. Caché de productos populares

```python
# app/services/product_service.py
from typing import List
from fastapi import Depends

from app.repositories.product_repository import ProductRepository
from app.services.cache_service import CacheService
from app.models.product import Product

class ProductService:
    def __init__(
        self,
        repository: ProductRepository = Depends(),
        cache: CacheService = Depends(lambda: CacheService(prefix="product_service"))
    ):
        self.repository = repository
        self.cache = cache
    
    def get_popular_products(self, limit: int = 10) -> List[Product]:
        """Obtiene los productos más populares (frecuentemente consultados)"""
        cache_key = f"popular:limit{limit}"
        cached_products = self.cache.get(cache_key)
        
        if cached_products:
            return [Product(**p) for p in cached_products]
        
        # En un caso real, esto podría ser una consulta compleja que cuente ventas
        popular_products = self.repository.db.query(Product)\
            .order_by(Product.views.desc())\
            .limit(limit)\
            .all()
            
        if popular_products:
            self.cache.set(
                cache_key,
                [p.__dict__ for p in popular_products],
                expire=1800  # 30 minutos
            )
            
        return popular_products
```

### 2. Bloqueo distribuido para operaciones críticas

```python
# app/core/distributed_lock.py
import time
import uuid
from typing import Optional, Callable, Any

from redis import Redis

class RedisLock:
    """Implementación de bloqueo distribuido con Redis"""
    
    def __init__(self, redis_client: Redis, lock_name: str, timeout: int = 10):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.lock_id = str(uuid.uuid4())
    
    def acquire(self, blocking: bool = True, retry_delay: float = 0.1) -> bool:
        """Adquiere el bloqueo"""
        end_time = time.time() + self.timeout if blocking else time.time()
        
        while True:
            # Intentar adquirir el bloqueo con NX (solo si no existe)
            if self.redis.set(self.lock_name, self.lock_id, ex=self.timeout, nx=True):
                return True
                
            if not blocking or time.time() > end_time:
                return False
                
            time.sleep(retry_delay)
    
    def release(self) -> bool:
        """Libera el bloqueo solo si es propietario"""
        # Script Lua para asegurar atomicidad
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        return bool(self.redis.eval(script, 1, self.lock_name, self.lock_id))
    
    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"No se pudo adquirir el bloqueo: {self.lock_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
```

Ejemplo de uso para actualización de stock:

```python
# app/services/inventory_service.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import redis

from app.db.database import get_db
from app.core.cache import get_redis_client
from app.core.distributed_lock import RedisLock
from app.repositories.product_repository import ProductRepository


class InventoryService:
    def __init__(
            self,
            db: Session = Depends(get_db),
            redis_client: redis.Redis = Depends(get_redis_client),
            repository: ProductRepository = Depends()
    ):
        self.db = db
        self.redis = redis_client
        self.repository = repository

    def update_stock(self, product_id: int, quantity: int) -> bool:
        """Actualiza el stock de un producto con bloqueo distribuido"""
        lock_name = f"inventory:product:{product_id}"

        with RedisLock(self.redis, lock_name, timeout=30) as lock:
            # Ahora tenemos un bloqueo exclusivo para este producto
            product = self.repository.get(id=product_id)

            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            if product.stock + quantity < 0:
                raise HTTPException(status_code=400, detail="Stock insuficiente")

            # Actualizar stock
            product.stock += quantity
            self.repository.update(db_obj=product, obj_in={"stock": product.stock})

            # La operación ha sido exitosa
            return True
```

### 3. Contador de vistas de productos

```python
# app/api/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis

from app.core.cache import get_redis_client
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Product

router = APIRouter()

@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    repository: ProductRepository = Depends(),
    redis: Redis = Depends(get_redis_client)
):
    product = repository.get(id=product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Incrementar contador de vistas usando Redis
    redis.incr(f"product_views:{product_id}")
    
    # Actualizar contador en base de datos periódicamente
    view_count = int(redis.get(f"product_views:{product_id}") or 0)
    
    # Si el contador ha aumentado en 10, actualizar la BD
    if view_count % 10 == 0:
        product.views = view_count
        repository.update(db_obj=product, obj_in={"views": view_count})
    
    return product
```

## Patrones comunes con Redis

### 1. Caché de resultados de consultas (Cacheo de lado del servidor)

```python
# app/core/decorators.py
import functools
import inspect
import json
from typing import Any, Callable

from app.core.cache import RedisCache

def cached(prefix: str, expire: int = 3600):
    """Decorador para cachear resultados de funciones"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Obtenemos una instancia de RedisCache
            # Esto asume que RedisCache está disponible como servicio
            cache = kwargs.get("cache")
            
            if not cache:
                # Si no se proporciona caché, no aplicamos caché
                return await func(*args, **kwargs)
            
            # Construir clave basada en argumentos
            key_parts = [prefix, func.__name__]
            
            # Añadir args a la clave
            for arg in args:
                if hasattr(arg, "id"):  # Para objetos con ID
                    key_parts.append(f"id:{arg.id}")
                else:
                    key_parts.append(str(arg))
            
            # Añadir kwargs a la clave
            for k, v in sorted(kwargs.items()):
                if k != "cache":  # Excluir el objeto cache
                    key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(key_parts)
            
            # Intentar obtener de caché
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función si no está en caché
            result = await func(*args, **kwargs)
            
            # Cachear resultado
            if result is not None:
                cache.set(cache_key, result, expire)
            
            return result
            
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Versión síncrona del wrapper
            cache = kwargs.get("cache")
            
            if not cache:
                return func(*args, **kwargs)
            
            # Construir clave como en async_wrapper
            key_parts = [prefix, func.__name__]
            
            for arg in args:
                if hasattr(arg, "id"):
                    key_parts.append(f"id:{arg.id}")
                else:
                    key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                if k != "cache":
                    key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(key_parts)
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, expire)
            
            return result
        
        # Determinar si la función es asíncrona
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
```

### 2. Limitación de tasa (Rate Limiting)

```python
# app/core/rate_limit.py
from datetime import datetime
from typing import Tuple

from fastapi import Depends, HTTPException, status
from redis import Redis

from app.core.cache import get_redis_client

class RateLimiter:
    """Limitador de tasa basado en Redis"""
    
    def __init__(
        self,
        redis_client: Redis = Depends(get_redis_client),
        prefix: str = "ratelimit:",
        max_requests: int = 100,
        window: int = 60  # Ventana en segundos
    ):
        self.redis = redis_client
        self.prefix = prefix
        self.max_requests = max_requests
        self.window = window
    
    def _get_key(self, identifier: str) -> str:
        """Genera la clave para el identificador"""
        return f"{self.prefix}{identifier}"
    
    def check(self, identifier: str) -> Tuple[bool, int]:
        """
        Comprueba si el identificador está dentro de los límites
        
        Returns:
            Tuple[bool, int]: (allowed, remaining_requests)
        """
        key = self._get_key(identifier)
        
        # Obtener conteo actual
        count = self.redis.get(key)
        
        if count is None:
            # Primera solicitud en esta ventana
            self.redis.set(key, 1, ex=self.window)
            return True, self.max_requests - 1
        
        # Incrementar contador si está por debajo del límite
        count = int(count)
        if count < self.max_requests:
            self.redis.incr(key)
            return True, self.max_requests - count - 1
        
        # Obtener tiempo restante para reset
        ttl = self.redis.ttl(key)
        
        # Devolver falso si se excede el límite
        return False, 0
```

Implementación como dependencia de FastAPI:

```python
# app/api/deps.py
from fastapi import Depends, Header, HTTPException, status
from typing import Optional

from app.core.rate_limit import RateLimiter

def rate_limit(
    x_forwarded_for: Optional[str] = Header(None),
    rate_limiter: RateLimiter = Depends()
):
    """Dependencia para limitar tasa de solicitudes"""
    # Usar IP del cliente o un valor por defecto
    ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else "unknown"
    
    allowed, remaining = rate_limiter.check(ip)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes, intente nuevamente más tarde",
            headers={"Retry-After": "60", "X-RateLimit-Remaining": "0"}
        )
    
    # Configurar encabezados de límite de tasa
    headers = {"X-RateLimit-Remaining": str(remaining)}
    
    # La dependencia no devuelve ningún valor, solo verifica el límite
    return headers
```

### 3. Cache en dos niveles (memoria volátil + persistente)

```python
# app/core/tiered_cache.py
import json
from typing import Any, Dict, Optional

from fastapi import Depends
from redis import Redis

from app.core.cache import get_redis_client

class TieredCache:
    """
    Implementación de caché en dos niveles:
    - Nivel 1: Caché en memoria (para respuesta ultrarrápida)
    - Nivel 2: Redis (para persistencia y escala)
    """
    
    def __init__(self, redis_client: Redis = Depends(get_redis_client)):
        self.redis = redis_client
        self.memory_cache: Dict[str, Any] = {}
        self.memory_expiry: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor de la caché, buscando primero en memoria"""
        # Comprobar memoria primero
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Si no está en memoria, buscar en Redis
        value = self.redis.get(key)
        if value is None:
            return None
        
        try:
            # Intentar deserializar desde JSON
            data = json.loads(value)
            
            # Actualizar caché en memoria
            self.memory_cache[key] = data
            
            return data
        except (json.JSONDecodeError, TypeError):
            # Si no es JSON, devolver como está
            self.memory_cache[key] = value
            return value
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Almacena un valor en ambos niveles de caché"""
        # Guardar en memoria
        self.memory_cache[key] = value
        
        # Preparar valor para Redis
        redis_value = value
        if not isinstance(value, (str, bytes, int, float)):
            redis_value = json.dumps(value)
        
        # Guardar en Redis
        return self.redis.set(key, redis_value, ex=expire)
    
    def delete(self, key: str) -> bool:
        """Elimina una clave de ambos niveles de caché"""
        # Eliminar de memoria
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Eliminar de Redis
        return bool(self.redis.delete(key))
    
    def clear_memory_cache(self) -> None:
        """Limpia solo la caché en memoria"""
        self.memory_cache.clear()
```

## Mejores prácticas

1. **Claves estructuradas**: Utilizar prefijos y separadores para organizar claves por dominio
   ```python
   "product:123:details"  # Detalles del producto 123
   "order:456:items"      # Ítems del pedido 456
   "user:789:preferences" # Preferencias del usuario 789
   ```

2. **Expiración adecuada**: Establecer TTL (time-to-live) apropiado según la frecuencia de cambio de los datos
   ```python
   # Datos que cambian con frecuencia
   cache.set("products:trending", trending_products, expire=300)  # 5 minutos
   
   # Datos relativamente estables
   cache.set("products:categories", categories, expire=86400)  # 1 día
   ```

3. **Invalidación de caché**: Invalidar caché cuando los datos subyacentes cambian
   ```python
   # Al actualizar un producto
   def update_product(product_id, data):
       # Actualizar en base de datos
       product = update_in_db(product_id, data)
       
       # Invalidar caché relacionada
       cache.delete(f"product:{product_id}")
       cache.delete("products:list")
       cache.delete("products:trending")
       
       return product
   ```

4. **Serialización eficiente**: Usar formatos compactos como JSON o MessagePack
   ```python
   import msgpack
   
   def set_compressed(key, value, expire=None):
       compressed = msgpack.packb(value)
       return redis.set(key, compressed, ex=expire)
   
   def get_compressed(key):
       data = redis.get(key)
       if data:
           return msgpack.unpackb(data)
       return None
   ```

5. **Persistencia configurada apropiadamente**: Configurar RDB o AOF según necesidades
   ```
   # Configuración en redis.conf
   save 900 1       # Guardar si al menos 1 clave cambia en 15 minutos
   save 300 10      # Guardar si al menos 10 claves cambian en 5 minutos
   save 60 10000    # Guardar si al menos 10000 claves cambian en 1 minuto
   ```

6. **Monitoreo**: Implementar monitoreo de uso de memoria y tasa de aciertos
   ```python
   def get_cache_stats():
       info = redis.info()
       return {
           "used_memory": info["used_memory_human"],
           "hit_rate": info["keyspace_hits"] / (info["keyspace_hits"] + info["keyspace_misses"]),
           "uptime_days": info["uptime_in_days"]
       }
   ```

## Escenarios para el sistema de inventario

1. **Caché de productos populares o recién vistos**
2. **Almacenamiento de sesiones de usuario**
3. **Control de stock en tiempo real durante compras simultáneas**
4. **Agregación de estadísticas (vistas, ventas, búsquedas)**
5. **Limitación de tasa para prevenir abuso de API**
6. **Cola de trabajos para procesamiento asíncrono de pedidos**
7. **Bloqueo distribuido para operaciones críticas de inventario**

## Configuración en Docker

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ..
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - MYSQL_SERVER=db
      - REDIS_HOST=redis
      - REDIS_PORT=6379

  db:
    image: mysql:8
    # ...configuración de MySQL...

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```