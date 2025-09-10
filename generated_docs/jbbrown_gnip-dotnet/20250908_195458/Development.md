# Development

This section provides comprehensive guidance for developers who want to contribute to, modify, or extend the Gnip .NET API Client. The following documentation covers everything from setting up your development environment to submitting contributions.

## Development Environment Setup

### Prerequisites

Before beginning development on the Gnip .NET API Client, ensure your development environment meets the following requirements:

#### Required Software
- **.NET Framework 4.5+** or **.NET Core 3.1+** / **.NET 5.0+**
- **Visual Studio 2019/2022** (Community, Professional, or Enterprise) or **Visual Studio Code**
- **Git** for version control
- **NuGet Package Manager** (typically included with Visual Studio)

#### Recommended Tools
- **ReSharper** or **CodeMaid** for code quality and formatting
- **Postman** or **Fiddler** for API testing and debugging
- **NUnit Test Adapter** for Visual Studio (if using NUnit)
- **GitKraken** or **SourceTree** for advanced Git operations

### Environment Configuration

#### 1. Clone the Repository
```bash
git clone https://github.com/jbbrown/gnip-dotnet.git
cd gnip-dotnet
```

#### 2. Configure IDE Settings
For consistent code formatting across the project, configure your IDE with the following settings:

**Visual Studio:**
```xml
<!-- .editorconfig -->
root = true

[*.cs]
indent_style = space
indent_size = 4
end_of_line = crlf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# C# formatting rules
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true
```

#### 3. Set Up API Credentials
Create a `appsettings.Development.json` file in the test project:

```json
{
  "Gnip": {
    "Username": "your-gnip-username",
    "Password": "your-gnip-password",
    "Account": "your-account-name",
    "BaseUrl": "https://gnip-api.twitter.com"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Gnip": "Trace"
    }
  }
}
```

**Important:** Never commit actual credentials to the repository. Use environment variables or secure configuration management for production deployments.

## Building from Source

### Build Process Overview

The Gnip .NET API Client uses MSBuild as its primary build system, supporting both command-line and IDE-based builds. The project follows standard .NET build conventions with additional custom targets for packaging and deployment.

### Command Line Build

#### Basic Build Commands
```bash
# Restore NuGet packages
dotnet restore

# Build the solution in Debug mode
dotnet build

# Build in Release mode
dotnet build --configuration Release

# Build with verbose output for troubleshooting
dotnet build --verbosity detailed
```

#### Advanced Build Options
```bash
# Build specific project
dotnet build src/Gnip.Client/Gnip.Client.csproj

# Build with specific framework target
dotnet build --framework net5.0

# Build and output to specific directory
dotnet build --output ./build/output
```

### Visual Studio Build

1. Open `Gnip.sln` in Visual Studio
2. Select build configuration (Debug/Release) from the toolbar
3. Build the solution using:
   - **Build → Build Solution** (Ctrl+Shift+B)
   - **Build → Rebuild Solution** for clean build

### Build Configuration

The project supports multiple build configurations optimized for different scenarios:

#### Debug Configuration
- Includes debug symbols and detailed logging
- Optimized for development and debugging
- Enables all compiler warnings
- Includes XML documentation generation

#### Release Configuration
- Optimized for performance and size
- Excludes debug symbols
- Enables code optimization
- Suitable for production deployment

### Custom Build Targets

The project includes several custom MSBuild targets for specialized operations:

```xml
<!-- Custom targets in Directory.Build.props -->
<Target Name="GenerateApiDocs" BeforeTargets="Build">
  <Exec Command="docfx docfx.json" ContinueOnError="false" />
</Target>

<Target Name="RunCodeAnalysis" AfterTargets="Build">
  <Exec Command="dotnet sonarscanner begin /k:gnip-dotnet" />
</Target>
```

### Troubleshooting Build Issues

#### Common Build Problems

**Package Restore Failures:**
```bash
# Clear NuGet cache
dotnet nuget locals all --clear

# Restore with force
dotnet restore --force --no-cache
```

**Framework Target Issues:**
```bash
# List installed SDKs
dotnet --list-sdks

# Install required SDK version
dotnet --version
```

**Dependency Conflicts:**
Review `Directory.Packages.props` for version conflicts and ensure consistent package versions across projects.

## Running Tests

### Test Architecture

The Gnip .NET API Client employs a comprehensive testing strategy that includes:

- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing API interactions with Gnip services
- **Performance Tests**: Validating response times and throughput
- **Contract Tests**: Ensuring API compatibility

### Test Project Structure

