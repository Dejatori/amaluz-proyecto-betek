# React Query: Gestión de Estado y Caché para React

## ¿Qué es React Query?

React Query es una biblioteca de gestión de estado y caché para datos asíncronos en aplicaciones React. Facilita la obtención, sincronización, actualización y caché de datos del servidor sin necesidad de gestionar manualmente el estado global. Está diseñada específicamente para manejar el "estado del servidor" (datos que provienen de un servidor) de manera eficiente.

## ¿Por qué usar React Query?

- **Gestión automática de caché**: Almacena los resultados de consultas para minimizar solicitudes innecesarias
- **Revalidación en segundo plano**: Actualiza datos automáticamente mientras muestra datos en caché
- **Refetch automático**: Reactiva consultas cuando la ventana recupera el foco o la conexión se restablece
- **Gestión de estados de carga**: Estados `isLoading`, `isError`, `isSuccess` integrados
- **Paginación y consultas infinitas**: Soporte integrado para paginación y carga infinita
- **Gestión de mutaciones**: Facilita operaciones de actualización con invalidación automática de caché
- **DevTools**: Herramientas de desarrollo visual para inspeccionar el estado de la caché

## Configuración en nuestro proyecto

### Estructura de archivos

```
src/
├── hooks/
│   ├── useProducts.ts      # Hooks personalizados para productos
│   ├── useCustomers.ts     # Hooks personalizados para clientes
│   └── useOrders.ts        # Hooks personalizados para pedidos
├── api/
│   ├── axios.ts            # Configuración de Axios
│   └── products.ts         # Funciones de API para productos
├── components/
│   └── Products/
│       ├── ProductList.tsx # Componentes que consumen hooks
```

### Configuración básica

```tsx
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import App from './App';
import './index.css';

// Crear instancia de QueryClient con configuración por defecto
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      refetchOnReconnect: true,
      staleTime: 1000 * 60 * 5, // 5 minutos
      cacheTime: 1000 * 60 * 30, // 30 minutos
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
```

## Implementación de hooks personalizados

### 1. Consulta básica (useQuery)

```typescript
// src/hooks/useProducts.ts
import { useQuery, UseQueryOptions } from 'react-query';
import { getProducts, getProduct } from '../api/products';
import { Product } from '../types/product';

// Hook para obtener lista de productos
export const useProducts = (page = 1, limit = 10, options?: UseQueryOptions<Product[]>) => {
  return useQuery<Product[]>(
    ['products', page, limit], // Clave de caché única
    () => getProducts(page, limit),
    {
      keepPreviousData: true, // Mantener datos anteriores mientras se carga la siguiente página
      ...options
    }
  );
};

// Hook para obtener un producto específico
export const useProduct = (id: number, options?: UseQueryOptions<Product>) => {
  return useQuery<Product>(
    ['product', id],
    () => getProduct(id),
    {
      enabled: !!id, // Solo ejecutar si hay un ID
      ...options
    }
  );
};
```

### 2. Mutaciones (useMutation)

```typescript
// src/hooks/useProducts.ts (continuación)
import { useMutation, useQueryClient } from 'react-query';
import { createProduct, updateProduct, deleteProduct } from '../api/products';
import { ProductCreate, ProductUpdate } from '../types/product';

// Hook para crear un producto
export const useCreateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (newProduct: ProductCreate) => createProduct(newProduct),
    {
      onSuccess: () => {
        // Invalidar consultas para que se actualice la UI
        queryClient.invalidateQueries('products');
      },
    }
  );
};

// Hook para actualizar un producto
export const useUpdateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ id, data }: { id: number, data: ProductUpdate }) => updateProduct(id, data),
    {
      onSuccess: (updatedProduct) => {
        // Actualizar producto en caché
        queryClient.setQueryData(['product', updatedProduct.id], updatedProduct);
        // Invalidar listas que puedan contener este producto
        queryClient.invalidateQueries('products');
      },
    }
  );
};

// Hook para eliminar un producto
export const useDeleteProduct = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (id: number) => deleteProduct(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
      },
    }
  );
};
```

