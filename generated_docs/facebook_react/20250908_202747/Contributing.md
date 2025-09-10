# Contributing

Welcome to the React project! We appreciate your interest in contributing to one of the world's most widely-used JavaScript libraries for building user interfaces. This guide will walk you through everything you need to know to make meaningful contributions to React, from setting up your development environment to getting your changes merged into the main codebase.

React is maintained by Meta (formerly Facebook) and the open-source community. We welcome contributions of all kinds, including bug fixes, feature implementations, documentation improvements, and performance optimizations. Whether you're a first-time contributor or an experienced open-source developer, this guide will help you navigate the contribution process effectively.

## Development Setup

### Prerequisites

Before you begin contributing to React, ensure you have the following tools installed on your development machine:

- **Node.js**: Version 16.0.0 or higher (we recommend using the latest LTS version)
- **npm**: Version 7.0.0 or higher (comes with Node.js)
- **Git**: Latest stable version
- **A code editor**: We recommend Visual Studio Code with React and JavaScript extensions

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Navigate to https://github.com/facebook/react and click "Fork"
   # Then clone your fork locally
   git clone https://github.com/YOUR_USERNAME/react.git
   cd react
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/facebook/react.git
   git remote -v  # Verify remotes are set correctly
   ```

3. **Install Dependencies**
   ```bash
   npm install
   ```

### Build System Overview

React uses a custom build system that handles multiple package builds, testing, and bundling. Key build commands include:

```bash
# Build all packages for development
npm run build

# Build specific packages
npm run build -- --type=NODE

# Build for production (optimized)
npm run build -- --type=PROD

# Watch mode for development
npm run build -- --watch
```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Run Tests During Development**
   ```bash
   # Run all tests
   npm test

   # Run tests in watch mode
   npm test -- --watch

   # Run specific test suites
   npm test -- --testNamePattern="ComponentName"
   ```

3. **Local Testing with Examples**
   ```bash
   # Start the development server for fixtures
   cd fixtures/packaging
   npm start
   ```

### Environment Configuration

Create a `.env.local` file in the root directory for local development settings:

```bash
# Enable additional debugging
REACT_DEBUG=true

# Enable experimental features (use with caution)
REACT_EXPERIMENTAL=true

# Profiling mode
REACT_PROFILING=true
```

## Code Style and Guidelines

### JavaScript/TypeScript Standards

React follows strict coding standards to maintain consistency across the large codebase. We use ESLint and Prettier for automated code formatting and linting.

#### Code Formatting

```bash
# Format all files
npm run prettier

# Lint and fix issues
npm run lint -- --fix
```

#### Naming Conventions

- **Components**: Use PascalCase for React components
  ```javascript
  function MyComponent(props) {
    return <div>{props.children}</div>;
  }
  ```

- **Functions and Variables**: Use camelCase
  ```javascript
  const handleUserInput = (event) => {
    const userValue = event.target.value;
  };
  ```

- **Constants**: Use SCREAMING_SNAKE_CASE
  ```javascript
  const MAX_RETRY_ATTEMPTS = 3;
  const DEFAULT_TIMEOUT_MS = 5000;
  ```

#### File Structure

- **Component Files**: End with `.js` or `.tsx` for TypeScript
- **Test Files**: Use `.test.js` or `.spec.js` suffix
- **Type Definitions**: Use `.d.ts` for TypeScript declarations

```
packages/react/
├── src/
│   ├── React.js
│   ├── ReactChildren.js
│   └── __tests__/
│       ├── React-test.js
│       └── ReactChildren-test.js
└── index.js
```

### Documentation Standards

All public APIs must include comprehensive JSDoc comments:

```javascript
/**
 * Creates a React element with the given type, props, and children.
 * 
 * @param {string|Function|Class} type - The element type
 * @param {Object} props - Properties passed to the element
 * @param {...React.ReactNode} children - Child elements
 * @returns {React.ReactElement} The created React element
 * 
 * @example
 * const element = createElement('div', {className: 'container'}, 'Hello World');
 */
function createElement(type, props, ...children) {
  // Implementation
}
```

### Performance Considerations

- **Avoid unnecessary re-renders**: Use React.memo, useMemo, and useCallback appropriately
- **Bundle size impact**: Consider the impact of new dependencies on bundle size
- **Memory leaks**: Ensure proper cleanup in useEffect hooks

```javascript
// Good: Proper cleanup
useEffect(() => {
  const subscription = subscribe();
  return () => subscription.unsubscribe();
}, []);

