# Migration Guides

This comprehensive guide provides step-by-step instructions for migrating React applications across different versions and architectural patterns. Whether you're upgrading to the latest React version, modernizing class components to hooks, or migrating away from legacy APIs, these guides will help ensure a smooth transition while maintaining application stability and performance.

## Upgrading to Latest Version

### Pre-Migration Assessment

Before upgrading React, conduct a thorough assessment of your current application:

**Dependency Analysis**
```bash
# Check current React version
npm list react react-dom

# Audit dependencies for compatibility
npm audit
npx npm-check-updates --target minor
```

**Codebase Evaluation**
- Identify deprecated APIs and patterns
- Review third-party library compatibility
- Assess TypeScript version compatibility
- Document custom webpack configurations

### Version-Specific Migration Paths

#### Upgrading from React 17 to React 18

**1. Update Dependencies**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

**2. Update Root Rendering**
```javascript
// Before (React 17)
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));

// After (React 18)
import { createRoot } from 'react-dom/client';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
```

**3. TypeScript Configuration Updates**
```typescript
// types/react-dom.d.ts
declare module 'react-dom/client' {
  export interface Root {
    render(children: React.ReactChild | React.ReactFragment | React.ReactPortal | boolean | null | undefined): void;
    unmount(): void;
  }
  export function createRoot(container: Element | DocumentFragment): Root;
}
```

**4. Concurrent Features Integration**
```javascript
// Enable concurrent features
import { createRoot } from 'react-dom/client';
import { startTransition } from 'react';

// Wrap state updates in transitions
const handleSearch = (query) => {
  startTransition(() => {
    setSearchQuery(query);
  });
};

// Use Suspense for data fetching
function App() {
  return (
    <Suspense fallback={<Loading />}>
      <SearchResults />
    </Suspense>
  );
}
```

#### Next.js Integration Updates

**Update Next.js Configuration**
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Enable React 18 features
    reactRoot: true,
    runtime: 'nodejs',
  },
  compiler: {
    // Enable SWC compiler for better performance
    styledComponents: true,
  }
};

module.exports = nextConfig;
```

**Server-Side Rendering Updates**
```javascript
// pages/_app.js
import { Suspense } from 'react';

function MyApp({ Component, pageProps }) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Component {...pageProps} />
    </Suspense>
  );
}

export default MyApp;
```

### Breaking Changes and Compatibility

**Automatic Batching**
```javascript
// React 18 automatically batches these updates
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React will only re-render once at the end (batching)
}

// To opt out of batching when needed
import { flushSync } from 'react-dom';

function handleClick() {
  flushSync(() => {
    setCount(c => c + 1);
  });
  // React has updated the DOM by now
  flushSync(() => {
    setFlag(f => !f);
  });
  // React has updated the DOM by now
}
```

**Stricter StrictMode**
```javascript
// Components may be mounted, unmounted, and remounted
useEffect(() => {
  const subscription = subscribe();
  return () => subscription.unsubscribe();
}, []); // Ensure cleanup is properly handled
```

## Class to Hooks Migration

### Migration Strategy

**Phase 1: Assessment and Planning**
1. Identify class components for migration
2. Analyze component complexity and dependencies
3. Plan migration order (leaf components first)
4. Set up testing infrastructure

**Phase 2: Systematic Migration**
1. Convert simple class components
2. Migrate complex state logic
3. Handle lifecycle methods
4. Update parent-child relationships

### Basic Class to Hooks Conversion

#### State Migration
```javascript
// Before: Class Component
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
      loading: true,
      error: null
    };
  }

  render() {
    const { user, loading, error } = this.state;
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    
    return <div>Welcome, {user.name}!</div>;
  }
}

// After: Functional Component with Hooks
import { useState } from 'react';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>Welcome, {user.name}!</div>;
}
```

#### Lifecycle Methods Migration

**componentDidMount → useEffect**
```javascript
// Before
class DataFetcher extends React.Component {
  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const data = await response.json();
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error, loading: false });
    }
  };
}

// After
import { useState, useEffect } from 'react';

function DataFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data');
        const data = await response.json();
        setData(data);
        setLoading(false);
      } catch (error) {
        setError(error);
        setLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array = componentDidMount

  // Component logic...
}
```

**componentDidUpdate → useEffect with Dependencies**
```javascript
// Before
class SearchComponent extends React.Component {
  componentDidUpdate(prevProps) {
    if (prevProps.searchTerm !== this.props.searchTerm) {
      this.performSearch(this.props.searchTerm);
    }
  }
}

// After
import { useEffect } from 'react';