## Uso en componentes React

### 1. Listado con paginación

```tsx
// src/components/Products/ProductList.tsx
import React, { useState } from 'react';
import { useProducts } from '../../hooks/useProducts';

const ProductList: React.FC = () => {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, error, isPreviousData } = useProducts(page);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Productos</h1>
      
      {isLoading ? (
        <div className="flex justify-center">
          <div className="spinner">Cargando...</div>
        </div>
      ) : isError ? (
        <div className="bg-red-100 p-4 rounded text-red-700">
          Error: {(error as Error).message}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.map(product => (
              <div key={product.id} className="border p-4 rounded shadow">
                <h2 className="text-lg font-semibold">{product.name}</h2>
                <p className="text-gray-600">{product.description}</p>
                <div className="mt-2">
                  <span className="font-bold">${product.price}</span>
                  <span className="text-sm text-gray-500 ml-2">
                    Stock: {product.stock}
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex justify-between mt-4">
            <button
              onClick={() => setPage(old => Math.max(old - 1, 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Anterior
            </button>
            <span>Página {page}</span>
            <button
              onClick={() => setPage(old => old + 1)}
              disabled={!data || data.length < 10 || isPreviousData}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ProductList;
```

### 2. Formulario con mutación

```tsx
// src/components/Products/AddProductForm.tsx
import React from 'react';
import { useCreateProduct } from '../../hooks/useProducts';

const AddProductForm: React.FC = () => {
  const [product, setProduct] = React.useState({
    name: '',
    description: '',
    price: 0,
    stock: 0
  });
  
  const createProductMutation = useCreateProduct();
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProduct(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'stock'
        ? parseFloat(value) || 0
        : value
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProductMutation.mutate(product, {
      onSuccess: () => {
        // Resetear formulario
        setProduct({
          name: '',
          description: '',
          price: 0,
          stock: 0
        });
        // Notificar al usuario
        alert('¡Producto creado con éxito!');
      }
    });
  };
  
  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-xl font-bold mb-4">Añadir Nuevo Producto</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre</label>
          <input
            type="text"
            name="name"
            value={product.name}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Descripción</label>
          <textarea
            name="description"
            value={product.description}
            onChange={handleChange}
            className="w-full p-2 border rounded"
            rows={3}
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Precio</label>
            <input
              type="number"
              name="price"
              value={product.price}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              min="0"
              step="0.01"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Stock</label>
            <input
              type="number"
              name="stock"
              value={product.stock}
              onChange={handleChange}
              className="w-full p-2 border rounded"
              min="0"
              required
            />
          </div>
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          disabled={createProductMutation.isLoading}
        >
          {createProductMutation.isLoading ? 'Guardando...' : 'Guardar Producto'}
        </button>
        
        {createProductMutation.isError && (
          <div className="bg-red-100 p-3 rounded text-red-700 text-sm">
            Error: {(createProductMutation.error as Error).message}
          </div>
        )}
      </form>
    </div>
  );
};

export default AddProductForm;
```

## Características avanzadas de React Query

### 1. Consultas dependientes

Ideal para cuando necesitas datos de una consulta para realizar otra:

```typescript
// src/hooks/useOrders.ts
import { useQuery } from 'react-query';
import { getOrderDetails, getOrderItems } from '../api/orders';

export const useOrderWithItems = (orderId: number) => {
  // Primera consulta: obtener detalles del pedido
  const orderQuery = useQuery(
    ['order', orderId],
    () => getOrderDetails(orderId),
    { enabled: !!orderId }
  );
  
  // Consulta dependiente: obtener ítems solo si tenemos el pedido
  const itemsQuery = useQuery(
    ['orderItems', orderId],
    () => getOrderItems(orderId),
    { 
      enabled: !!orderId && !!orderQuery.data,
      // Solo ejecutar cuando exista orderId y orderQuery.data
    }
  );
  
  return {
    order: orderQuery.data,
    items: itemsQuery.data,
    isLoading: orderQuery.isLoading || itemsQuery.isLoading,
    isError: orderQuery.isError || itemsQuery.isError,
  };
};
```

