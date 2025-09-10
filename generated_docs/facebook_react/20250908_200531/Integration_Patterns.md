# Integration Patterns

React's component-based architecture provides exceptional flexibility for integrating with various frameworks, libraries, and backend services. This section outlines proven integration patterns that enable React applications to work seamlessly within complex technical ecosystems while maintaining code quality, performance, and maintainability.

## Next.js Integration

Next.js represents one of the most sophisticated React integration patterns, providing a full-stack framework that enhances React with server-side rendering, static site generation, and advanced routing capabilities.

### Framework Setup and Configuration

Next.js integration begins with proper project initialization and configuration. The framework extends React's capabilities through a convention-over-configuration approach:

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack configuration for React components
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
};

module.exports = nextConfig;
```

### Server-Side Rendering Patterns

Next.js provides multiple rendering strategies that integrate seamlessly with React components:

```typescript
// pages/products/[id].tsx
import { GetServerSideProps, GetStaticProps, GetStaticPaths } from 'next';
import { ReactElement } from 'react';

interface ProductProps {
  product: {
    id: string;
    name: string;
    description: string;
  };
}

// Server-Side Rendering (SSR)
export const getServerSideProps: GetServerSideProps<ProductProps> = async (context) => {
  const { id } = context.params!;
  
  try {
    const response = await fetch(`${process.env.API_BASE_URL}/products/${id}`);
    const product = await response.json();
    
    return {
      props: {
        product,
      },
    };
  } catch (error) {
    return {
      notFound: true,
    };
  }
};

// Static Site Generation (SSG)
export const getStaticProps: GetStaticProps<ProductProps> = async ({ params }) => {
  const product = await fetchProduct(params!.id as string);
  
  return {
    props: {
      product,
    },
    revalidate: 3600, // Incremental Static Regeneration
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  const products = await fetchAllProducts();
  
  return {
    paths: products.map((product) => ({
      params: { id: product.id },
    })),
    fallback: 'blocking',
  };
};

const ProductPage = ({ product }: ProductProps): ReactElement => {
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
    </div>
  );
};

export default ProductPage;
```

### API Routes Integration

Next.js API routes provide seamless backend integration within the React application structure:

```typescript
// pages/api/products/[id].ts
import { NextApiRequest, NextApiResponse } from 'next';
import { z } from 'zod';

const productSchema = z.object({
  name: z.string().min(1),
  description: z.string(),
  price: z.number().positive(),
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { id } = req.query;

  switch (req.method) {
    case 'GET':
      try {
        const product = await getProductById(id as string);
        res.status(200).json(product);
      } catch (error) {
        res.status(404).json({ error: 'Product not found' });
      }
      break;

    case 'PUT':
      try {
        const validatedData = productSchema.parse(req.body);
        const updatedProduct = await updateProduct(id as string, validatedData);
        res.status(200).json(updatedProduct);
      } catch (error) {
        res.status(400).json({ error: 'Invalid product data' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'PUT']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

### App Router Integration (Next.js 13+)

The new App Router provides enhanced integration patterns with React Server Components:

```typescript
// app/products/[id]/page.tsx
import { Suspense } from 'react';
import { ProductDetails } from '@/components/ProductDetails';
import { ProductReviews } from '@/components/ProductReviews';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface PageProps {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function ProductPage({ params, searchParams }: PageProps) {
  // Server Component - runs on server
  const product = await fetchProduct(params.id);

  return (
    <div>
      <ProductDetails product={product} />
      <Suspense fallback={<LoadingSpinner />}>
        <ProductReviews productId={params.id} />
      </Suspense>
    </div>
  );
}

// app/products/[id]/loading.tsx
export default function Loading() {
  return <LoadingSpinner />;
}

// app/products/[id]/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

## State Management Libraries

React's integration with state management libraries requires careful consideration of data flow, performance implications, and architectural patterns.

### Redux Toolkit Integration

Redux Toolkit provides the modern standard for Redux integration with React:

```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { productsApi } from './api/productsApi';
import authSlice from './slices/authSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    ui: uiSlice,
    [productsApi.reducerPath]: productsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(productsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

```typescript
// store/slices/authSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: null,
  loading: false,
  error: null,
};

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
```

### RTK Query Integration

RTK Query provides powerful data fetching and caching capabilities:

```typescript
// store/api/productsApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../index';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
}

export const productsApi = createApi({
  reducerPath: 'productsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/products',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Product'],
  endpoints: (builder) => ({
    getProducts: builder.query<Product[], { category?: string; limit?: number }>({
      query: ({ category, limit = 10 }) => ({
        url: '',
        params: { category, limit },
      }),
      providesTags: ['Product'],
    }),
    getProduct: builder.query<Product, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Product', id }],
    }),
    createProduct: builder.mutation<Product, Partial<Product>>({
      query: (newProduct) => ({
        url: '',
        method: 'POST',
        body: newProduct,
      }),
      invalidatesTags: ['Product'],
    }),
    updateProduct: builder.mutation<Product, { id: string; updates: Partial<Product> }>({
      query: ({ id, updates }) => ({
        url: `/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Product', id }],
    }),
  }),
});

export const {
  useGetProductsQuery,
  useGetProductQuery,
  useCreateProductMutation,
  useUpdateProductMutation,
} = productsApi;
```

### Zustand Integration

Zustand offers a lightweight alternative for state management:

```typescript
// store/useProductStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface Product {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface ProductStore {
  products: Product[];
  cart: Product[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchProducts: () => Promise<void>;
  addToCart: (product: Product) => void;
  removeFromCart: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

export const useProductStore = create<ProductStore>()(
  devtools(
    persist(
      immer((set, get) => ({
        products: [],
        cart: [],
        loading: false,
        error: null,

        fetchProducts: async () => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const response = await fetch('/api/products');
            const products = await response.json();
            
            set((state) => {
              state.products = products;
              state.loading = false;
            });
          } catch (error) {
            set((state) => {
              state.error = error.message;
              state.loading = false;
            });
          }
        },

        addToCart: (product) => {
          set((state) => {
            const existingItem = state.cart.find(item => item.id === product.id);
            if (existingItem) {
              existingItem.quantity += 1;
            } else {
              state.cart.push({ ...product, quantity: 1 });
            }
          });
        },

        removeFromCart: (productId) => {
          set((state) => {
            state.cart = state.cart.filter(item => item.id !== productId);
          });
        },

        updateQuantity: (productId, quantity) => {
          set((state) => {
            const item = state.cart.find(item => item.id === productId);
            if (item) {
              item.quantity = quantity;
            }
          });
        },

        clearCart: () => {
          set((state) => {
            state.cart = [];
          });
        },
      })),
      {
        name: 'product-store',
        partialize: (state) => ({ cart: state.cart }),
      }
    )
  )
);
```

## Backend Integration

React applications require robust patterns for integrating with various backend services, APIs, and data sources.

### RESTful API Integration

Modern React applications use sophisticated patterns for REST API integration:

```typescript
// services/apiClient.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refreshToken');
            const response = await this.client.post('/auth/