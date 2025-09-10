# TypeScript Integration

TypeScript integration with React provides enhanced developer experience through static type checking, improved IDE support, and better code maintainability. This comprehensive guide covers the essential aspects of implementing TypeScript in React applications, from initial setup to advanced patterns.

## Setting up React with TypeScript

### Creating a New TypeScript React Project

The most straightforward approach to start a React project with TypeScript is using Create React App with the TypeScript template:

```bash
npx create-react-app my-app --template typescript
cd my-app
npm start
```

This command generates a project structure with pre-configured TypeScript settings, including:

- `tsconfig.json` - TypeScript compiler configuration
- Type definitions for React (`@types/react`, `@types/react-dom`)
- Sample TypeScript React components
- Webpack configuration optimized for TypeScript

### Manual TypeScript Setup

For existing React projects or custom configurations, manual setup involves several steps:

1. **Install TypeScript and type definitions:**

```bash
npm install --save-dev typescript @types/react @types/react-dom @types/node
```

2. **Create `tsconfig.json` configuration:**

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "esnext"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}
```

3. **Configure build tools:**

For Webpack configurations, ensure the TypeScript loader is properly configured:

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
};
```

### Next.js TypeScript Integration

Next.js provides built-in TypeScript support. To enable it:

1. Create a `tsconfig.json` file in your project root
2. Install TypeScript dependencies:

```bash
npm install --save-dev typescript @types/react @types/node
```

3. Next.js will automatically configure TypeScript on the next build or development server start.

## Typing Components

### Function Components

Modern React development primarily uses function components, which can be typed in several ways:

**Method 1: Explicit typing with React.FC**

```typescript
import React from 'react';

interface UserCardProps {
  name: string;
  email: string;
  age?: number;
}

const UserCard: React.FC<UserCardProps> = ({ name, email, age }) => {
  return (
    <div className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      {age && <p>Age: {age}</p>}
    </div>
  );
};

export default UserCard;
```

**Method 2: Direct function typing (recommended)**

```typescript
import React from 'react';

interface UserCardProps {
  name: string;
  email: string;
  age?: number;
}

const UserCard = ({ name, email, age }: UserCardProps) => {
  return (
    <div className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      {age && <p>Age: {age}</p>}
    </div>
  );
};

export default UserCard;
```

### Class Components

While less common in modern React, class components require specific typing patterns:

```typescript
import React, { Component } from 'react';

interface CounterProps {
  initialCount?: number;
  onCountChange?: (count: number) => void;
}

interface CounterState {
  count: number;
}

class Counter extends Component<CounterProps, CounterState> {
  constructor(props: CounterProps) {
    super(props);
    this.state = {
      count: props.initialCount || 0
    };
  }

  handleIncrement = (): void => {
    this.setState(
      prevState => ({ count: prevState.count + 1 }),
      () => {
        this.props.onCountChange?.(this.state.count);
      }
    );
  };

  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.handleIncrement}>Increment</button>
      </div>
    );
  }
}

export default Counter;
```

## Typing Props and State

### Advanced Props Patterns

**Union Types for Props**

```typescript
interface BaseButtonProps {
  children: React.ReactNode;
  disabled?: boolean;
}

interface PrimaryButtonProps extends BaseButtonProps {
  variant: 'primary';
  color: 'blue' | 'green' | 'red';
}

interface SecondaryButtonProps extends BaseButtonProps {
  variant: 'secondary';
  outline?: boolean;
}

type ButtonProps = PrimaryButtonProps | SecondaryButtonProps;

const Button = (props: ButtonProps) => {
  const { children, disabled, variant } = props;
  
  if (variant === 'primary') {
    // TypeScript knows this is PrimaryButtonProps
    const { color } = props;
    return (
      <button 
        disabled={disabled} 
        className={`btn-primary btn-${color}`}
      >
        {children}
      </button>
    );
  }
  
  // TypeScript knows this is SecondaryButtonProps
  const { outline } = props;
  return (
    <button 
      disabled={disabled} 
      className={`btn-secondary ${outline ? 'outline' : ''}`}
    >
      {children}
    </button>
  );
};
```

**Generic Props**

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}