### 2. Consultas infinitas

Para implementar listas con scroll infinito:

```typescript
// src/hooks/useInfiniteProducts.ts
import { useInfiniteQuery } from 'react-query';
import { getProducts } from '../api/products';

export const useInfiniteProducts = (limit = 10) => {
  return useInfiniteQuery(
    ['infiniteProducts', limit],
    ({ pageParam = 1 }) => getProducts(pageParam, limit),
    {
      getNextPageParam: (lastPage, allPages) => {
        // Si la última página tiene menos items que el límite, no hay más páginas
        return lastPage.length === limit ? allPages.length + 1 : undefined;
      },
    }
  );
};
```

Uso en componente:

```tsx
// src/components/Products/InfiniteProductList.tsx
import React, { useRef, useCallback } from 'react';
import { useInfiniteProducts } from '../../hooks/useInfiniteProducts';

const InfiniteProductList: React.FC = () => {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error
  } = useInfiniteProducts();
  
  // Configurar el observador de intersección para cargar más al hacer scroll
  const observer = useRef<IntersectionObserver>();
  const lastElementRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (isFetchingNextPage) return;
      if (observer.current) observer.current.disconnect();
      
      observer.current = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting && hasNextPage) {
          fetchNextPage();
        }
      });
      
      if (node) observer.current.observe(node);
    },
    [isFetchingNextPage, fetchNextPage, hasNextPage]
  );
  
  // Renderizado condicional
  if (isLoading) return <div>Cargando productos...</div>;
  if (isError) return <div>Error: {(error as Error).message}</div>;
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Catálogo de Productos</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.pages.map((page, i) => (
          <React.Fragment key={i}>
            {page.map((product, index) => {
              // Marcar el último elemento para el observador
              if (i === data.pages.length - 1 && index === page.length - 1) {
                return (
                  <div
                    ref={lastElementRef}
                    key={product.id}
                    className="border p-4 rounded shadow"
                  >
                    <h2 className="text-lg font-semibold">{product.name}</h2>
                    <p className="text-gray-600">{product.description}</p>
                    <div className="mt-2">
                      <span className="font-bold">${product.price}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        Stock: {product.stock}
                      </span>
                    </div>
                  </div>
                );
              } else {
                return (
                  <div key={product.id} className="border p-4 rounded shadow">
                    <h2 className="text-lg font-semibold">{product.name}</h2>
                    <p className="text-gray-600">{product.description}</p>
                    <div className="mt-2">
                      <span className="font-bold">${product.price}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        Stock: {product.stock}
                      </span>
                    </div>
                  </div>
                );
              }
            })}
          </React.Fragment>
        ))}
      </div>
      
      {isFetchingNextPage && (
        <div className="text-center my-4">Cargando más productos...</div>
      )}
    </div>
  );
};

export default InfiniteProductList;
```

### 3. Consulta paralela optimizada (useQueries)

Para realizar múltiples consultas en paralelo:

```typescript
// src/hooks/useDashboardData.ts
import { useQueries } from 'react-query';
import { 
  getTopProducts, 
  getLowStockItems, 
  getRecentOrders, 
  getSalesStats 
} from '../api/dashboard';

export const useDashboardData = () => {
  const results = useQueries([
    { queryKey: ['topProducts'], queryFn: getTopProducts },
    { queryKey: ['lowStock'], queryFn: getLowStockItems },
    { queryKey: ['recentOrders'], queryFn: getRecentOrders },
    { queryKey: ['salesStats'], queryFn: getSalesStats }
  ]);
  
  const isLoading = results.some(result => result.isLoading);
  const isError = results.some(result => result.isError);
  
  return {
    topProducts: results[0].data,
    lowStockItems: results[1].data,
    recentOrders: results[2].data,
    salesStats: results[3].data,
    isLoading,
    isError,
    errors: results.map(r => r.error).filter(Boolean)
  };
};
```

