# Performance and Optimization

Performance optimization is crucial for React applications to ensure fast loading times, smooth user interactions, and efficient resource utilization. This section provides comprehensive guidance on profiling, optimizing, and bundling React applications for production environments.

## Performance Profiling

### React DevTools Profiler

The React DevTools Profiler is the primary tool for identifying performance bottlenecks in React applications. It provides detailed insights into component render times, commit phases, and interaction tracking.

#### Setting Up the Profiler

```javascript
// Enable profiler in development
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration, baseDuration, startTime, commitTime) {
  console.log('Component:', id);
  console.log('Phase:', phase);
  console.log('Actual duration:', actualDuration);
  console.log('Base duration:', baseDuration);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Navigation />
      <Main />
    </Profiler>
  );
}
```

#### Key Metrics to Monitor

- **Actual Duration**: Time spent rendering the component and its children
- **Base Duration**: Estimated time to render the entire subtree without memoization
- **Start Time**: When React began rendering this update
- **Commit Time**: When React committed this update

### Browser Performance Tools

#### Chrome DevTools Performance Tab

1. **Recording Performance**: Use the Performance tab to record user interactions
2. **Analyzing Flame Graphs**: Identify long-running tasks and JavaScript execution bottlenecks
3. **Memory Usage**: Monitor heap size and garbage collection patterns

```javascript
// Performance marking for custom measurements
performance.mark('component-render-start');
// Component rendering logic
performance.mark('component-render-end');
performance.measure('component-render', 'component-render-start', 'component-render-end');
```

#### Lighthouse Integration

Configure Lighthouse for automated performance auditing:

```json
{
  "extends": "lighthouse:default",
  "settings": {
    "onlyCategories": ["performance"],
    "skipAudits": ["uses-http2"]
  }
}
```

### Performance Monitoring in Production

#### Web Vitals Integration

```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send metrics to your analytics service
  analytics.track('Web Vital', {
    name: metric.name,
    value: metric.value,
    id: metric.id,
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

#### Custom Performance Monitoring

```javascript
// Custom hook for performance monitoring
function usePerformanceMonitor(componentName) {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 16) { // Flag renders longer than one frame
        console.warn(`Slow render detected in ${componentName}: ${renderTime}ms`);
      }
    };
  });
}
```

## Optimization Techniques

### Component-Level Optimizations

#### React.memo for Functional Components

```javascript
import React, { memo } from 'react';

const ExpensiveComponent = memo(({ data, onUpdate }) => {
  return (
    <div>
      {data.map(item => (
        <ComplexItem key={item.id} item={item} onUpdate={onUpdate} />
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function
  return prevProps.data.length === nextProps.data.length &&
         prevProps.data.every((item, index) => item.id === nextProps.data[index].id);
});
```

#### useMemo and useCallback Hooks

```javascript
import React, { useMemo, useCallback, useState } from 'react';

function DataVisualization({ rawData, filters }) {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    return rawData
      .filter(item => filters.includes(item.category))
      .map(item => ({
        ...item,
        computedValue: expensiveCalculation(item)
      }))
      .sort((a, b) => b.computedValue - a.computedValue);
  }, [rawData, filters]);

  // Memoize event handlers
  const handleItemClick = useCallback((itemId) => {
    setSelectedItem(itemId);
    trackAnalyticsEvent('item_selected', { itemId });
  }, []);

  return (
    <div>
      {processedData.map(item => (
        <DataItem
          key={item.id}
          item={item}
          onClick={handleItemClick}
        />
      ))}
    </div>
  );
}
```

#### Virtualization for Large Lists

```javascript
import { FixedSizeList as List } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

### State Management Optimizations

#### Context API Optimization

```javascript
// Split contexts to prevent unnecessary re-renders
const UserContext = createContext();
const ThemeContext = createContext();
const DataContext = createContext();

// Use multiple providers instead of one large context
function AppProviders({ children }) {
  return (
    <UserProvider>
      <ThemeProvider>
        <DataProvider>
          {children}
        </DataProvider>
      </ThemeProvider>
    </UserProvider>
  );
}

// Optimize context consumers
const UserConsumer = memo(() => {
  const user = useContext(UserContext);
  // Only re-render when user changes
  return <UserProfile user={user} />;
});
```

#### State Normalization

```javascript
// Normalize nested state structures
const initialState = {
  users: {
    byId: {},
    allIds: []
  },
  posts: {
    byId: {},
    allIds: []
  }
};

// Reducer for normalized state
function appReducer(state, action) {
  switch (action.type) {
    case 'LOAD_USERS':
      return {
        ...state,
        users: {
          byId: action.users.reduce((acc, user) => ({
            ...acc,
            [user.id]: user
          }), {}),
          allIds: action.users.map(user => user.id)
        }
      };
    default:
      return state;
  }
}
```

### Rendering Optimizations

#### Lazy Loading and Code Splitting

```javascript
import { lazy, Suspense } from 'react';

// Component-level code splitting
const Dashboard = lazy(() => import('./Dashboard'));
const Profile = lazy(() => import('./Profile'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

#### Image Optimization

```javascript
// Lazy loading images with intersection observer
function LazyImage({ src, alt, placeholder }) {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageRef, setImageRef] = useState();

  useEffect(() => {
    let observer;
    
    if (imageRef && imageSrc === placeholder) {
      observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              setImageSrc(src);
              observer.unobserve(imageRef);
            }
          });
        },
        { threshold: 0.1 }
      );
      observer.observe(imageRef);
    }
    
    return () => {
      if (observer && observer.unobserve) {
        observer.unobserve(imageRef);
      }
    };
  }, [imageRef, imageSrc, placeholder, src]);

  return (
    <img
      ref={setImageRef}
      src={imageSrc}
      alt={alt}
      loading="lazy"
    />
  );
}
```

## Bundle Optimization

### Webpack Configuration

#### Production Optimization Settings

```javascript
// webpack.config.js
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    clean: true,
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true,
          },
        },
      }),
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
    runtimeChunk: 'single',
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
};
```

#### Tree Shaking Configuration

```javascript
// Enable tree shaking for ES modules
module.exports = {
  mode: 'production',
  optimization: {
    usedExports: true,
    sideEffects: false, // or specify files with side effects
  },
  resolve: {
    mainFields: ['module', 'main'], // Prefer ES modules
  },
};