// Usage
const users = [
  { id: 1, name: 'John', email: 'john@example.com' },
  { id: 2, name: 'Jane', email: 'jane@example.com' }
];

<List
  items={users}
  keyExtractor={(user) => user.id}
  renderItem={(user) => <span>{user.name} - {user.email}</span>}
/>
```

### Complex State Management

**Discriminated Unions for State**

```typescript
interface LoadingState {
  status: 'loading';
}

interface SuccessState {
  status: 'success';
  data: User[];
}

interface ErrorState {
  status: 'error';
  error: string;
}

type AsyncState = LoadingState | SuccessState | ErrorState;

const UserList = () => {
  const [state, setState] = useState<AsyncState>({ status: 'loading' });

  const fetchUsers = async () => {
    setState({ status: 'loading' });
    try {
      const response = await fetch('/api/users');
      const data = await response.json();
      setState({ status: 'success', data });
    } catch (error) {
      setState({ 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  };

  if (state.status === 'loading') {
    return <div>Loading...</div>;
  }

  if (state.status === 'error') {
    return <div>Error: {state.error}</div>;
  }

  // TypeScript knows state.data exists here
  return (
    <ul>
      {state.data.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};
```

## Typing Hooks

### useState Hook

```typescript
// Primitive types (inferred)
const [count, setCount] = useState(0); // number
const [name, setName] = useState(''); // string

// Explicit typing for complex types
interface User {
  id: number;
  name: string;
  email: string;
}

const [user, setUser] = useState<User | null>(null);

// Array types
const [users, setUsers] = useState<User[]>([]);

// Function updates with proper typing
const updateUser = (updates: Partial<User>) => {
  setUser(prevUser => 
    prevUser ? { ...prevUser, ...updates } : null
  );
};
```

### useEffect Hook

```typescript
import { useEffect, useRef } from 'react';

const DataFetcher = ({ userId }: { userId: number }) => {
  const [user, setUser] = useState<User | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      // Cancel previous request
      abortControllerRef.current?.abort();
      
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const response = await fetch(`/api/users/${userId}`, {
          signal: controller.signal
        });
        const userData: User = await response.json();
        setUser(userData);
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          console.error('Failed to fetch user:', error);
        }
      }
    };

    fetchUser();

    // Cleanup function
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [userId]);

  return user ? <UserCard {...user} /> : <div>Loading...</div>;
};
```

### Custom Hooks

```typescript
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result: T = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Usage
const UserProfile = ({ userId }: { userId: number }) => {
  const { data: user, loading, error, refetch } = useApi<User>(`/api/users/${userId}`);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>No user found</div>;

  return <UserCard {...user} onRefresh={refetch} />;
};
```

## Advanced TypeScript Patterns

### Higher-Order Components (HOCs)

```typescript
interface WithLoadingProps {
  loading: boolean;
}

function withLoading<P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P & WithLoadingProps> {
  return (props: P & WithLoadingProps) => {
    const { loading, ...restProps } = props;
    
    if (loading) {
      return <div>Loading...</div>;
    }
    
    return <Component {...(restProps as P)} />;
  };
}

// Usage
const UserCard = ({ name, email }: { name: string; email: string }) => (
  <div>
    <h3>{name}</h3>
    <p>{email}</p>
  </div>
);

const UserCardWithLoading = withLoading(UserCard);

// Component usage
<UserCardWithLoading 
  name="John Doe" 
  email="john@example.com" 
  loading={false} 
/>
```

### Render Props Pattern

```typescript
interface RenderPropsComponentProps<T> {
  children: (data: T, loading: boolean, error: string | null) => React.ReactNode;
  url: string;
}

function DataProvider<T>({ children, url }: RenderPropsComponentProps<T>) {
  const { data, loading, error } = useApi<T>(url);
  return <>{children(data, loading, error)}</>;
}

// Usage
<DataProvider<User[]> url="/api/users">
  {(users, loading, error) => {
    if (loading) return <div>Loading users...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!users) return <div>No users found</div>;
    
    return (
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    );
  }}
</DataProvider>
```

### Context API with TypeScript

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const userData: User = await response.json();
      setUser(userData);
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = (): void => {
    setUser(null);
  };

  const value: AuthContextType = {
    user,