## Optimización de la caché

```typescript
// src/api/queryClient.ts
import { QueryClient } from 'react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Configuraciones globales
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 30 * 60 * 1000, // 30 minutos
      retry: process.env.NODE_ENV === 'production' ? 3 : 0,
      onError: (err) => {
        console.error('Error en consulta:', err);
      }
    },
    mutations: {
      // Configuración de mutaciones
      retry: 2,
      onError: (err) => {
        console.error('Error en mutación:', err);
      }
    }
  }
});

// Funciones helper para manejar la caché
export const prefetchProduct = async (id: number) => {
  await queryClient.prefetchQuery(['product', id], () => getProduct(id));
};

export const invalidateProductQueries = () => {
  queryClient.invalidateQueries('products');
};

export const clearCache = () => {
  queryClient.clear();
};
```

## Integración con Axios

React Query se integra perfectamente con Axios (que ya usamos para las peticiones HTTP):

```typescript
// src/api/products.ts
import api from './axios';
import { Product, ProductCreate, ProductUpdate } from '../types/product';

export const getProducts = async (page = 1, limit = 10): Promise<Product[]> => {
  const response = await api.get<Product[]>('/products', {
    params: { skip: (page - 1) * limit, limit }
  });
  return response.data;
};

// Otras funciones de API...
```

```typescript
// src/hooks/useProducts.ts
import { useQuery } from 'react-query';
import { getProducts } from '../api/products';

export const useProducts = (page = 1, limit = 10) => {
  return useQuery(['products', page, limit], () => getProducts(page, limit), {
    keepPreviousData: true,
  });
};
```

## Gestión de errores

```tsx
// src/components/ErrorBoundary.tsx
import React from 'react';
import { useQueryErrorResetBoundary } from 'react-query';

interface Props {
  children: React.ReactNode;
}

const ErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({ 
  error, 
  resetErrorBoundary 
}) => {
  return (
    <div className="p-4 bg-red-50 rounded-lg">
      <h2 className="text-lg font-bold text-red-700">Algo salió mal:</h2>
      <pre className="mt-2 text-sm text-red-600">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="mt-4 px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200"
      >
        Reintentar
      </button>
    </div>
  );
};

export const QueryErrorBoundary: React.FC<Props> = ({ children }) => {
  const { reset } = useQueryErrorResetBoundary();
  
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={reset}>
      {children}
    </ErrorBoundary>
  );
};
```

## Mejores prácticas

1. **Estructurar claves de consulta**:
   ```typescript
   // Estructura jerárquica para facilitar invalidación
   ['products']                  // Todos los productos
   ['products', 'list', page]    // Lista paginada
   ['product', id]               // Producto específico
   ['products', 'low-stock']     // Productos con bajo stock
   ```

2. **Reutilizar hooks de consulta**:
    - Crear hooks personalizados para cada entidad (productos, clientes, pedidos)
    - Mantener lógica de consulta y caché centralizada

3. **Optimizar configuraciones de revalidación**:
    - Ajustar `staleTime` según la frecuencia de cambio de los datos
    - Para datos estáticos: `staleTime: Infinity`
    - Para datos dinámicos: `staleTime` más corto (30 segundos a 5 minutos)

4. **Implementar manejo de errores robusto**:
    - Usar `onError` para manejar errores específicos
    - Implementar reintentos con `retry` para fallas de red
    - Utilizar `ErrorBoundary` para capturar y mostrar errores

5. **Prefetching estratégico**:
    - Precargar datos que probablemente se necesitarán:
   ```typescript
   // Precargar detalles del producto al hacer hover sobre su tarjeta
   const prefetchProductDetails = (id: number) => {
     queryClient.prefetchQuery(['product', id], () => getProduct(id));
   };
   ```