// Package.json configuration
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "./src/polyfills.js"
  ]
}
```

### Next.js Optimizations

#### Next.js Configuration

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    optimizeCss: true,
    optimizeImages: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  images: {
    domains: ['example.com'],
    formats: ['image/webp', 'image/avif'],
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack optimizations
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups.commons = {
        name: 'commons',
        chunks: 'all',
        minChunks: 2,
      };
    }
    
    return config;
  },
};

module.exports = nextConfig;
```

#### Dynamic Imports and Route-based Splitting

```javascript
// Automatic code splitting with Next.js dynamic imports
import dynamic from 'next/dynamic';

const DynamicComponent = dynamic(() => import('../components/HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // Disable server-side rendering if not needed
});

// Route-based code splitting
const AdminPanel = dynamic(() => import('../components/AdminPanel'), {
  loading: () => <AdminSkeleton />,
});
```

### Asset Optimization

#### Static Asset Optimization

```javascript
// Service Worker for caching
// sw.js
const CACHE_NAME = 'app-cache-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
  );
});
```

#### Resource Hints and Preloading

```javascript
// Preload critical resources
function ResourceHints() {
  return (
    <Head>
      <link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossOrigin="" />
      <link rel="prefetch" href="/api/user-data" />
      <link rel="preconnect" href="https://api.example.com" />
      <link rel="dns-prefetch" href="https://cdn.example.com" />
    </Head>
  );
}
```

### Performance Monitoring and Analysis

#### Bundle Analysis Tools

```bash
# Analyze bundle size
npm install --save-dev webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js

# Source map analysis
npm install --save-dev source-map-explorer
npm run build
npx source-map-explorer 'build/static/js/*.js'
```

#### Performance Budget Configuration

```javascript
// webpack.config.js - Performance budgets
module.exports = {
  performance: {
    maxAssetSize: 250000,
    maxEntrypointSize: 250000,
    hints: 'warning',
  },
};

// Lighthouse CI configuration
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.9 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 3000 }],
      },
    },
  },
};
```

## Best Practices and Common Pitfalls

### Performance Best Practices

1. **Measure First**: Always profile before optimizing
2. **Optimize Critical Path**: Focus on above-the-fold content
3. **Lazy Load Non-Critical Resources**: Defer loading of below-the-fold content
4. **Minimize Bundle Size**: Use tree shaking and code splitting
5. **Cache Effectively**: Implement proper caching strategies
6. **Monitor Continuously**: Set up performance monitoring in production

### Common Performance Pitfalls

- **Over-optimization**: Premature optimization without measurement
- **Inline Functions**: Creating new functions on every render
- **Large Context Values**: Causing unnecessary re-renders
- **Inefficient List Rendering**: Not using keys or virtualization
- **Memory Leaks**: Not cleaning up event listeners and subscriptions

## References

- [React DevTools