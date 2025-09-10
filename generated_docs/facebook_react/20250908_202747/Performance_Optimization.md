# Performance Optimization

Performance optimization is crucial for delivering exceptional user experiences in React applications. This section covers essential techniques and strategies for optimizing React applications, from component-level optimizations to bundle size reduction and profiling techniques.

## React.memo

React.memo is a higher-order component that provides memoization for functional components, preventing unnecessary re-renders when props haven't changed. It performs a shallow comparison of props by default and only re-renders the component if the props have actually changed.

### Basic Usage

```javascript
import React, { memo } from 'react';

const ExpensiveComponent = memo(({ name, age, items }) => {
  console.log('ExpensiveComponent rendered');
  
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
});

export default ExpensiveComponent;
```

### Custom Comparison Function

For more complex scenarios, you can provide a custom comparison function as the second argument to React.memo:

```javascript
const MyComponent = memo(({ user, settings }) => {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>Theme: {settings.theme}</p>
    </div>
  );
}, (prevProps, nextProps) => {
  // Return true if props are equal (skip re-render)
  // Return false if props are different (re-render)
  return (
    prevProps.user.id === nextProps.user.id &&
    prevProps.settings.theme === nextProps.settings.theme
  );
});
```

### Best Practices for React.memo

- **Use sparingly**: Only apply React.memo to components that actually have performance issues
- **Profile first**: Use React DevTools Profiler to identify components that re-render frequently
- **Consider prop complexity**: React.memo is most effective with components that receive simple props
- **Avoid with frequently changing props**: Don't use React.memo on components whose props change on every render

### Common Pitfalls

```javascript
// ❌ Bad: Object props will always trigger re-renders
const Parent = () => {
  return (
    <MemoizedChild 
      style={{ color: 'red' }} // New object on every render
      onClick={() => console.log('clicked')} // New function on every render
    />
  );
};

// ✅ Good: Stable references
const Parent = () => {
  const style = useMemo(() => ({ color: 'red' }), []);
  const handleClick = useCallback(() => console.log('clicked'), []);
  
  return (
    <MemoizedChild 
      style={style}
      onClick={handleClick}
    />
  );
};
```

## useMemo and useCallback

These hooks are essential for optimizing expensive computations and preventing unnecessary function recreations that can trigger child component re-renders.

### useMemo Hook

`useMemo` memoizes the result of expensive calculations and only recalculates when dependencies change:

```javascript
import React, { useMemo, useState } from 'react';

const DataProcessor = ({ items, filter, sortBy }) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Expensive computation that should only run when dependencies change
  const processedData = useMemo(() => {
    console.log('Processing data...');
    
    return items
      .filter(item => item.category === filter)
      .filter(item => item.name.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => {
        if (sortBy === 'name') return a.name.localeCompare(b.name);
        if (sortBy === 'date') return new Date(b.date) - new Date(a.date);
        return 0;
      });
  }, [items, filter, searchTerm, sortBy]);

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search items..."
      />
      <ul>
        {processedData.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
};
```

### useCallback Hook

`useCallback` memoizes function references to prevent child component re-renders:

```javascript
import React, { useCallback, useState } from 'react';

const TodoApp = () => {
  const [todos, setTodos] = useState([]);
  const [filter, setFilter] = useState('all');

  // Memoized callback functions
  const addTodo = useCallback((text) => {
    setTodos(prev => [...prev, { id: Date.now(), text, completed: false }]);
  }, []);

  const toggleTodo = useCallback((id) => {
    setTodos(prev => prev.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  }, []);

  const deleteTodo = useCallback((id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  }, []);

  const filteredTodos = useMemo(() => {
    switch (filter) {
      case 'active':
        return todos.filter(todo => !todo.completed);
      case 'completed':
        return todos.filter(todo => todo.completed);
      default:
        return todos;
    }
  }, [todos, filter]);

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <TodoList 
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
      />
      <FilterButtons filter={filter} onFilterChange={setFilter} />
    </div>
  );
};
```

### Advanced useMemo Patterns

```javascript
// Complex object memoization
const UserProfile = ({ user, permissions, settings }) => {
  const userContext = useMemo(() => ({
    ...user,
    canEdit: permissions.includes('edit'),
    canDelete: permissions.includes('delete'),
    displayName: `${user.firstName} ${user.lastName}`,
    theme: settings.theme || 'light'
  }), [user, permissions, settings.theme]);

  return <ProfileDisplay context={userContext} />;
};

// Memoizing expensive API transformations
const DataVisualization = ({ rawData, chartType }) => {
  const chartData = useMemo(() => {
    if (!rawData.length) return null;
    
    switch (chartType) {
      case 'line':
        return transformToLineChart(rawData);
      case 'bar':
        return transformToBarChart(rawData);
      case 'pie':
        return transformToPieChart(rawData);
      default:
        return rawData;
    }
  }, [rawData, chartType]);

  return chartData ? <Chart data={chartData} /> : <LoadingSpinner />;
};
```

## Virtual DOM and Reconciliation

Understanding React's Virtual DOM and reconciliation process is crucial for writing performant React applications. The Virtual DOM is React's in-memory representation of the real DOM, enabling efficient updates through a process called reconciliation.

### How Virtual DOM Works

The Virtual DOM operates through a three-step process:

1. **Virtual DOM Creation**: React creates a virtual representation of the DOM in memory
2. **Diffing**: React compares (diffs) the new Virtual DOM tree with the previous version
3. **Reconciliation**: React updates only the parts of the real DOM that have changed

### Reconciliation Algorithm

React uses a heuristic O(n) algorithm based on two assumptions:

- Elements of different types will produce different trees
- Developers can hint at which child elements may be stable across renders with a `key` prop

### Optimizing Reconciliation with Keys