6. **Optimistic Updates**:
   ```typescript
   // src/hooks/useToggleProductStatus.ts
   export const useToggleProductStatus = () => {
     const queryClient = useQueryClient();
     
     return useMutation(
       ({ id, isActive }: { id: number; isActive: boolean }) => 
         updateProductStatus(id, isActive),
       {
         // Actualizar caché antes de que la petición termine
         onMutate: async ({ id, isActive }) => {
           // Cancelar consultas en curso
           await queryClient.cancelQueries(['product', id]);
           
           // Guardar estado anterior
           const previousProduct = queryClient.getQueryData(['product', id]);
           
           // Actualizar caché optimistamente
           queryClient.setQueryData(['product', id], (old: any) => ({
             ...old,
             isActive
           }));
           
           // Devolver contexto con estado anterior para rollback
           return { previousProduct };
         },
         // Si hay error, revertir a estado anterior
         onError: (err, variables, context) => {
           if (context?.previousProduct) {
             queryClient.setQueryData(
               ['product', variables.id],
               context.previousProduct
             );
           }
         },
         // Siempre invalidar tras finalizar
         onSettled: (data, error, variables) => {
           queryClient.invalidateQueries(['product', variables.id]);
         }
       }
     );
   };
   ```

7. **Configurar data transformations**:
   ```typescript
   // src/hooks/useProducts.ts
   export const useSearchProducts = (query: string) => {
     return useQuery(
       ['products', 'search', query],
       () => searchProducts(query),
       {
         // Transformar resultados para formatear fechas, etc.
         select: (data) => data.map(product => ({
           ...product,
           createdAt: new Date(product.createdAt),
           // Añadir campos calculados
           discountedPrice: product.price * (1 - (product.discount || 0) / 100)
         }))
       }
     );
   };
   ```

## Ejemplos específicos para inventario

### 1. Dashboard con datos en tiempo real

```tsx
// src/pages/Dashboard.tsx
import React from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { DashboardChart, StockAlert, RecentOrdersList } from '../components/Dashboard';

const Dashboard: React.FC = () => {
  const { 
    topProducts, 
    lowStockItems, 
    recentOrders, 
    salesStats, 
    isLoading 
  } = useDashboardData();
  
  // Configurar refresco automático cada 30 segundos
  const refetchInterval = 30 * 1000;
  
  // Usar refetchInterval para datos que necesitan actualización frecuente
  const { data: alertsData } = useQuery(
    'alerts', 
    getAlerts, 
    { refetchInterval }
  );
  
  if (isLoading) return <div>Cargando dashboard...</div>;
  
  return (
    <div className="container mx-auto p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <DashboardCard title="Ventas del Mes">
        <DashboardChart data={salesStats} />
      </DashboardCard>
      
      <DashboardCard title="Productos con Bajo Stock">
        <StockAlert items={lowStockItems} />
      </DashboardCard>
      
      <DashboardCard title="Pedidos Recientes">
        <RecentOrdersList orders={recentOrders} />
      </DashboardCard>
      
      {/* Otros widgets del dashboard */}
    </div>
  );
};

export default Dashboard;
```

### 2. Formulario de ajuste de inventario

