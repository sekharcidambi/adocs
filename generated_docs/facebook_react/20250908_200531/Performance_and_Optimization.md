# Performance and Optimization

React applications require careful attention to performance optimization to deliver exceptional user experiences. This section provides comprehensive guidance on optimizing React applications, from component-level optimizations to bundle size reduction and advanced profiling techniques.

## Performance Optimization Strategies

### Component-Level Optimizations

#### React.memo and Memoization

React.memo is a higher-order component that prevents unnecessary re-renders by memoizing the component's output based on its props.

```javascript
import React, { memo, useMemo, useCallback } from 'react';

// Basic memoization
const ExpensiveComponent = memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      computed: heavyComputation(item)
    }));
  }, [data]);

  const handleClick = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id} onClick={() => handleClick(item.id)}>
          {item.name}: {item.computed}
        </div>
      ))}
    </div>
  );
});

// Custom comparison function for complex props
const ComplexComponent = memo(({ user, settings }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  return prevProps.user.id === nextProps.user.id &&
         JSON.stringify(prevProps.settings) === JSON.stringify(nextProps.settings);
});
```

#### Hooks Optimization

Proper use of React hooks can significantly impact performance:

```javascript
import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

const OptimizedComponent = ({ items, filter }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const debounceRef = useRef();

  // Memoize expensive filtering operations
  const filteredItems = useMemo(() => {
    return items.filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      item.category === filter
    );
  }, [items, searchTerm, filter]);

  // Debounced search to prevent excessive API calls
  const debouncedSearch = useCallback((term) => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchTerm(term);
    }, 300);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => clearTimeout(debounceRef.current);
  }, []);

  return (
    <div>
      <input 
        onChange={(e) => debouncedSearch(e.target.value)}
        placeholder="Search items..."
      />
      {filteredItems.map(item => (
        <ItemComponent key={item.id} item={item} />
      ))}
    </div>
  );
};
```

### Virtual Scrolling and Windowing

For large datasets, implement virtual scrolling to render only visible items:

```javascript
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ItemComponent item={items[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

### Code Splitting and Lazy Loading

Implement dynamic imports and lazy loading to reduce initial bundle size:

```javascript
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Lazy load components
const Dashboard = lazy(() => import('./components/Dashboard'));
const Profile = lazy(() => import('./components/Profile'));
const Analytics = lazy(() => 
  import('./components/Analytics').then(module => ({
    default: module.Analytics
  }))
);

const App = () => {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Suspense>
    </Router>
  );
};
```

### State Management Optimization

Optimize state updates and context usage:

```javascript
import React, { createContext, useContext, useReducer, useMemo } from 'react';

// Split contexts to prevent unnecessary re-renders
const UserContext = createContext();
const ThemeContext = createContext();

const AppProvider = ({ children }) => {
  const [userState, userDispatch] = useReducer(userReducer, initialUserState);
  const [themeState, themeDispatch] = useReducer(themeReducer, initialThemeState);

  // Memoize context values to prevent recreation
  const userValue = useMemo(() => ({
    state: userState,
    dispatch: userDispatch
  }), [userState]);

  const themeValue = useMemo(() => ({
    state: themeState,
    dispatch: themeDispatch
  }), [themeState]);

  return (
    <UserContext.Provider value={userValue}>
      <ThemeContext.Provider value={themeValue}>
        {children}
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
};
```

## Profiling and Debugging

### React DevTools Profiler

The React DevTools Profiler helps identify performance bottlenecks:

```javascript
import { Profiler } from 'react';

const onRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
  console.log('Profiler data:', {
    id,
    phase, // 'mount' or 'update'
    actualDuration, // Time spent rendering
    baseDuration, // Estimated time without memoization
    startTime,
    commitTime
  });
};

const ProfiledComponent = () => {
  return (
    <Profiler id="ExpensiveComponent" onRender={onRenderCallback}>
      <ExpensiveComponent />
    </Profiler>
  );
};
```

### Performance Monitoring

Implement custom performance monitoring:

```javascript
class PerformanceMonitor {
  static measureRender(componentName, renderFunction) {
    const startTime = performance.now();
    const result = renderFunction();
    const endTime = performance.now();
    
    console.log(`${componentName} render time: ${endTime - startTime}ms`);
    
    // Send to analytics service
    if (endTime - startTime > 16) { // Longer than one frame
      this.reportSlowRender(componentName, endTime - startTime);
    }
    
    return result;
  }

  static reportSlowRender(componentName, duration) {
    // Send to monitoring service
    fetch('/api/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'slow_render',
        component: componentName,
        duration,
        timestamp: Date.now()
      })
    });
  }
}

