# Configuration

The Gnip .NET API Client provides a flexible and robust configuration system designed to handle various connection scenarios, authentication methods, and operational requirements. This section covers all aspects of configuring the client for optimal performance in production environments.

## Connection Settings

The connection settings form the foundation of your Gnip client configuration, determining how your application communicates with Gnip's streaming and REST APIs.

### Basic Connection Configuration

The primary connection configuration is handled through the `GnipConfiguration` class, which serves as the central configuration object for all client operations:

```csharp
var config = new GnipConfiguration
{
    BaseUrl = "https://gnip-api.twitter.com",
    Account = "your-account-name",
    Label = "your-stream-label",
    ConnectionTimeout = TimeSpan.FromSeconds(30),
    ReadTimeout = TimeSpan.FromMinutes(5),
    MaxConnectionPoolSize = 10
};
```

### Advanced Connection Parameters

For production environments, you'll need to configure additional connection parameters to ensure reliable operation:

```csharp
var advancedConfig = new GnipConfiguration
{
    BaseUrl = "https://gnip-api.twitter.com",
    Account = "your-account-name",
    Label = "your-stream-label",
    
    // Connection pooling settings
    MaxConnectionPoolSize = 20,
    MaxConnectionsPerRoute = 5,
    ConnectionKeepAlive = TimeSpan.FromMinutes(2),
    
    // Timeout configurations
    ConnectionTimeout = TimeSpan.FromSeconds(30),
    ReadTimeout = TimeSpan.FromMinutes(10),
    WriteTimeout = TimeSpan.FromSeconds(30),
    
    // Buffer settings for streaming
    BufferSize = 8192,
    MaxBufferSize = 65536,
    
    // Compression settings
    EnableCompression = true,
    CompressionLevel = CompressionLevel.Optimal
};
```

### Environment-Specific Configuration

Different environments require different configuration approaches. Here's how to structure configuration for various deployment scenarios:

**Development Environment:**
```csharp
var devConfig = new GnipConfiguration
{
    BaseUrl = "https://gnip-api.twitter.com",
    Account = "dev-account",
    Label = "dev-stream",
    ConnectionTimeout = TimeSpan.FromSeconds(10),
    ReadTimeout = TimeSpan.FromMinutes(1),
    EnableDebugLogging = true,
    ValidateSslCertificates = false // Only for development
};
```

**Production Environment:**
```csharp
var prodConfig = new GnipConfiguration
{
    BaseUrl = "https://gnip-api.twitter.com",
    Account = Environment.GetEnvironmentVariable("GNIP_ACCOUNT"),
    Label = Environment.GetEnvironmentVariable("GNIP_LABEL"),
    ConnectionTimeout = TimeSpan.FromSeconds(30),
    ReadTimeout = TimeSpan.FromMinutes(10),
    MaxConnectionPoolSize = 50,
    EnableHealthChecks = true,
    ValidateSslCertificates = true
};
```

## Authentication Configuration

Gnip supports multiple authentication mechanisms, with HTTP Basic Authentication being the primary method for API access.

### Basic Authentication Setup

The most common authentication method uses username and password credentials:

```csharp
var authConfig = new GnipAuthenticationConfiguration
{
    Username = "your-username",
    Password = "your-password",
    AuthenticationType = AuthenticationType.Basic
};

var config = new GnipConfiguration
{
    BaseUrl = "https://gnip-api.twitter.com",
    Account = "your-account",
    Label = "your-label",
    Authentication = authConfig
};
```

### Secure Credential Management

For production environments, never hardcode credentials. Use secure configuration providers:

```csharp
// Using configuration providers
var builder = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .AddEnvironmentVariables()
    .AddUserSecrets<Program>();

var configuration = builder.Build();

var authConfig = new GnipAuthenticationConfiguration
{
    Username = configuration["Gnip:Username"],
    Password = configuration["Gnip:Password"],
    AuthenticationType = AuthenticationType.Basic
};
```

### Token-Based Authentication

For scenarios requiring token-based authentication:

```csharp
var tokenAuthConfig = new GnipAuthenticationConfiguration
{
    Token = "your-bearer-token",
    AuthenticationType = AuthenticationType.Bearer,
    TokenRefreshInterval = TimeSpan.FromHours(1)
};
```

### Authentication Middleware Configuration

Configure authentication middleware for automatic credential management:

```csharp
var config = new GnipConfiguration
{
    Authentication = new GnipAuthenticationConfiguration
    {
        Username = "your-username",
        Password = "your-password",
        AuthenticationType = AuthenticationType.Basic,
        
        // Automatic retry on authentication failure
        RetryOnAuthFailure = true,
        MaxAuthRetries = 3,
        AuthRetryDelay = TimeSpan.FromSeconds(5),
        
        // Preemptive authentication
        PreemptiveAuthentication = true
    }
};
```