```tsx
// src/components/Inventory/InventoryAdjustmentForm.tsx
import React, { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { adjustInventory } from '../../api/inventory';
import { Product } from '../../types/product';

interface InventoryAdjustmentFormProps {
  product: Product;
  onSuccess?: () => void;
}

const InventoryAdjustmentForm: React.FC<InventoryAdjustmentFormProps> = ({ 
  product, 
  onSuccess 
}) => {
  const [quantity, setQuantity] = useState<number>(0);
  const [reason, setReason] = useState<string>('');
  const queryClient = useQueryClient();
  
  // Usar useMutation para ajustar el inventario
  const adjustInventoryMutation = useMutation(
    (data: { productId: number; quantity: number; reason: string }) => 
      adjustInventory(data),
    {
      // Actualización optimista - actualizar la UI antes de que la API responda
      onMutate: async (newAdjustment) => {
        // Cancelar cualquier consulta en curso para evitar sobrescrituras
        await queryClient.cancelQueries(['product', product.id]);
        
        // Guardar el estado anterior
        const previousProduct = queryClient.getQueryData<Product>(['product', product.id]);
        
        // Actualizar la caché optimistamente
        if (previousProduct) {
          queryClient.setQueryData<Product>(['product', product.id], {
            ...previousProduct,
            stock: previousProduct.stock + newAdjustment.quantity
          });
        }
        
        // Devolver contexto con el producto anterior
        return { previousProduct };
      },
      
      // En caso de error, revertir al estado anterior
      onError: (err, newAdjustment, context) => {
        if (context?.previousProduct) {
          queryClient.setQueryData(
            ['product', product.id],
            context.previousProduct
          );
        }
      },
      
      // Después de una mutación exitosa, invalidar consultas relevantes
      onSuccess: () => {
        // Invalidar consulta específica del producto
        queryClient.invalidateQueries(['product', product.id]);
        // Invalidar listas de productos que podrían mostrar este producto
        queryClient.invalidateQueries('products');
        // Invalidar consultas de bajo stock si este ajuste podría afectarlas
        queryClient.invalidateQueries('lowStockProducts');
        
        // Ejecutar callback opcional
        if (onSuccess) onSuccess();
        
        // Resetear formulario
        setQuantity(0);
        setReason('');
      }
    }
  );
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar entrada
    if (!quantity) {
      alert('La cantidad no puede ser cero');
      return;
    }
    
    if (!reason.trim()) {
      alert('Debe proporcionar una razón para el ajuste');
      return;
    }
    
    // Ejecutar la mutación
    adjustInventoryMutation.mutate({
      productId: product.id,
      quantity,
      reason
    });
  };
  
  return (
    <div className="max-w-md mx-auto p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-4">
        Ajustar Inventario: {product.name}
      </h2>
      
      <div className="mb-4">
        <p className="text-gray-600">Stock actual: {product.stock} unidades</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="quantity" className="block text-sm font-medium text-gray-700">
            Cantidad (+ aumenta, - reduce)
          </label>
          <input
            type="number"
            id="quantity"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        
        <div className="mb-4">
          <label htmlFor="reason" className="block text-sm font-medium text-gray-700">
            Razón del ajuste
          </label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            rows={3}
          />
        </div>
        
        <button
          type="submit"
          disabled={adjustInventoryMutation.isLoading}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {adjustInventoryMutation.isLoading ? 'Procesando...' : 'Ajustar Inventario'}
        </button>
        
        {adjustInventoryMutation.isError && (
          <div className="mt-2 text-red-500">
            Error: {(adjustInventoryMutation.error as Error).message}
          </div>
        )}
        
        {adjustInventoryMutation.isSuccess && (
          <div className="mt-2 text-green-500">
            Inventario ajustado correctamente
          </div>
        )}
      </form>
    </div>
  );
};

export default InventoryAdjustmentForm;
```

### 3. Búsqueda avanzada con filtros