```
tests/
├── Gnip.Client.UnitTests/
│   ├── ClientTests.cs
│   ├── AuthenticationTests.cs
│   ├── SerializationTests.cs
│   └── Helpers/
├── Gnip.Client.IntegrationTests/
│   ├── ApiEndpointTests.cs
│   ├── StreamingTests.cs
│   └── Configuration/
└── Gnip.Client.PerformanceTests/
    ├── ThroughputTests.cs
    └── LoadTests.cs
```

### Running Unit Tests

#### Command Line Execution
```bash
# Run all tests
dotnet test

# Run tests with detailed output
dotnet test --verbosity normal

# Run tests in specific project
dotnet test tests/Gnip.Client.UnitTests/

# Run tests with code coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test category
dotnet test --filter Category=Unit
```

#### Visual Studio Test Runner
1. Open **Test Explorer** (Test → Test Explorer)
2. Build the solution to discover tests
3. Run tests using:
   - **Run All Tests** for complete test suite
   - **Run Selected Tests** for specific test methods
   - **Debug Selected Tests** for debugging test failures

### Integration Test Configuration

Integration tests require valid Gnip API credentials and network connectivity. Configure test settings:

```csharp
// IntegrationTestBase.cs
public abstract class IntegrationTestBase
{
    protected GnipClient Client { get; private set; }
    
    [OneTimeSetUp]
    public void GlobalSetup()
    {
        var config = new GnipConfiguration
        {
            Username = Environment.GetEnvironmentVariable("GNIP_USERNAME"),
            Password = Environment.GetEnvironmentVariable("GNIP_PASSWORD"),
            Account = Environment.GetEnvironmentVariable("GNIP_ACCOUNT"),
            BaseUrl = "https://gnip-api.twitter.com"
        };
        
        Client = new GnipClient(config);
    }
}
```

### Test Categories and Filtering

Tests are organized using categories for selective execution:

```csharp
[Test]
[Category("Unit")]
[Category("Authentication")]
public void Should_Authenticate_With_Valid_Credentials()
{
    // Test implementation
}

[Test]
[Category("Integration")]
[Category("Streaming")]
public void Should_Connect_To_Streaming_Endpoint()
{
    // Test implementation
}
```

#### Running Specific Test Categories
```bash
# Run only unit tests
dotnet test --filter Category=Unit

# Run authentication-related tests
dotnet test --filter Category=Authentication

# Exclude integration tests
dotnet test --filter Category!=Integration
```

### Performance Testing

Performance tests validate the client's behavior under various load conditions:

```csharp
[Test]
[Category("Performance")]
public async Task Should_Handle_High_Volume_Streaming()
{
    var stopwatch = Stopwatch.StartNew();
    var messageCount = 0;
    
    await Client.StreamAsync(stream =>
    {
        stream.OnMessage += (sender, args) =>
        {
            Interlocked.Increment(ref messageCount);
        };
    });
    
    stopwatch.Stop();
    
    Assert.That(messageCount, Is.GreaterThan(1000));
    Assert.That(stopwatch.ElapsedMilliseconds, Is.LessThan(30000));
}
```

### Continuous Integration Testing

The project includes GitHub Actions workflows for automated testing:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup .NET
        uses: actions/setup-dotnet@v1
        with:
          dotnet-version: 5.0.x
      - name: Run tests
        run: dotnet test --configuration Release --collect:"XPlat Code Coverage"
```

## Contributing Guidelines

### Code of Conduct

All contributors must adhere to our Code of Conduct, which promotes a welcoming and inclusive environment for all participants. We expect:

- **Respectful Communication**: Use welcoming and inclusive language
- **Constructive Feedback**: Focus on code and ideas, not individuals
- **Collaborative Spirit**: Help others learn and grow
- **Professional Behavior**: Maintain professionalism in all interactions

### Contribution Workflow

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/gnip-dotnet.git
cd gnip-dotnet

# Add upstream remote
git remote add upstream https://github.com/jbbrown/gnip-dotnet.git
```

#### 2. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

#### 3. Development Process
- Write code following established patterns and conventions
- Add comprehensive tests for new functionality
- Update documentation as needed
- Ensure all tests pass locally

#### 4. Commit Guidelines
Follow conventional commit format for clear history:

```bash
# Feature commits
git commit -m "feat: add support for PowerTrack 2.0 API"

# Bug fix commits
git commit -m "fix: resolve authentication timeout issue"

# Documentation commits
git commit -m "docs: update API usage examples"

# Test commits
git commit -m "test: add integration tests for streaming endpoints"
```

#### 5. Pull Request Process
```bash
# Push feature branch to your fork
git push origin feature/your-feature-name

# Create pull request through GitHub interface
```