## Retry Policies

Robust retry policies are essential for handling transient failures in distributed systems. The Gnip client provides comprehensive retry configuration options.

### Basic Retry Configuration

Configure basic retry behavior for common scenarios:

```csharp
var retryPolicy = new GnipRetryPolicy
{
    MaxRetries = 3,
    BaseDelay = TimeSpan.FromSeconds(1),
    MaxDelay = TimeSpan.FromSeconds(30),
    RetryStrategy = RetryStrategy.ExponentialBackoff
};

var config = new GnipConfiguration
{
    // ... other configuration
    RetryPolicy = retryPolicy
};
```

### Advanced Retry Strategies

Implement sophisticated retry strategies for different types of failures:

```csharp
var advancedRetryPolicy = new GnipRetryPolicy
{
    MaxRetries = 5,
    BaseDelay = TimeSpan.FromSeconds(2),
    MaxDelay = TimeSpan.FromMinutes(5),
    RetryStrategy = RetryStrategy.ExponentialBackoffWithJitter,
    
    // Specific retry conditions
    RetryableHttpStatusCodes = new[]
    {
        HttpStatusCode.ServiceUnavailable,
        HttpStatusCode.RequestTimeout,
        HttpStatusCode.TooManyRequests,
        HttpStatusCode.InternalServerError,
        HttpStatusCode.BadGateway,
        HttpStatusCode.GatewayTimeout
    },
    
    // Exception-based retry logic
    RetryableExceptions = new[]
    {
        typeof(HttpRequestException),
        typeof(TaskCanceledException),
        typeof(SocketException)
    },
    
    // Custom retry conditions
    ShouldRetry = (attempt, exception, response) =>
    {
        // Custom logic for determining retry eligibility
        if (attempt >= 5) return false;
        if (exception is TimeoutException) return true;
        if (response?.StatusCode == HttpStatusCode.TooManyRequests)
        {
            // Check rate limit headers
            var retryAfter = response.Headers.RetryAfter;
            return retryAfter?.Delta < TimeSpan.FromMinutes(5);
        }
        return false;
    }
};
```

### Circuit Breaker Integration

Combine retry policies with circuit breaker patterns for enhanced resilience:

```csharp
var circuitBreakerPolicy = new GnipCircuitBreakerPolicy
{
    FailureThreshold = 5,
    RecoveryTimeout = TimeSpan.FromMinutes(1),
    SamplingDuration = TimeSpan.FromMinutes(5),
    MinimumThroughput = 10
};

var config = new GnipConfiguration
{
    RetryPolicy = retryPolicy,
    CircuitBreakerPolicy = circuitBreakerPolicy
};
```

### Streaming-Specific Retry Configuration

Streaming connections require special retry considerations:

```csharp
var streamingRetryPolicy = new GnipStreamingRetryPolicy
{
    MaxRetries = int.MaxValue, // Infinite retries for streaming
    BaseDelay = TimeSpan.FromSeconds(5),
    MaxDelay = TimeSpan.FromMinutes(10),
    BackoffMultiplier = 2.0,
    
    // Streaming-specific settings
    ReconnectOnDisconnection = true,
    MaxReconnectAttempts = 10,
    ReconnectDelay = TimeSpan.FromSeconds(30),
    
    // Graceful degradation
    FallbackToPolling = true,
    PollingInterval = TimeSpan.FromMinutes(1)
};
```

## Logging Configuration

Comprehensive logging is crucial for monitoring, debugging, and maintaining Gnip client applications in production environments.

### Basic Logging Setup

Configure basic logging using the Microsoft.Extensions.Logging framework:

```csharp
var loggerFactory = LoggerFactory.Create(builder =>
{
    builder
        .AddConsole()
        .AddDebug()
        .SetMinimumLevel(LogLevel.Information);
});

var config = new GnipConfiguration
{
    // ... other configuration
    LoggerFactory = loggerFactory,
    EnableRequestLogging = true,
    EnableResponseLogging = true
};
```

### Structured Logging Configuration

Implement structured logging for better observability:

```csharp
var loggerFactory = LoggerFactory.Create(builder =>
{
    builder
        .AddSerilog(new LoggerConfiguration()
            .WriteTo.Console(new JsonFormatter())
            .WriteTo.File("logs/gnip-client-.log", 
                rollingInterval: RollingInterval.Day,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
            .Enrich.WithProperty("Application", "GnipClient")
            .Enrich.WithProperty("Environment", Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"))
            .CreateLogger());
});
```

