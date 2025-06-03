# Axios: Cliente HTTP para React

## ¿Qué es Axios?

Axios es una biblioteca cliente HTTP basada en promesas para el navegador y Node.js. Proporciona una API simple 
para realizar solicitudes HTTP desde aplicaciones JavaScript/TypeScript, facilitando la comunicación con APIs REST
como nuestro backend FastAPI.

## ¿Por qué usar Axios?

- **Basado en Promesas**: Soporta async/await para código más limpio y legible
- **Interceptores**: Permite modificar solicitudes y respuestas globalmente
- **Transformación automática**: Convierte datos JSON automáticamente
- **Cancelación de solicitudes**: Permite cancelar peticiones en curso
- **Protección CSRF**: Incluye protección contra falsificación de solicitudes
- **Soporte para progreso de carga**: Útil para cargas de archivos
- **Compatibilidad con TypeScript**: Tipado estático para reducir errores

## Configuración en nuestro proyecto

### Estructura de archivos

```
src/
├── api/
│   ├── axios.ts          # Configuración base de Axios
│   ├── products.ts       # Endpoints relacionados con productos
│   ├── customers.ts      # Endpoints relacionados con clientes
│   └── orders.ts         # Endpoints relacionados con pedidos
```

### Configuración básica

```typescript
// src/api/axios.ts
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

// Crear instancia con configuración base
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos
});

// Interceptor de solicitudes
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Obtener token del almacenamiento local
    const token = localStorage.getItem('token');
    
    // Si existe token, añadirlo a los headers
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Interceptor de respuestas
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    // Manejar errores comunes
    if (error.response) {
      // Error de servidor (4xx, 5xx)
      const status = error.response.status;
      
      if (status === 401) {
        // Token expirado o inválido
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else if (status === 403) {
        // Permiso denegado
        console.error('Permiso denegado');
      }
    } else if (error.request) {
      // No se recibió respuesta
      console.error('No se pudo conectar al servidor');
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

## Implementación de servicios de API

### Servicio de Productos

```typescript
// src/api/products.ts
import api from './axios';
import { Product, ProductCreate, ProductUpdate } from '../types/product';

// Obtener lista de productos con paginación
export const getProducts = async (page = 1, limit = 10) => {
  const response = await api.get<Product[]>('/products', {
    params: { skip: (page - 1) * limit, limit }
  });
  return response.data;
};

// Obtener un producto por ID
export const getProduct = async (id: number) => {
  const response = await api.get<Product>(`/products/${id}`);
  return response.data;
};

// Crear un nuevo producto
export const createProduct = async (product: ProductCreate) => {
  const response = await api.post<Product>('/products', product);
  return response.data;
};

// Actualizar un producto existente
export const updateProduct = async (id: number, product: ProductUpdate) => {
  const response = await api.put<Product>(`/products/${id}`, product);
  return response.data;
};

// Eliminar un producto
export const deleteProduct = async (id: number) => {
  const response = await api.delete<Product>(`/products/${id}`);
  return response.data;
};
```

## Integración con React Query

React Query es una biblioteca para gestionar el estado de datos y caché en aplicaciones React. Se integra 
perfectamente con Axios:

```typescript
// src/hooks/useProducts.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from '../api/products';
import { ProductCreate, ProductUpdate } from '../types/product';

// Hook para obtener productos
export const useProducts = (page = 1, limit = 10) => {
  return useQuery(['products', page, limit], () => getProducts(page, limit), {
    keepPreviousData: true,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

// Hook para obtener un producto específico
export const useProduct = (id: number) => {
  return useQuery(['product', id], () => getProduct(id), {
    enabled: !!id,
  });
};

// Hook para crear un producto
export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation((product: ProductCreate) => createProduct(product), {
    onSuccess: () => {
      // Invalidar consultas para refrescar datos
      queryClient.invalidateQueries('products');
    },
  });
};

// Hook para actualizar un producto
export const useUpdateProduct = (id: number) => {
  const queryClient = useQueryClient();
  
  return useMutation((product: ProductUpdate) => updateProduct(id, product), {
    onSuccess: (data) => {
      // Actualizar producto en caché
      queryClient.setQueryData(['product', id], data);
      // Invalidar lista de productos
      queryClient.invalidateQueries('products');
    },
  });
};

// Hook para eliminar un producto
export const useDeleteProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation((id: number) => deleteProduct(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('products');
    },
  });
};
```

## Uso en componentes React

```tsx
// src/components/ProductList.tsx
import React from 'react';
import { useProducts } from '../hooks/useProducts';