function SearchComponent({ searchTerm }) {
  useEffect(() => {
    performSearch(searchTerm);
  }, [searchTerm]); // Runs when searchTerm changes

  const performSearch = (term) => {
    // Search logic
  };
}
```

**componentWillUnmount → useEffect Cleanup**
```javascript
// Before
class TimerComponent extends React.Component {
  componentDidMount() {
    this.timer = setInterval(() => {
      this.setState({ time: Date.now() });
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.timer);
  }
}

// After
import { useState, useEffect } from 'react';

function TimerComponent() {
  const [time, setTime] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(Date.now());
    }, 1000);

    return () => clearInterval(timer); // Cleanup function
  }, []);
}
```

### Advanced Migration Patterns

#### Custom Hooks for Complex Logic
```javascript
// Extract complex logic into custom hooks
function useUserData(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        
        if (!cancelled) {
          setUser(userData);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { user, loading, error };
}

// Usage in component
function UserProfile({ userId }) {
  const { user, loading, error } = useUserData(userId);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>Welcome, {user.name}!</div>;
}
```

#### Context Migration
```javascript
// Before: Class-based context consumption
class ThemeConsumer extends React.Component {
  static contextType = ThemeContext;

  render() {
    const theme = this.context;
    return <div style={{ color: theme.color }}>Themed content</div>;
  }
}

// After: Hook-based context consumption
import { useContext } from 'react';

function ThemeConsumer() {
  const theme = useContext(ThemeContext);
  return <div style={{ color: theme.color }}>Themed content</div>;
}
```

### TypeScript Migration Considerations

```typescript
// Define proper types for hooks
interface User {
  id: string;
  name: string;
  email: string;
}

interface UserState {
  user: User | null;
  loading: boolean;
  error: Error | null;
}

function useUser(userId: string): UserState {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Implementation with proper error handling
  }, [userId]);

  return { user, loading, error };
}
```

## Legacy API Migration

### Deprecated APIs and Modern Alternatives

#### String Refs to useRef
```javascript
// Before: String refs (deprecated)
class MyComponent extends React.Component {
  handleClick = () => {
    this.refs.myInput.focus();
  };

  render() {
    return (
      <div>
        <input ref="myInput" />
        <button onClick={this.handleClick}>Focus Input</button>
      </div>
    );
  }
}

// After: useRef hook
import { useRef } from 'react';

function MyComponent() {
  const inputRef = useRef(null);

  const handleClick = () => {
    inputRef.current?.focus();
  };

  return (
    <div>
      <input ref={inputRef} />
      <button onClick={handleClick}>Focus Input</button>
    </div>
  );
}
```

#### Legacy Context API to Modern Context
```javascript
// Before: Legacy Context API
class LegacyProvider extends React.Component {
  static childContextTypes = {
    theme: PropTypes.object
  };

  getChildContext() {
    return { theme: this.props.theme };
  }

  render() {
    return this.props.children;
  }
}

// After: Modern Context API
import { createContext, useContext } from 'react';

const ThemeContext = createContext();

function ThemeProvider({ theme, children }) {
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

#### UNSAFE Lifecycle Methods Migration
```javascript
// Before: UNSAFE_componentWillReceiveProps
class UserList extends React.Component {
  UNSAFE_componentWillReceiveProps(nextProps) {
    if (nextProps.userId !== this.props.userId) {
      this.setState({ loading: true });
      this.fetchUser(nextProps.userId);
    }
  }
}

// After: getDerivedStateFromProps + useEffect
import { useState, useEffect } from 'react';

function UserList({ userId }) {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchUser(userId).then(userData => {
      setUser(userData);
      setLoading(false);
    });
  }, [userId]);

  const fetchUser = async (id) => {
    // Fetch implementation
  };

  // Component render logic
}
```

### Webpack and Build Tool Migration

#### Webpack Configuration Updates
```javascript
// webpack.config.js - React 18 optimizations
const path = require('path');

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true,
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          chunks: 'all',
        },
      },
    },
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              ['@babel/preset-react', { runtime: 'automatic' }],
              '@babel/preset-typescript',
            ],
          },
        },
      },
    ],
  },
};
```

### Testing Migration

#### Enzyme to React Testing Library
```javascript
// Before: Enzyme
import { shallow } from 'enzyme';

describe('UserProfile', () => {
  it('displays user name', () => {
    const wrapper = shallow(<UserProfile user={{ name: 'John' }} />);
    expect(wrapper.find('.user-name').text()).toBe('John');
  });
});

// After: React Testing Library
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('UserProfile', () => {
  it('displays user name', () => {
    render(<UserProfile user={{ name: 'John' }} />);