### Performance and Diagnostic Logging

Configure detailed logging for performance monitoring and diagnostics:

```csharp
var diagnosticConfig = new GnipLoggingConfiguration
{
    LogLevel = LogLevel.Debug,
    
    // Request/Response logging
    LogRequests = true,
    LogResponses = true,
    LogHeaders = true,
    LogBody = false, // Disable in production for performance
    
    // Performance logging
    LogPerformanceMetrics = true,
    LogConnectionPoolStats = true,
    LogRetryAttempts = true,
    
    // Streaming-specific logging
    LogStreamingEvents = true,
    LogHeartbeats = false,
    LogReconnections = true,
    
    // Sensitive data handling
    MaskSensitiveData = true,
    SensitiveHeaders = new[] { "Authorization", "X-API-Key" },
    
    // Log filtering
    ExcludeHealthChecks = true,
    MinimumDuration = TimeSpan.FromMilliseconds(100)
};

var config = new GnipConfiguration
{
    LoggingConfiguration = diagnosticConfig
};
```

### Custom Logging Providers

Implement custom logging providers for specific requirements:

```csharp
public class GnipMetricsLogger : ILogger<GnipClient>
{
    private readonly IMetricsCollector _metricsCollector;
    
    public GnipMetricsLogger(IMetricsCollector metricsCollector)
    {
        _metricsCollector = metricsCollector;
    }
    
    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, 
        Exception exception, Func<TState, Exception, string> formatter)
    {
        // Custom logging logic
        if (eventId.Name == "RequestCompleted")
        {
            _metricsCollector.RecordRequestMetrics(state);
        }
        
        if (exception != null)
        {
            _metricsCollector.RecordError(exception);
        }
    }
    
    // ... other ILogger implementation
}
```

### Production Logging Best Practices

For production environments, implement these logging best practices:

```csharp
var productionLoggingConfig = new GnipLoggingConfiguration
{
    LogLevel = LogLevel.Warning, // Reduce noise in production
    LogRequests = false, // Disable detailed request logging
    LogResponses = false,
    LogPerformanceMetrics = true,
    LogRetryAttempts = true,
    LogReconnections = true,
    
    // Async logging for performance
    UseAsyncLogging = true,
    LogBufferSize = 1000,
    LogFlushInterval = TimeSpan.FromSeconds(5),
    
    // Log rotation and retention
    MaxLogFileSize = "100MB",
    MaxLogFiles = 30,
    
    // Correlation tracking
    EnableCorrelationIds = true,
    CorrelationIdHeader = "X-Correlation-ID"
};
```

## Configuration Validation and Best Practices

### Configuration Validation

Implement configuration validation to catch issues early:

```csharp
public static class GnipConfigurationValidator
{
    public static ValidationResult Validate(GnipConfiguration config)
    {
        var errors = new List<string>();
        
        if (string.IsNullOrEmpty(config.Account))
            errors.Add("Account is required");
            
        if (string.IsNullOrEmpty(config.Label))
            errors.Add("Label is required");
            
        if (config.ConnectionTimeout <= TimeSpan.Zero)
            errors.Add("ConnectionTimeout must be positive");
            
        if (config.Authentication?.Username == null)
            errors.Add("Authentication username is required");
            
        return new ValidationResult
        {
            IsValid = errors.Count == 0,
            Errors = errors
        };
    }
}
```

### Configuration Best Practices

1. **Environment Separation**: Use different configurations for development, staging, and production
2. **Secure Storage**: Store sensitive configuration in secure vaults or encrypted configuration
3. **Validation**: Always validate configuration at startup
4. **Monitoring**: Monitor configuration changes and their impact
5. **Documentation**: Document all configuration options and their effects
6. **Defaults**: Provide sensible defaults for optional configuration

## Troubleshooting Common Configuration Issues

### Connection Issues
- **Timeout Problems**: Increase `ConnectionTimeout` and `ReadTimeout` values
- **Pool Exhaustion**: Adjust `MaxConnectionPoolSize` based on load requirements
- **SSL Issues**: Verify certificate validation settings for your environment

### Authentication Failures
- **Credential Issues**: Verify username/password combination
- **Token Expiration**: Implement automatic token refresh mechanisms
- **Rate Limiting**: Configure appropriate retry policies with backoff

### Performance Issues
- **Logging Overhead**: Reduce logging verbosity in production
- **Buffer Sizes**: Optimize buffer sizes based on message volume
- **Connection Pooling**: Tune connection pool settings for your workload

This comprehensive configuration guide provides the foundation for successfully deploying and operating the Gnip .NET client in various environments while maintaining reliability, security, and performance.