### Code Standards

#### Coding Conventions

**Naming Conventions:**
```csharp
// Classes: PascalCase
public class GnipStreamClient { }

// Methods: PascalCase
public async Task<Stream> ConnectAsync() { }

// Properties: PascalCase
public string ApiEndpoint { get; set; }

// Fields: camelCase with underscore prefix for private
private readonly HttpClient _httpClient;

// Constants: PascalCase
public const string DefaultBaseUrl = "https://gnip-api.twitter.com";
```

**Code Organization:**
```csharp
// File header with copyright
// Copyright (c) 2023 Gnip .NET Contributors

using System;
using System.Threading.Tasks;
// Third-party usings
using Newtonsoft.Json;
// Local usings
using Gnip.Client.Models;

namespace Gnip.Client
{
    /// <summary>
    /// Provides access to Gnip streaming APIs with event-driven architecture.
    /// </summary>
    public class GnipStreamClient : IDisposable
    {
        // Constants first
        private const int DefaultTimeoutMs = 30000;
        
        // Fields
        private readonly HttpClient _httpClient;
        private readonly GnipConfiguration _configuration;
        
        // Properties
        public bool IsConnected { get; private set; }
        
        // Events
        public event EventHandler<MessageReceivedEventArgs> MessageReceived;
        
        // Constructor
        public GnipStreamClient(GnipConfiguration configuration)
        {
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _httpClient = new HttpClient();
        }
        
        // Public methods
        public async Task ConnectAsync()
        {
            // Implementation
        }
        
        // Private methods
        private void OnMessageReceived(MessageReceivedEventArgs args)
        {
            MessageReceived?.Invoke(this, args);
        }
        
        // Dispose implementation
        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
```

#### Documentation Standards

All public APIs must include comprehensive XML documentation:

```csharp
/// <summary>
/// Establishes a connection to the specified Gnip streaming endpoint.
/// </summary>
/// <param name="endpoint">The streaming endpoint URL to connect to.</param>
/// <param name="cancellationToken">Token to cancel the connection attempt.</param>
/// <returns>A task representing the asynchronous connection operation.</returns>
/// <exception cref="ArgumentNullException">Thrown when endpoint is null.</exception>
/// <exception cref="GnipAuthenticationException">Thrown when authentication fails.</exception>
/// <exception cref="GnipConnectionException">Thrown when connection cannot be established.</exception>
/// <example>
/// <code>
/// var client = new GnipStreamClient(configuration);
/// await client.ConnectAsync("https://gnip-stream.twitter.com/stream.json");
/// </code>
/// </example>
public async Task ConnectAsync(string endpoint, CancellationToken cancellationToken = default)
{
    // Implementation
}
```

### Review Process

#### Pull Request Requirements

Before submitting a pull request, ensure:

- [ ] All tests pass locally
- [ ] Code coverage meets minimum threshold (80%)
- [ ] No compiler warnings or errors
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated for significant changes
- [ ] Breaking changes are clearly documented

#### Review Criteria

Pull requests are evaluated based on:

1. **Code Quality**: Adherence to coding standards and best practices
2. **Test Coverage**: Comprehensive tests for new functionality
3. **Documentation**: Clear and complete documentation
4. **Performance**: No significant performance regressions
5. **Compatibility**: Backward compatibility maintained unless breaking change is justified
6. **Security**: No introduction of security vulnerabilities

#### Reviewer Guidelines

Reviewers should:
- Provide constructive feedback
- Test changes locally when possible
- Verify documentation accuracy
- Check for potential edge cases
- Ensure changes align with project goals

### Issue Reporting

When reporting issues, include:

1. **Environment Details**: .NET version, OS, IDE
2. **Reproduction Steps**: Clear steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Code Samples**: Minimal reproducible example
6. **Error Messages**: Complete error messages and stack traces

### Feature Requests

For new features, provide:

1. **Use Case**: Clear description of the problem being solved
2. **Proposed Solution**: Detailed description of the proposed feature
3. **Alternatives Considered**: Other approaches you've considered
4. **Implementation Notes**: Technical considerations or constraints

---

## Additional Resources

- [Project Wiki](https://github.com/jbbrown/gnip-dotnet/wiki)
- [API Documentation](https://jbbrown.github.io/gnip-dotnet/)
- [Gnip API Reference](https://developer.twitter.com/en/docs/twitter-api/enterprise/gnip-api/overview)
- [.NET Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/inside-a-program/coding-conventions)

For questions or support, please open an issue on GitHub or contact the maintainers through the project's