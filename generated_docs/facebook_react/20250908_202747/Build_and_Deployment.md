# Build and Deployment

This section provides comprehensive guidance for building and deploying React applications, covering modern build processes, server-side rendering implementation, and production deployment strategies. Whether you're working with Create React App, custom Webpack configurations, or Next.js applications, this documentation will help you optimize your build pipeline and deployment workflow.

## Build Process

### Overview

The React build process transforms your development code into optimized, production-ready assets. This involves transpiling JSX and TypeScript, bundling modules, optimizing assets, and generating static files that browsers can efficiently load and execute.

### Webpack Configuration

React applications typically use Webpack as the primary build tool. Here's a comprehensive production configuration:

```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction 
        ? '[name].[contenthash].js' 
        : '[name].js',
      chunkFilename: isProduction 
        ? '[name].[contenthash].chunk.js' 
        : '[name].chunk.js',
      publicPath: '/',
      clean: true
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
                '@babel/preset-react',
                '@babel/preset-typescript'
              ],
              plugins: [
                '@babel/plugin-transform-runtime',
                isProduction && 'babel-plugin-transform-react-remove-prop-types'
              ].filter(Boolean)
            }
          }
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader',
            'postcss-loader'
          ]
        },
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name].[hash][ext]'
          }
        }
      ]
    },
    
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html',
        minify: isProduction && {
          removeComments: true,
          collapseWhitespace: true,
          removeRedundantAttributes: true,
          useShortDoctype: true,
          removeEmptyAttributes: true,
          removeStyleLinkTypeAttributes: true,
          keepClosingSlash: true,
          minifyJS: true,
          minifyCSS: true,
          minifyURLs: true
        }
      }),
      
      isProduction && new MiniCssExtractPlugin({
        filename: '[name].[contenthash].css',
        chunkFilename: '[name].[contenthash].chunk.css'
      })
    ].filter(Boolean),
    
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: true,
              drop_debugger: true
            }
          }
        }),
        new OptimizeCSSAssetsPlugin()
      ],
      
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
      }
    },
    
    resolve: {
      extensions: ['.js', '.jsx', '.ts', '.tsx'],
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  };
};
```

### TypeScript Integration

For TypeScript projects, ensure proper configuration:

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
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
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": [
    "src"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
```

### Build Scripts and Automation

Configure comprehensive build scripts in your `package.json`:

```json
{
  "scripts": {
    "start": "webpack serve --mode development --open",
    "build": "webpack --mode production",
    "build:analyze": "webpack --mode production --analyze",
    "build:stats": "webpack --mode production --json > stats.json",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint src --ext .js,.jsx,.ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "prebuild": "npm run lint && npm run type-check && npm run test",
    "postbuild": "npm run build:analyze"
  }
}
```

### Environment Configuration

Implement environment-specific configurations:

```javascript
// config/env.js
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const NODE_ENV = process.env.NODE_ENV || 'development';
const isProduction = NODE_ENV === 'production';
const isDevelopment = NODE_ENV === 'development';

// Define environment variables for the client
const getClientEnvironment = (publicUrl) => {
  const raw = Object.keys(process.env)
    .filter(key => /^REACT_APP_/i.test(key))
    .reduce((env, key) => {
      env[key] = process.env[key];
      return env;
    }, {
      NODE_ENV,
      PUBLIC_URL: publicUrl,
      REACT_APP_VERSION: require('../package.json').version
    });

  // Stringify all values for webpack DefinePlugin
  const stringified = {
    'process.env': Object.keys(raw).reduce((env, key) => {
      env[key] = JSON.stringify(raw[key]);
      return env;
    }, {})
  };

  return { raw, stringified };
};

module.exports = {
  NODE_ENV,
  isProduction,
  isDevelopment,
  getClientEnvironment
};
```

## Server-Side Rendering

### Next.js Implementation

Next.js provides built-in SSR capabilities with minimal configuration:

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Image optimization
  images: {
    domains: ['example.com', 'cdn.example.com'],
    formats: ['image/webp', 'image/avif']
  },
  
  // Internationalization
  i18n: {
    locales: ['en', 'es', 'fr'],
    defaultLocale: 'en'
  },
  
  // Custom webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack modifications
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false
      };
    }
    
    return config;
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Redirects and rewrites
  async redirects() {
    return [
      {
        source: '/old-path',
        destination: '/new-path',
        permanent: true,
      },
    ];
  },
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.example.com/:path*',
      },
    ];
  }
};

module.exports = nextConfig;
```

### Custom SSR Implementation

For custom SSR setups with Express:

```javascript
// server/index.js
import express from 'express';
import React from 'react';
import { renderToString } from 'react-dom/server';
import { StaticRouter } from 'react-router-dom/server';
import { Provider } from 'react-redux';
import { ChunkExtractor } from '@loadable/server';
import path from 'path';
import fs from 'fs';

import App from '../src/App';
import { createStore } from '../src/store';

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.resolve(__dirname, '../dist')));

// SSR handler
app.get('*', async (req, res) => {
  try {
    // Create Redux store
    const store = createStore();
    
    // Load initial data based on route
    await loadInitialData(req.path, store);
    
    // Create chunk extractor for code splitting
    const statsFile = path.resolve(__dirname, '../dist/loadable-stats.json');
    const extractor = new ChunkExtractor({ statsFile });
    
    // Render app to string
    const jsx = extractor.collectChunks(
      <Provider store={store}>
        <StaticRouter location={req.url}>
          <App />
        </StaticRouter>
      </Provider>
    );
    
    const html = renderToString(jsx);
    const scriptTags = extractor.getScriptTags();
    const linkTags = extractor.getLinkTags();
    const styleTags = extractor.getStyleTags();
    
    // Get initial state
    const preloadedState = store.getState();
    
    // Load HTML template
    const template = fs.readFileSync(
      path.resolve(__dirname, '../dist/index.html'),
      'utf-8'
    );
    
    // Replace placeholders
    const finalHtml = template
      .replace('<div id="root"></div>', `<div id="root">${html}</div>`)
      .replace('</head>', `${linkTags}${styleTags}</head>`)
      .replace('</body>', `
        <script>
          window.__PRELOADED_STATE__ = ${JSON.stringify(preloadedState).replace(/</g, '\\u003c')}
        </script>
        ${scriptTags}
        </body>
      `);
    
    res.send(finalHtml);
  } catch (error) {
    console.error('SSR Error:', error);
    res.status(500).send('Internal Server Error');
  }
});

async function loadInitialData(path, store) {
  // Implement route-based data loading
  // This would typically involve matching routes and calling appropriate actions
}

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Hydration Strategy

Implement proper client-side hydration:

```javascript
// src/index.js
import React from 'react';
import { hydrateRoot, createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { loadableReady } from '@loadable/component';

import App from './App';
import { createStore } from './store';

// Get preloaded state from server
const preloadedState = window.__PRELOADED_STATE__;
delete window.__PRELOADED_STATE__;

// Create store with preloaded state
const store = createStore(preloadedState);

const AppWithProviders = () => (
  <Provider store={store}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </Provider>
);

const container = document.getElementById('root');

// Use hydration for SSR, regular render for CSR
if (container.hasChildNodes()) {
  loadableReady(() => {
    hydrateRoot(container, <AppWithProviders />);
  });
} else {
  const root = createRoot(container);
  root.render(<AppWithProviders />);
}
```

## Deployment Strategies

### Containerized Deployment with Docker

Create optimized Docker configurations:

```dockerfile
# Dockerfile
# Multi-stage build for production optimization
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN yarn build

# Production stage
FROM nginx:alpine AS production

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public,