const ProductList: React.FC = () => {
  const [page, setPage] = React.useState(1);
  const { data, isLoading, error } = useProducts(page);

  if (isLoading) return <div>Cargando...</div>;
  if (error) return <div>Error al cargar productos</div>;

  return (
    <div>
      <h2>Lista de Productos</h2>
      <ul>
        {data?.map(product => (
          <li key={product.id}>{product.name} - ${product.price}</li>
        ))}
      </ul>
      <button 
        onClick={() => setPage(p => Math.max(1, p - 1))}
        disabled={page === 1}
      >
        Anterior
      </button>
      <button 
        onClick={() => setPage(p => p + 1)}
        disabled={!data || data.length < 10}
      >
        Siguiente
      </button>
    </div>
  );
};

export default ProductList;
```

## Manejo de errores y carga

```tsx
// src/components/ProductForm.tsx
import React from 'react';
import { useCreateProduct } from '../hooks/useProducts';
import { ProductCreate } from '../types/product';

const ProductForm: React.FC = () => {
  const [form, setForm] = React.useState<ProductCreate>({
    name: '',
    description: '',
    price: 0,
    stock: 0
  });
  
  const createProduct = useCreateProduct();
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'stock' 
        ? parseFloat(value) 
        : value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProduct.mutateAsync(form);
      alert('Producto creado con éxito');
      // Limpiar formulario
      setForm({ name: '', description: '', price: 0, stock: 0 });
    } catch (error) {
      console.error('Error al crear producto:', error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Nombre:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={form.name}
          onChange={handleChange}
          required
        />
      </div>
      {/* Otros campos del formulario */}
      <button 
        type="submit" 
        disabled={createProduct.isLoading}
      >
        {createProduct.isLoading ? 'Creando...' : 'Crear Producto'}
      </button>
      
      {createProduct.isError && (
        <div className="error">
          Error: {(createProduct.error as Error).message}
        </div>
      )}
    </form>
  );
};

export default ProductForm;
```

## Configuración para cargas de archivos

```typescript
// src/api/upload.ts
import api from './axios';

export const uploadProductImage = async (productId: number, file: File) => {
  // Crear FormData para enviar el archivo
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/products/${productId}/image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    // Añadir manejador de progreso
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / (progressEvent.total || 1)
      );
      console.log(`Progreso: ${percentCompleted}%`);
    },
  });
  
  return response.data;
};
```

## Mejores prácticas

1. **Centralizar configuración**: Mantener una instancia global de Axios configurada
2. **Interceptores para aspectos transversales**:
    - Añadir tokens de autenticación
    - Manejar errores comunes
    - Implementar lógica de reintento
3. **Cancelación de solicitudes**: Cancelar peticiones pendientes cuando un componente se desmonta
   ```typescript
   const source = axios.CancelToken.source();
   
   useEffect(() => {
     api.get('/data', { cancelToken: source.token });
     
     return () => {
       source.cancel('Componente desmontado');
     };
   }, []);
   ```
4. **Timeouts adecuados**: Establecer tiempos de espera según la naturaleza de la operación
5. **Tipado de respuestas**: Utilizar TypeScript para tipar respuestas y parámetros
6. **Captura y manejo de errores**: Capturar errores específicos de la API
7. **Integrar con React Query**: Para cacheo, invalidación y manejo del estado de carga

## Consideraciones de seguridad

1. **Sanitización de datos**: Validar y sanitizar datos antes de enviarlos
2. **Protección CSRF**: Configurar tokens CSRF cuando sea necesario
3. **Almacenamiento seguro de tokens**: Considerar donde almacenar tokens de autenticación
4. **Validación de respuestas**: No confiar ciegamente en respuestas del servidor
5. **HTTPS**: Asegurar que todas las comunicaciones sean sobre HTTPS

## Ejemplos específicos para inventario

### Actualización de stock en tiempo real

```typescript
// src/api/inventory.ts
import api from './axios';
import { StockAdjustment } from '../types/inventory';

export const adjustStock = async (adjustment: StockAdjustment) => {
  return api.post('/inventory/adjust-stock', adjustment);
};
```

### Búsqueda avanzada de productos

```typescript
// src/api/products.ts
export const searchProducts = async (
  query: string,
  filters: {
    minPrice?: number;
    maxPrice?: number;
    category?: string;
    inStock?: boolean;
  }
) => {
  const response = await api.get('/products/search', {
    params: {
      q: query,
      ...filters
    }
  });
  return response.data;
};
```