```tsx
// src/components/Products/ProductSearch.tsx
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { searchProducts } from '../../api/products';

interface SearchFilters {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
}

const ProductSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    inStock: true
  });
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [debouncedFilters, setDebouncedFilters] = useState<SearchFilters>(filters);
  
  // Debounce función para evitar múltiples llamadas durante la escritura
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setDebouncedFilters(filters);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchTerm, filters]);
  
  // Consulta con React Query
  const { data, isLoading, isError } = useQuery(
    ['productSearch', debouncedSearch, debouncedFilters],
    () => searchProducts(debouncedSearch, debouncedFilters),
    {
      // No ejecutar la consulta si no hay término de búsqueda
      enabled: debouncedSearch.length > 0,
      // Mantener resultados anteriores mientras se cargan nuevos
      keepPreviousData: true,
      // Tiempo de caducidad más corto para búsquedas
      staleTime: 1000 * 60 * 5 // 5 minutos
    }
  );
  
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    setFilters(prev => ({
      ...prev,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked
        : type === 'number' 
          ? parseFloat(value) || undefined
          : value
    }));
  };
  
  return (
    <div className="space-y-4">
      <div className="flex space-x-2">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Buscar productos..."
          className="flex-1 p-2 border rounded"
        />
        <button 
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => setSearchTerm('')}
        >
          Limpiar
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Categoría</label>
          <select
            name="category"
            value={filters.category || ''}
            onChange={handleFilterChange}
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
          >
            <option value="">Todas las categorías</option>
            <option value="electronics">Electrónica</option>
            <option value="clothing">Ropa</option>
            <option value="furniture">Muebles</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Precio mínimo</label>
          <input
            type="number"
            name="minPrice"
            value={filters.minPrice || ''}
            onChange={handleFilterChange}
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Precio máximo</label>
          <input
            type="number"
            name="maxPrice"
            value={filters.maxPrice || ''}
            onChange={handleFilterChange}
            className="mt-1 block w-full border border-gray-300 rounded-md p-2"
          />
        </div>
        
        <div className="flex items-center mt-6">
          <input
            type="checkbox"
            name="inStock"
            id="inStock"
            checked={filters.inStock || false}
            onChange={handleFilterChange}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          <label htmlFor="inStock" className="ml-2 block text-sm text-gray-700">
            Solo productos en stock
          </label>
        </div>
      </div>
      
      {isLoading && <div className="text-center py-4">Buscando productos...</div>}
      
      {isError && (
        <div className="text-center py-4 text-red-500">
          Error al buscar productos. Intente nuevamente.
        </div>
      )}
      
      {!isLoading && !isError && debouncedSearch && (
        <div className="mt-4">
          <h3 className="text-lg font-medium">
            {data?.length 
              ? `Resultados (${data.length})` 
              : "No se encontraron productos"}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
            {data?.map(product => (
              <div key={product.id} className="border rounded p-4">
                <h4 className="font-bold">{product.name}</h4>
                <p className="text-gray-600">${product.price.toFixed(2)}</p>
                <p className="text-sm">Stock: {product.stock}</p>
                <p className="text-xs text-gray-500">Categoría: {product.category}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductSearch;
```

## Implementación de sincronización en tiempo real

React Query también puede utilizarse para implementar experiencias en tiempo real mediante el uso de websockets o polling:

```tsx
// src/hooks/useRealtimeInventory.ts
import { useQuery } from 'react-query';
import { getProductStock } from '../api/products';

export const useRealtimeInventory = (productId: number) => {
  return useQuery(
    ['productStock', productId],
    () => getProductStock(productId),
    {
      // Actualización cada 5 segundos
      refetchInterval: 5000,
      // Continuar actualizando incluso cuando la ventana pierde foco
      refetchIntervalInBackground: true,
      // Función personalizada para determinar si es necesario actualizar la UI
      onSuccess: (data, variables, context) => {
        // Muestra notificación si el stock está por debajo del umbral
        if (data.stock < data.minStockThreshold) {
          showStockAlert(data.name, data.stock);
        }
      }
    }
  );
};
```

## Conclusión

React Query ofrece una solución robusta para gestionar el estado del servidor en aplicaciones React, proporcionando una
API intuitiva para realizar operaciones CRUD contra nuestra API FastAPI. Al combinarlo con TypeScript, obtenemos un 
sistema completamente tipado desde el backend hasta el frontend.

La principal ventaja de React Query es la reducción significativa de código boilerplate para manejar estados de carga,
error y éxito, además de proporcionar una estrategia de caché sofisticada que mejora el rendimiento y la experiencia 
de usuario.

En nuestro sistema de gestión de inventario, React Query nos permite:

1. Mostrar datos actualizados de productos y stock
2. Implementar operaciones como creación, actualización y eliminación de productos
3. Reflejar cambios inmediatamente en la UI con actualizaciones optimistas
4. Mantener la coherencia de datos en múltiples componentes
5. Reducir solicitudes innecesarias al servidor mediante estrategias de caché
6. Proporcionar feedback inmediato a los usuarios

La integración con Axios hace que sea fácil conectar nuestro frontend con el backend FastAPI, creando un flujo de 
datos eficiente y confiable para nuestro sistema de gestión de inventario.