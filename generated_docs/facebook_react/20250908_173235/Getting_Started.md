# Getting Started

Welcome to React, the powerful JavaScript library for building user interfaces. This comprehensive guide will walk you through everything you need to know to get started with React development, from initial setup to creating your first application.

React revolutionizes web development by introducing a component-based architecture that promotes reusability, maintainability, and efficient rendering through its virtual DOM implementation. Whether you're building simple interactive components or complex single-page applications, React provides the foundation for modern web development.

## Installation

### Prerequisites

Before installing React, ensure your development environment meets the following requirements:

- **Node.js**: Version 14.0.0 or higher (LTS recommended)
- **npm**: Version 6.0.0 or higher (comes with Node.js)
- **Git**: For version control and cloning repositories
- **Code Editor**: VS Code, WebStorm, or your preferred editor with JavaScript/TypeScript support

Verify your Node.js and npm installation:

```bash
node --version
npm --version
```

### Installation Methods

#### Method 1: Create React App (Recommended for Beginners)

Create React App is the official toolchain for React development, providing a zero-configuration setup with modern build tools:

```bash
# Using npx (recommended)
npx create-react-app my-react-app

# Using npm
npm init react-app my-react-app

# Using Yarn
yarn create react-app my-react-app

# For TypeScript support
npx create-react-app my-react-app --template typescript
```

Navigate to your project directory:

```bash
cd my-react-app
npm start
```

#### Method 2: Next.js Framework

For production-ready applications with server-side rendering capabilities:

```bash
# Create a new Next.js application
npx create-next-app@latest my-next-app

# With TypeScript
npx create-next-app@latest my-next-app --typescript

# Navigate and start development server
cd my-next-app
npm run dev
```

#### Method 3: Manual Setup with Webpack

For custom configurations and advanced users:

```bash
# Initialize project
mkdir my-react-project
cd my-react-project
npm init -y

# Install React dependencies
npm install react react-dom

# Install development dependencies
npm install --save-dev webpack webpack-cli webpack-dev-server
npm install --save-dev babel-loader @babel/core @babel/preset-env @babel/preset-react
npm install --save-dev html-webpack-plugin css-loader style-loader
```

Create a basic `webpack.config.js`:

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
  devServer: {
    contentBase: path.join(__dirname, 'dist'),
    compress: true,
    port: 3000,
  },
};
```

#### Method 4: Adding React to Existing Project

To integrate React into an existing project:

```bash
# Install React
npm install react react-dom

# Install Babel for JSX transformation
npm install --save-dev @babel/core @babel/preset-react
```

Add React preset to your `.babelrc`:

```json
{
  "presets": ["@babel/preset-env", "@babel/preset-react"]
}
```

### Package Manager Considerations

**npm vs Yarn vs pnpm:**

- **npm**: Default package manager, widely supported
- **Yarn**: Faster installation, better dependency resolution
- **pnpm**: Efficient disk space usage, strict dependency management

Choose based on your team's preferences and project requirements.

## Quick Start Guide

### Creating Your First Component

React applications are built using components - reusable pieces of UI that manage their own state and lifecycle.

#### Functional Components (Recommended)

Create your first functional component:

```jsx
// src/components/Welcome.js
import React from 'react';

function Welcome({ name }) {
  return (
    <div className="welcome-container">
      <h1>Hello, {name}!</h1>
      <p>Welcome to React development.</p>
    </div>
  );
}

export default Welcome;
```

#### Using Hooks for State Management

React Hooks allow you to use state and lifecycle features in functional components:

```jsx
// src/components/Counter.js
import React, { useState, useEffect } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [isEven, setIsEven] = useState(true);

  useEffect(() => {
    setIsEven(count % 2 === 0);
  }, [count]);

  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);

  return (
    <div className="counter">
      <h2>Counter: {count}</h2>
      <p>The number is {isEven ? 'even' : 'odd'}</p>
      <div className="button-group">
        <button onClick={increment}>+</button>
        <button onClick={decrement}>-</button>
        <button onClick={reset}>Reset</button>
      </div>
    </div>
  );
}

export default Counter;
```

#### Building a Complete Application

Create a main App component that combines multiple components:

```jsx
// src/App.js
import React, { useState } from 'react';
import Welcome from './components/Welcome';
import Counter from './components/Counter';
import './App.css';

function App() {
  const [user, setUser] = useState('Developer');
  const [showCounter, setShowCounter] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <Welcome name={user} />
        
        <div className="user-input">
          <label htmlFor="username">Enter your name:</label>
          <input
            id="username"
            type="text"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            placeholder="Your name"
          />
        </div>

        <button 
          onClick={() => setShowCounter(!showCounter)}
          className="toggle-button"
        >
          {showCounter ? 'Hide' : 'Show'} Counter
        </button>

        {showCounter && <Counter />}
      </header>
    </div>
  );
}

export default App;
```

#### Entry Point Configuration

Set up your application's entry point:

```jsx
// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### TypeScript Integration

For TypeScript projects, define proper interfaces and types:

```typescript
// src/types/index.ts
export interface User {
  id: number;
  name: string;
  email: string;
}

export interface WelcomeProps {
  name: string;
  onNameChange?: (name: string) => void;
}
```

```tsx
// src/components/Welcome.tsx
import React from 'react';
import { WelcomeProps } from '../types';

const Welcome: React.FC<WelcomeProps> = ({ name, onNameChange }) => {
  return (
    <div className="welcome-container">
      <h1>Hello, {name}!</h1>
      {onNameChange && (
        <button onClick={() => onNameChange('Guest')}>
          Reset to Guest
        </button>
      )}
    </div>
  );
};

export default Welcome;
```

### Styling Your Components

#### CSS Modules

```css
/* src/components/Counter.module.css */
.counter {
  padding: 20px;
  border: 2px solid #007bff;
  border-radius: 8px;
  text-align: center;
  max-width: 300px;
  margin: 20px auto;
}

.buttonGroup {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.buttonGroup button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.buttonGroup button:hover {
  background-color: #0056b3;
}
```

```jsx
// Using CSS Modules
import styles from './Counter.module.css';

function Counter() {
  return (
    <div className={styles.counter}>
      <div className={styles.buttonGroup}>
        {/* buttons */}
      </div>
    </div>
  );
}
```

## Development Environment

### Essential Development Tools

#### Code Editor Setup

**Visual Studio Code Extensions:**
- ES7+ React/Redux/React-Native snippets
- Bracket Pair Colorizer
- Auto Rename Tag
- Prettier - Code formatter
- ESLint
- GitLens
- Thunder Client (for API testing)

**VS Code Settings for React:**

```json
{
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "javascript.preferences.quoteStyle": "single",
  "typescript.preferences.quoteStyle": "single"
}
```

#### Linting and Formatting

Install and configure ESLint and Prettier:

```bash
# ESLint setup
npm install --save-dev eslint eslint-plugin-react eslint-plugin-react-hooks
npx eslint --init

# Prettier setup
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

`.eslintrc.json` configuration:

```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": 12,
    "sourceType": "module"
  },
  "plugins": ["react", "react-hooks", "prettier"],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "prettier/prettier": "error"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

`.prettierrc` configuration:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

#### Development Server Configuration

**Custom Webpack Dev Server:**

```javascript
// webpack.dev.js
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    contentBase: './dist',
    hot: true,
    open: true,
    port: 3000,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
});
```

#### Environment Variables

Create environment-specific configurations:

```bash
# .env.development
REACT_APP_API_URL=http://localhost:8080/api
REACT_APP_DEBUG_MODE=true
REACT_APP_VERSION=1.0.0-dev

# .env.production
REACT_APP_API_URL=https://api.production.com
REACT_APP_DEBUG_MODE=false
REACT_APP_VERSION=1.0.0
```

Access in your React components:

```jsx
const apiUrl = process.env.REACT_APP_API_URL;
const isDebugMode = process.env.REACT_APP_DEBUG_MODE === 'true';
```

### Testing Setup

#### Jest and React Testing Library

```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Create test files:

```jsx
// src/components/__tests__/Counter.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from '../Counter';

describe('Counter Component', () => {
  test('renders counter with initial value', () => {
    render(<Counter />);
    expect(screen.getByText(/Counter: 0/i)).toBeInTheDocument();
  });

  test('increments counter when + button is clicked', () => {
    render(<Counter />);
    const incrementButton = screen.getByText('+');
    fireEvent.click(incrementButton);
    expect(screen.getByText(/Counter: 1/i)).toBeInTheDocument();
  });

  test('shows even/odd status correctly', () => {
    render(<Counter />);
    expect(screen.getByText(/The number is even/i)).toBeInTheDocument();
    
    const incrementButton = screen.getByText('+');
    fireEvent.click(incrementButton);
    expect(screen.getByText(/The number is odd/i)).toBeInTheDocument();
  });
});
```

### Debugging Tools

#### React Developer Tools

Install the React Developer Tools browser extension for:
- Component tree inspection
- Props and state debugging
- Performance profiling
- Hook debugging

#### Browser DevTools Integration

Use browser debugging features:

```jsx
// Add debugging breakpoints
function MyComponent() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    debugger; // Browser will pause here
    fetchData().then(setData);
  }, []);

  // Console logging for development
  if (process.env.NODE_ENV === 'development') {
    console.log('Component data:', data);
  }

  return <div>{/* component JSX */}</div>;
}
```

### Performance Optimization

#### Bundle Analysis

Analyze your bundle size:

```bash
# Install bundle analyzer
npm install --save-dev webpack-bundle-analyzer

# Add to package.json scripts
"analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js"
```

#### Code Splitting

Implement dynamic imports for better performance:

```jsx
import React, { Suspense, lazy } from 'react';

const LazyComponent = lazy(() => import('./components/LazyComponent'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
}
```

### Common Troubleshooting

**Port Already in Use:**
```bash
# Kill process on port 3000