// Usage in components
const MonitoredComponent = () => {
  return PerformanceMonitor.measureRender('MonitoredComponent', () => {
    // Component rendering logic
    return <div>Component content</div>;
  });
};
```

### Memory Leak Detection

Identify and prevent memory leaks:

```javascript
import { useEffect, useRef } from 'react';

const useMemoryLeakDetection = (componentName) => {
  const mountTime = useRef(Date.now());
  const timers = useRef(new Set());
  const listeners = useRef(new Set());

  const addTimer = (timerId) => {
    timers.current.add(timerId);
  };

  const addListener = (element, event, handler) => {
    element.addEventListener(event, handler);
    listeners.current.add({ element, event, handler });
  };

  useEffect(() => {
    return () => {
      // Cleanup timers
      timers.current.forEach(timerId => clearTimeout(timerId));
      
      // Cleanup listeners
      listeners.current.forEach(({ element, event, handler }) => {
        element.removeEventListener(event, handler);
      });

      const lifetime = Date.now() - mountTime.current;
      console.log(`${componentName} lifetime: ${lifetime}ms`);
    };
  }, [componentName]);

  return { addTimer, addListener };
};
```

## Bundle Size Optimization

### Webpack Configuration

Optimize your Webpack configuration for production builds:

```javascript
// webpack.config.js
const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    clean: true
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    usedExports: true,
    sideEffects: false
  },
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false
    }),
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8
    })
  ]
};
```

### Tree Shaking Optimization

Configure your project for effective tree shaking:

```javascript
// package.json
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "./src/polyfills.js"
  ]
}

// Import only what you need
import { debounce, throttle } from 'lodash-es';
// Instead of: import _ from 'lodash';

// Use babel-plugin-import for automatic tree shaking
// .babelrc
{
  "plugins": [
    ["import", {
      "libraryName": "antd",
      "libraryDirectory": "es",
      "style": "css"
    }]
  ]
}
```

### Next.js Optimization

Leverage Next.js built-in optimizations:

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    optimizeCss: true,
    modern: true
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack optimizations
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups.framework = {
        chunks: 'all',
        name: 'framework',
        test: /(?<!node_modules.*)[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types|use-subscription)[\\/]/,
        priority: 40,
        enforce: true
      };
    }
    return config;
  },
  images: {
    domains: ['example.com'],
    formats: ['image/webp', 'image/avif']
  }
};

module.exports = nextConfig;

// pages/_app.js - Optimize font loading
import { Inter } from '@next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
});

export default function App({ Component, pageProps }) {
  return (
    <main className={inter.variable}>
      <Component {...pageProps} />
    </main>
  );
}
```

### Dynamic Imports and Code Splitting

Implement strategic code splitting:

```javascript
// Dynamic imports with loading states
const DynamicComponent = dynamic(
  () => import('./HeavyComponent'),
  {
    loading: () => <Skeleton />,
    ssr: false // Disable server-side rendering if not needed
  }
);

// Conditional loading
const ConditionalComponent = ({ shouldLoad }) => {
  const [Component, setComponent] = useState(null);

  useEffect(() => {
    if (shouldLoad && !Component) {
      import('./ConditionalFeature').then(module => {
        setComponent(() => module.default);
      });
    }
  }, [shouldLoad, Component]);

  return Component ? <Component /> : null;
};
```

### Performance Budgets

Set up performance budgets to maintain optimization:

```javascript
// webpack.config.js
module.exports = {
  performance: {
    maxAssetSize: 250000,
    maxEntrypointSize: 250000,
    hints: 'warning'
  }
};

// lighthouse-budget.json
[
  {
    "path": "/*",
    "timings": [
      {
        "metric": "first-contentful-paint",
        "budget": 2000
      },
      {
        "metric": "largest-contentful-paint",
        "budget": 2500
      }
    ],
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 300
      },
      {
        "resourceType": "total",
        "budget": 500
      }
    ]
  }
]
```

## Best Practices Summary

1. **Component Optimization**: Use React.memo, useMemo, and useCallback judiciously
2. **Bundle Analysis**: Regularly analyze bundle size with webpack-bundle-analyzer
3. **Code Splitting**: Implement route-based and component-based code splitting
4. **Performance Monitoring**: Set up continuous performance monitoring
5. **Tree Shaking**: Ensure proper tree shaking configuration
6. **Image Optimization**: Use Next.js Image component or similar solutions
7. **Caching Strategies**: Implement proper caching at multiple levels
8. **Performance Budgets**: Establish and maintain performance budgets

## References

- [React Performance Documentation](https://reactjs.org/docs/optimizing-performance.html)
- [Web Vitals](https://web.dev/vitals/)
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [React DevTools Profiler](https://reactjs.org/blog/2018/09/10/introducing-the-react-profiler.html)
- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)