# Vite: Herramienta de Desarrollo Moderna para Frontend

## ¿Qué es Vite?

Vite (pronunciado "vit", significa "rápido" en francés) es una herramienta de desarrollo frontend de nueva generación
creada por Evan You, el autor de Vue.js. Proporciona un entorno de desarrollo extremadamente rápido gracias a su 
servidor de desarrollo con HMR (Hot Module Replacement) nativo basado en ESM (ECMAScript Modules) y un sistema de
construcción optimizado para producción.

## ¿Por qué usar Vite?

- **Desarrollo ultrarrápido**: Servidor de desarrollo con tiempos de inicio instantáneos
- **HMR veloz**: Actualizaciones en tiempo real sin recargar la página completa
- **Optimizado para ESM**: Aprovecha los módulos ES nativos para mayor eficiencia
- **Construcción rápida**: Utiliza Rollup para bundles de producción optimizados
- **Configuración mínima**: Funciona de inmediato con configuración sensata por defecto
- **Ampliable**: Sistema de plugins compatible con el ecosistema de Rollup
- **Soporte TypeScript nativo**: Sin necesidad de configuraciones complejas
- **CSS con funcionalidades avanzadas**: Soporte para CSS Modules, PostCSS y preprocesadores

## Configuración en nuestro proyecto

Nuestro sistema de gestión de inventario utiliza Vite como herramienta de construcción para la parte frontend, 
con la siguiente estructura:

```
frontend/
├── index.html                # Punto de entrada HTML
├── package.json              # Dependencias y scripts
├── vite.config.ts            # Configuración de Vite
├── tsconfig.json             # Configuración de TypeScript
├── src/
│   ├── main.tsx              # Punto de entrada JavaScript/TypeScript
│   ├── App.tsx               # Componente raíz
│   ├── components/           # Componentes React
│   ├── pages/                # Páginas/rutas de la aplicación
│   ├── api/                  # Comunicación con API (Axios)
│   ├── hooks/                # Hooks personalizados
│   ├── types/                # Definiciones de TypeScript
│   ├── utils/                # Funciones utilitarias
│   └── assets/               # Recursos estáticos
└── public/                   # Archivos estáticos que no requieren procesamiento
```

### Configuración de Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
});
```

### Scripts en package.json

```json
{
  "scripts": {
    "dev": "vite",            // Inicia el servidor de desarrollo
    "build": "tsc -b && vite build",  // Compila TypeScript y construye para producción
    "preview": "vite preview" // Vista previa del build de producción
  }
}
```

## Flujo de Desarrollo con Vite

### 1. Desarrollo local

Para iniciar el servidor de desarrollo:

```bash
npm run dev
```

Esto inicia un servidor de desarrollo local, normalmente en `http://localhost:3000`, con las siguientes características:

- **Hot Module Replacement (HMR)**: Los cambios en el código se reflejan instantáneamente sin perder el estado de la aplicación
- **Error Overlay**: Los errores se muestran claramente en el navegador
- **Soporte para TypeScript**: Comprobación de tipos en tiempo real
- **Soporte para CSS**: Preprocesamiento y módulos CSS

### 2. Estructura del proyecto

El punto de entrada de la aplicación es `index.html` en la raíz del proyecto:

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sistema de Gestión de Inventario</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Y el punto de entrada JavaScript/TypeScript es `src/main.tsx`:

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import App from './App';
import './index.css';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 3. Importación de módulos

Vite permite importar diversos tipos de archivos directamente:

```tsx
// Importación de CSS
import './styles.css';

// Importación de imágenes
import logo from './assets/logo.png';

// Importación de SVG como componente (con plugin adecuado)
import { ReactComponent as Icon } from './assets/icon.svg';

// Importación de JSON
import data from './data.json';

// Importación de módulos CSS
import styles from './Component.module.css';
```

### 4. Variables de entorno

Vite proporciona soporte integrado para variables de entorno:

```
# .env
VITE_API_URL=http://localhost:8000/api/v1
```

Acceso en código:

```typescript
// Solo variables con prefijo VITE_ están disponibles en el cliente
const apiUrl = import.meta.env.VITE_API_URL;
```

## Construcción para Producción

Para construir la aplicación para producción:

```bash
npm run build
```

Esto genera una versión optimizada de la aplicación en el directorio `dist/` con las siguientes características:

- **Code Splitting**: División automática de código para cargar solo lo necesario
- **Tree Shaking**: Eliminación de código no utilizado
- **Minificación**: Reducción del tamaño de los archivos
- **Hashing**: Nombres de archivo con hash para invalidación de caché efectiva
- **Precargas**: Generación automática de etiquetas de precarga

Para previsualizar la versión de producción localmente:

```bash
npm run preview
```

## Integración con otras herramientas

### 1. TypeScript

Vite tiene soporte nativo para TypeScript. La configuración en `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ESNext"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": false,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 2. TailwindCSS

Integración con TailwindCSS mediante el plugin `@tailwindcss/vite`:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... otros tonos
          900: '#0c4a6e'
        }
      }
    }
  },
  plugins: []
};
```

### 3. React Router

Configuración de rutas con React Router:

```tsx
// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="products" element={<Products />} />
        <Route path="products/:id" element={<ProductDetail />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
```

## Optimizaciones avanzadas

### 1. Carga diferida (Lazy Loading)

```tsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Loading from './components/Loading';

// Carga diferida de componentes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Products = lazy(() => import('./pages/Products'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={
          <Suspense fallback={<Loading />}>
            <Dashboard />
          </Suspense>
        } />
        <Route path="products" element={
          <Suspense fallback={<Loading />}>
            <Products />
          </Suspense>
        } />
        {/* Otras rutas... */}
      </Route>
    </Routes>
  );
}
```

### 2. PWA con Vite

Añadiendo el plugin `vite-plugin-pwa`:

```bash
npm install -D vite-plugin-pwa
```

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Sistema de Gestión de Inventario',
        short_name: 'Inventario',
        theme_color: '#ffffff',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
});
```

## Solución de problemas comunes

### 1. Errores de importación

**Problema**: Importaciones que no se resuelven correctamente.

**Solución**: Verificar la configuración de alias en `vite.config.ts`:

```typescript
resolve: {
  alias: {
    '@': resolve(__dirname, './src')
  }
}
```

### 2. Problemas con Hot Module Replacement

**Problema**: Los cambios no se reflejan en tiempo real.

**Solución**:
- Verificar que el componente sea exportado como exportación por defecto
- Comprobar si hay errores en la consola
- Reiniciar el servidor de desarrollo

### 3. Rendimiento lento en desarrollo

**Problema**: La aplicación se vuelve lenta con muchos componentes.

**Solución**:
- Utilizar modo de desarrollo selectivo:
  ```bash
  # Solo hot reload para los componentes que estás trabajando
  npx vite --force
  ```

## Mejores prácticas

1. **Estructura modular**:
   ```
   src/
   ├── features/          # Características organizadas por dominio
   │   ├── products/      # Todo lo relacionado con productos
   │   ├── inventory/     # Todo lo relacionado con inventario
   │   └── orders/        # Todo lo relacionado con pedidos
   ```

2. **Optimización de imágenes**:
    - Utilizar formatos modernos como WebP
    - Aprovechar la importación de activos para optimización automática:
      ```tsx
      import optimizedImage from './image.jpg?width=800&format=webp';
      ```

3. **Monitoreo de tamaño de bundle**:
   ```bash
   npm run build -- --report
   ```

4. **División de código por rutas**:
    - Cada página en una carga diferida separada
    - Componentes grandes en chunks separados

5. **Aprovechar fast refresh**:
    - Mantener estado local durante actualizaciones
    - Extraer lógica compleja a hooks para mejor HMR

## Integración con Backend FastAPI

Para una experiencia de desarrollo fluida, configuramos un proxy en desarrollo para redirigir peticiones API:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

Esto permite usar rutas relativas en el código frontend:

```typescript
// src/api/axios.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1'  // En desarrollo, se dirigirá al backend en puerto 8000
});

export default api;
```

## Conclusión

Vite proporciona a nuestro sistema de gestión de inventario un entorno de desarrollo moderno, rápido y eficiente. 
Sus principales ventajas incluyen:

1. Tiempos de inicio y recarga instantáneos gracias a ESM nativo
2. Experiencia de desarrollo mejorada con HMR rápido
3. Construcción optimizada para producción
4. Excelente integración con React, TypeScript y TailwindCSS
5. Sistema de plugins potente para extender funcionalidades
6. Soporte para varios formatos de archivos y optimizaciones automáticas