# Getting Started

Welcome to the Gnip .NET API Client, a comprehensive library designed to simplify integration with Gnip's real-time social data streaming services. This client library provides a robust, event-driven architecture that enables developers to efficiently consume and process social media data streams from various platforms including Twitter, Facebook, and other social networks.

The Gnip .NET API Client abstracts the complexity of managing persistent connections, handling authentication, processing streaming data, and implementing retry logic, allowing you to focus on building powerful social media analytics and monitoring applications.

## Installation

### Prerequisites

Before installing the Gnip .NET API Client, ensure your development environment meets the following requirements:

- **.NET Framework**: Version 4.5 or higher, or .NET Core 2.0+
- **Visual Studio**: 2017 or later (recommended) or any compatible IDE
- **NuGet Package Manager**: Integrated with your development environment
- **Active Gnip Account**: Valid credentials and access to Gnip data streams
- **Network Configuration**: Ability to establish persistent HTTPS connections to Gnip endpoints

### NuGet Package Installation

The recommended installation method is through NuGet Package Manager:

#### Using Package Manager Console

```powershell
Install-Package Gnip.Client
```

#### Using .NET CLI

```bash
dotnet add package Gnip.Client
```

#### Using PackageReference in Project File

Add the following to your `.csproj` file:

```xml
<PackageReference Include="Gnip.Client" Version="2.1.0" />
```

### Manual Installation from Source

For development or customization purposes, you can clone and build from source:

```bash
git clone https://github.com/jbbrown/gnip-dotnet.git
cd gnip-dotnet
dotnet restore
dotnet build --configuration Release
```

### Verification of Installation

After installation, verify the package is correctly referenced by checking your project dependencies or running a simple import test:

```csharp
using Gnip.Client;
using Gnip.Client.Configuration;
using Gnip.Client.Events;

// If no compilation errors occur, installation was successful
```

## Quick Start Guide

### Basic Stream Consumer Implementation

The following example demonstrates how to quickly set up a basic Gnip stream consumer:

```csharp
using System;
using Gnip.Client;
using Gnip.Client.Configuration;
using Gnip.Client.Events;

class Program
{
    static void Main(string[] args)
    {
        // Configure the Gnip client
        var config = new GnipConfiguration
        {
            Username = "your-username",
            Password = "your-password",
            Account = "your-account-name",
            StreamLabel = "your-stream-label",
            StreamUrl = "https://gnip-stream.gnip.com/stream/powertrack/accounts/{account}/publishers/twitter/{stream}.json"
        };

        // Create and configure the stream client
        var client = new GnipStreamClient(config);

        // Subscribe to data events
        client.DataReceived += OnDataReceived;
        client.ConnectionEstablished += OnConnectionEstablished;
        client.ConnectionLost += OnConnectionLost;
        client.ErrorOccurred += OnErrorOccurred;

        // Start streaming
        client.StartAsync();

        // Keep the application running
        Console.WriteLine("Press any key to stop streaming...");
        Console.ReadKey();

        // Clean shutdown
        client.Stop();
    }

    private static void OnDataReceived(object sender, DataReceivedEventArgs e)
    {
        Console.WriteLine($"Received activity: {e.Data}");
        // Process your social media data here
    }

    private static void OnConnectionEstablished(object sender, EventArgs e)
    {
        Console.WriteLine("Connection established successfully");
    }

    private static void OnConnectionLost(object sender, EventArgs e)
    {
        Console.WriteLine("Connection lost - attempting to reconnect...");
    }

    private static void OnErrorOccurred(object sender, ErrorEventArgs e)
    {
        Console.WriteLine($"Error occurred: {e.Exception.Message}");
    }
}
```

### Advanced Configuration Example

For production environments, consider implementing more sophisticated configuration and error handling:

```csharp
var advancedConfig = new GnipConfiguration
{
    Username = Environment.GetEnvironmentVariable("GNIP_USERNAME"),
    Password = Environment.GetEnvironmentVariable("GNIP_PASSWORD"),
    Account = Environment.GetEnvironmentVariable("GNIP_ACCOUNT"),
    StreamLabel = Environment.GetEnvironmentVariable("GNIP_STREAM_LABEL"),
    
    // Connection settings
    ConnectionTimeout = TimeSpan.FromSeconds(30),
    ReadTimeout = TimeSpan.FromSeconds(90),
    MaxReconnectAttempts = 5,
    ReconnectDelay = TimeSpan.FromSeconds(10),
    
    // Buffer settings
    BufferSize = 8192,
    EnableCompression = true,
    
    // Logging
    EnableDetailedLogging = true
};

var client = new GnipStreamClient(advancedConfig);
```

## Authentication Setup

### Credential Management

Gnip uses HTTP Basic Authentication for API access. Proper credential management is crucial for security and reliability:

#### Environment Variables (Recommended)

Store credentials as environment variables to avoid hardcoding sensitive information:

```bash
# Windows
set GNIP_USERNAME=your-username
set GNIP_PASSWORD=your-password
set GNIP_ACCOUNT=your-account

# Linux/macOS
export GNIP_USERNAME=your-username
export GNIP_PASSWORD=your-password
export GNIP_ACCOUNT=your-account
```

#### Configuration File Approach