// Bad: Missing cleanup
useEffect(() => {
  const subscription = subscribe();
}, []);
```

## Pull Request Process

### Before Creating a Pull Request

1. **Sync with Upstream**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run the Full Test Suite**
   ```bash
   npm test
   npm run test:build
   npm run test:integration
   ```

3. **Verify Build Success**
   ```bash
   npm run build
   npm run test:build
   ```

### Pull Request Guidelines

#### Title and Description

- **Title**: Use a clear, descriptive title that summarizes the change
  - ✅ Good: "Fix memory leak in useEffect cleanup"
  - ❌ Bad: "Fix bug"

- **Description**: Include the following sections:
  ```markdown
  ## Summary
  Brief description of what this PR does.

  ## Test Plan
  How did you test these changes?

  ## Related Issues
  Fixes #issue-number

  ## Breaking Changes
  List any breaking changes (if applicable)
  ```

#### Code Review Checklist

Before submitting, ensure your PR meets these criteria:

- [ ] All tests pass locally
- [ ] Code follows the established style guide
- [ ] New features include comprehensive tests
- [ ] Documentation is updated for API changes
- [ ] No console.log statements or debugging code
- [ ] Performance impact has been considered
- [ ] Accessibility guidelines are followed

### Review Process

1. **Automated Checks**: All PRs must pass automated tests and linting
2. **Core Team Review**: At least one React core team member must approve
3. **Community Review**: Community feedback is encouraged and valued
4. **Integration Testing**: Changes are tested against internal Meta systems

### Handling Feedback

- **Be responsive**: Address feedback promptly and professionally
- **Ask questions**: If feedback is unclear, ask for clarification
- **Make incremental changes**: Push additional commits to address feedback
- **Squash commits**: Before merging, squash commits into logical units

```bash
# Interactive rebase to squash commits
git rebase -i HEAD~3

# Force push to update PR (after squashing)
git push --force-with-lease origin your-feature-branch
```

## Issue Reporting

### Before Reporting an Issue

1. **Search Existing Issues**: Check if the issue has already been reported
2. **Reproduce the Bug**: Ensure you can consistently reproduce the issue
3. **Check React Version**: Verify you're using a supported React version
4. **Minimal Reproduction**: Create the smallest possible example that demonstrates the issue

### Bug Report Template

When reporting bugs, please use this template:

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Minimal Reproduction
Link to CodeSandbox, JSFiddle, or GitHub repository with minimal reproduction.

## Environment
- React version: [e.g. 18.2.0]
- Browser: [e.g. Chrome 91]
- OS: [e.g. macOS 12.0]
- Node.js version: [e.g. 16.14.0]

## Additional Context
Add any other context about the problem here.
```

### Feature Requests

For feature requests, please include:

- **Use case**: Describe the problem you're trying to solve
- **Proposed solution**: Your suggested approach
- **Alternatives considered**: Other solutions you've considered
- **Implementation details**: Technical considerations (if applicable)

### Security Issues

**Do not report security vulnerabilities through public GitHub issues.** Instead, please report them through Meta's Bug Bounty program or email security@react.dev.

## Community Guidelines

### Code of Conduct

React follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity.

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Discord**: Real-time chat with the community
- **Twitter**: Follow [@reactjs](https://twitter.com/reactjs) for updates

### Best Practices for Community Interaction

1. **Be respectful**: Treat all community members with respect and kindness
2. **Be patient**: Remember that maintainers and contributors are often volunteers
3. **Be constructive**: Provide helpful feedback and suggestions
4. **Be inclusive**: Welcome newcomers and help them get started

### Mentorship and Learning

- **Good First Issues**: Look for issues labeled "good first issue" if you're new to contributing
- **Pair Programming**: Consider pairing with experienced contributors
- **Documentation**: Contributing to documentation is a great way to start
- **Testing**: Writing tests is valuable and helps you understand the codebase

### Recognition

Contributors are recognized in several ways:

- **Changelog**: Significant contributions are mentioned in release notes
- **Contributors List**: All contributors are listed in the project's contributors section
- **Social Media**: Notable contributions may be highlighted on React's social media channels

### Long-term Involvement

We encourage long-term involvement in the React community:

- **Consistent contributions**: Regular, smaller contributions are often more valuable than large, one-time changes
- **Code review**: Participating in code reviews helps improve the overall quality
- **Mentoring**: Help new contributors get started
- **Advocacy**: Share your React knowledge through blog posts, talks, and tutorials

---

## Additional Resources

- [React Documentation](https://react.dev/)
- [React GitHub Repository](https://github.com/facebook/react)
- [React RFC Process](https://github.com/reactjs/rfcs)
- [React DevTools](https://github.com/facebook/react/tree/main/packages/react-devtools)
- [React Native Contributing Guide](https://reactnative.dev/contributing/overview)

Thank you for your interest in contributing to React! Your contributions help make React better for millions of developers worldwide. If you have any questions about the contribution process, don't hesitate to ask in GitHub Discussions or reach out to the community through our various communication channels.