Proper key usage is critical for efficient list rendering:

```javascript
// ❌ Bad: Using array index as key
const BadList = ({ items }) => (
  <ul>
    {items.map((item, index) => (
      <li key={index}>{item.name}</li>
    ))}
  </ul>
);

// ✅ Good: Using stable, unique identifiers
const GoodList = ({ items }) => (
  <ul>
    {items.map(item => (
      <li key={item.id}>{item.name}</li>
    ))}
  </ul>
);

// ✅ Better: Complex list with stable keys
const OptimizedList = ({ items, onEdit, onDelete }) => (
  <ul>
    {items.map(item => (
      <ListItem
        key={item.id}
        item={item}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    ))}
  </ul>
);
```

### Component Type Stability

Maintain component type stability to avoid unnecessary unmounting:

```javascript
// ❌ Bad: Conditional component types
const BadConditionalRender = ({ isEditing, data }) => {
  if (isEditing) {
    return <EditForm data={data} />;
  }
  return <DisplayView data={data} />;
};

// ✅ Good: Single component handling different states
const GoodConditionalRender = ({ isEditing, data }) => (
  <DataComponent isEditing={isEditing} data={data} />
);

// ✅ Alternative: Stable wrapper with conditional content
const StableWrapper = ({ isEditing, data }) => (
  <div className="data-wrapper">
    {isEditing ? (
      <EditForm data={data} />
    ) : (
      <DisplayView data={data} />
    )}
  </div>
);
```

### Fiber Architecture Benefits

React's Fiber architecture provides additional performance benefits:

- **Incremental Rendering**: Work can be split into chunks and spread across multiple frames
- **Prioritization**: Different types of updates can have different priorities
- **Pausable Work**: Rendering work can be paused and resumed as needed

## Profiling and Debugging

React provides powerful tools for identifying and resolving performance bottlenecks in your applications.

### React DevTools Profiler

The React DevTools Profiler is essential for performance analysis:

```javascript
// Enable profiler in development
import { Profiler } from 'react';

const onRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
  console.log('Profiler:', {
    id,           // Component tree that was rendered
    phase,        // "mount" or "update"
    actualDuration, // Time spent rendering the committed update
    baseDuration,   // Estimated time to render the entire subtree without memoization
    startTime,      // When React began rendering this update
    commitTime      // When React committed this update
  });
};

const App = () => (
  <Profiler id="App" onRender={onRenderCallback}>
    <Navigation />
    <Main />
    <Footer />
  </Profiler>
);
```

### Performance Monitoring Hooks

Create custom hooks for performance monitoring:

```javascript
import { useEffect, useRef } from 'react';

// Hook to measure component render time
const useRenderTime = (componentName) => {
  const renderStart = useRef();
  
  // Mark start of render
  renderStart.current = performance.now();
  
  useEffect(() => {
    const renderEnd = performance.now();
    const renderTime = renderEnd - renderStart.current;
    
    if (renderTime > 16) { // Flag renders longer than one frame
      console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms`);
    }
  });
};

// Hook to detect unnecessary re-renders
const useWhyDidYouUpdate = (name, props) => {
  const previous = useRef();
  
  useEffect(() => {
    if (previous.current) {
      const allKeys = Object.keys({ ...previous.current, ...props });
      const changedProps = {};
      
      allKeys.forEach(key => {
        if (previous.current[key] !== props[key]) {
          changedProps[key] = {
            from: previous.current[key],
            to: props[key]
          };
        }
      });
      
      if (Object.keys(changedProps).length) {
        console.log('[why-did-you-update]', name, changedProps);
      }
    }
    
    previous.current = props;
  });
};

// Usage example
const ExpensiveComponent = (props) => {
  useRenderTime('ExpensiveComponent');
  useWhyDidYouUpdate('ExpensiveComponent', props);
  
  return <div>{/* Component content */}</div>;
};
```

### Memory Leak Detection

Identify and prevent common memory leaks:

```javascript
import { useEffect, useRef } from 'react';

// Hook to cleanup event listeners and subscriptions
const useCleanup = () => {
  const cleanupFunctions = useRef([]);
  
  const addCleanup = (cleanupFn) => {
    cleanupFunctions.current.push(cleanupFn);
  };
  
  useEffect(() => {
    return () => {
      cleanupFunctions.current.forEach(cleanup => cleanup());
      cleanupFunctions.current = [];
    };
  }, []);
  
  return addCleanup;
};

// Example usage
const ComponentWithSubscriptions = () => {
  const addCleanup = useCleanup();
  
  useEffect(() => {
    const subscription = eventEmitter.subscribe('event', handler);
    addCleanup(() => subscription.unsubscribe());
    
    const intervalId = setInterval(updateData, 1000);
    addCleanup(() => clearInterval(intervalId));
    
    const timeoutId = setTimeout(delayedAction, 5000);
    addCleanup(() => clearTimeout(timeoutId));
  }, [addCleanup]);
  
  return <div>Component content</div>;
};
```

## Bundle Optimization

Optimizing your application bundle is crucial for reducing load times and improving user experience.

### Code Splitting with React.lazy

Implement route-based and component-based code splitting:

```javascript
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Route-based code splitting
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Component-based code splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));

const App = () => (
  <Router>
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  </Router>
);

// Conditional loading with error boundaries
const ConditionalChart = ({ showChart, data }) => (
  <div>
    {showChart && (
      <Suspense fallback={<ChartSkeleton />}>
        <ErrorBoundary fallback={<ChartError />}>
          <HeavyChart data={data} />
        </ErrorBoundary>
      </Suspense>
    )}
  </div>
);
```

### Webpack Bundle Optimization

Configure Webpack for optimal bundle splitting:

```javascript
// webpack.config.js
module.exports = {
  optimization: {
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
          