Create a secure configuration file (ensure it's excluded from version control):

```json
{
  "GnipSettings": {
    "Username": "your-username",
    "Password": "your-password",
    "Account": "your-account-name",
    "StreamLabel": "your-stream-label"
  }
}
```

Load configuration in your application:

```csharp
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json", optional: false)
    .AddEnvironmentVariables()
    .Build();

var gnipConfig = new GnipConfiguration
{
    Username = configuration["GnipSettings:Username"],
    Password = configuration["GnipSettings:Password"],
    Account = configuration["GnipSettings:Account"],
    StreamLabel = configuration["GnipSettings:StreamLabel"]
};
```

### Authentication Validation

Implement authentication validation to ensure credentials are working correctly:

```csharp
public async Task<bool> ValidateCredentialsAsync(GnipConfiguration config)
{
    try
    {
        var client = new GnipStreamClient(config);
        var result = await client.TestConnectionAsync();
        return result.IsSuccessful;
    }
    catch (UnauthorizedAccessException)
    {
        Console.WriteLine("Invalid credentials provided");
        return false;
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Authentication test failed: {ex.Message}");
        return false;
    }
}
```

### Security Best Practices

- **Never commit credentials** to version control systems
- **Use encrypted storage** for production credentials
- **Implement credential rotation** policies
- **Monitor authentication failures** and implement alerting
- **Use least-privilege access** principles for Gnip accounts

## Basic Configuration

### Core Configuration Parameters

The `GnipConfiguration` class provides comprehensive options for customizing client behavior:

```csharp
public class GnipConfiguration
{
    // Authentication
    public string Username { get; set; }
    public string Password { get; set; }
    public string Account { get; set; }
    public string StreamLabel { get; set; }
    
    // Connection settings
    public string StreamUrl { get; set; }
    public TimeSpan ConnectionTimeout { get; set; } = TimeSpan.FromSeconds(30);
    public TimeSpan ReadTimeout { get; set; } = TimeSpan.FromSeconds(90);
    public int MaxReconnectAttempts { get; set; } = 3;
    public TimeSpan ReconnectDelay { get; set; } = TimeSpan.FromSeconds(5);
    
    // Performance settings
    public int BufferSize { get; set; } = 4096;
    public bool EnableCompression { get; set; } = true;
    public int MaxConcurrentConnections { get; set; } = 1;
    
    // Logging and monitoring
    public bool EnableDetailedLogging { get; set; } = false;
    public LogLevel LogLevel { get; set; } = LogLevel.Information;
}
```

### Stream URL Configuration

Different Gnip products require specific URL patterns:

#### PowerTrack Streams
```csharp
StreamUrl = "https://gnip-stream.gnip.com/stream/powertrack/accounts/{account}/publishers/twitter/{stream}.json"
```

#### Decahose Streams
```csharp
StreamUrl = "https://gnip-stream.gnip.com/stream/decahose/accounts/{account}/publishers/twitter/{stream}.json"
```

#### Historical PowerTrack
```csharp
StreamUrl = "https://gnip-api.gnip.com/historical/powertrack/accounts/{account}/publishers/twitter/historical/track/jobs.json"
```

### Event-Driven Configuration

Configure event handlers for different scenarios:

```csharp
var client = new GnipStreamClient(config);

// Data processing events
client.DataReceived += (sender, e) => {
    // Handle incoming social media activities
    ProcessActivity(e.Data);
};

client.HeartbeatReceived += (sender, e) => {
    // Handle keepalive messages
    UpdateConnectionStatus();
};

// Connection management events
client.ConnectionEstablished += (sender, e) => {
    // Log successful connections
    Logger.Info("Stream connection established");
};

client.ConnectionLost += (sender, e) => {
    // Handle disconnections
    Logger.Warning("Stream connection lost");
    NotifyMonitoringSystem();
};

// Error handling events
client.ErrorOccurred += (sender, e) => {
    // Comprehensive error handling
    Logger.Error($"Stream error: {e.Exception}");
    
    if (e.Exception is RateLimitExceededException)
    {
        // Handle rate limiting
        ImplementBackoffStrategy();
    }
    else if (e.Exception is AuthenticationException)
    {
        // Handle auth failures
        RefreshCredentials();
    }
};
```

### Performance Optimization Configuration

For high-throughput scenarios, optimize performance settings:

```csharp
var highPerformanceConfig = new GnipConfiguration
{
    // Increase buffer size for high-volume streams
    BufferSize = 16384,
    
    // Enable compression to reduce bandwidth
    EnableCompression = true,
    
    // Optimize timeouts for your network conditions
    ConnectionTimeout = TimeSpan.FromSeconds(45),
    ReadTimeout = TimeSpan.FromMinutes(2),
    
    // Configure aggressive reconnection
    MaxReconnectAttempts = 10,
    ReconnectDelay = TimeSpan.FromSeconds(2),
    
    // Enable detailed monitoring
    EnableDetailedLogging = true
};
```

### Troubleshooting Common Configuration Issues

#### Connection Timeouts
If experiencing frequent timeouts, adjust timeout values:
```csharp
config.ConnectionTimeout = TimeSpan.FromMinutes(1);
config.ReadTimeout = TimeSpan.FromMinutes(3);
```

#### Memory Usage Optimization
For memory-constrained environments:
```csharp
config.BufferSize = 2048;  // Reduce buffer size
config.EnableCompression = true;  // Reduce memory footprint
```

#### Network Reliability Issues
For unreliable networks:
```csharp
config.MaxReconnectAttempts = 15;
config.ReconnectDelay = TimeSpan.FromSeconds(30);
```

### Logging and Monitoring Configuration

Implement comprehensive logging for production deployments:

```csharp
// Configure logging
var loggerFactory = LoggerFactory.Create(builder => 
    builder.AddConsole()
           .AddFile("logs/gnip-client.log")
           .SetMinimumLevel(LogLevel.Information));

var logger = loggerFactory.CreateLogger<GnipStreamClient>();

// Pass logger to client
var client = new GnipStreamClient(config, logger);
```

This comprehensive Getting Started guide provides the foundation for successfully implementing the Gnip .NET API Client in your applications. The event-driven architecture ensures efficient processing of real-time social media data while maintaining robust error handling and connection management capabilities.

## Next Steps

After completing the basic setup, consider exploring:

- **Advanced Filtering**: Implement sophisticated data filtering and routing
- **Scaling Strategies**: Design for high-availability and horizontal scaling
- **Data Processing Pipelines**: Integrate with analytics and storage systems
- **Monitoring and Alerting**: Implement comprehensive operational monitoring

For additional resources and advanced configuration options, refer to the [API Reference Documentation](../api-reference/) and [Advanced Configuration Guide](../advanced-configuration/).