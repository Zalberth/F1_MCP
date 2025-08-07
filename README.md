# F1 MCP Servers

This repository contains two comprehensive MCP (Model Context Protocol) servers for accessing Formula 1 racing data:

1. **FastF1 MCP Server** (`fastf1_mcp_server.py`) - Advanced server using FastF1 library
2. **Basic F1 MCP Server** (`f1_mcp_server.py`) - Simple server using Ergast API

## FastF1 MCP Server (Recommended)

A comprehensive MCP server built with the [FastF1 library](https://docs.fastf1.dev/) that provides complete access to F1 data including telemetry, weather, track status, and advanced analytics.

### Features

- **Complete Session Data**: Practice, qualifying, and race sessions
- **Telemetry Data**: Speed, throttle, brake, gear, RPM data
- **Weather Information**: Temperature, humidity, wind conditions
- **Track Status**: Safety car periods, VSC, red flags
- **Lap Analysis**: Detailed lap times, sectors, compounds
- **Championship Standings**: Driver and constructor championships
- **Historical Data**: Results from 1950 to present
- **Advanced Analytics**: Driver comparisons, statistics, performance metrics
- **Caching System**: Optimized data retrieval with local caching

### Installation

#### Prerequisites

- Python 3.8 or higher
- Required Python packages:
  ```bash
  pip install fastf1 pandas numpy matplotlib scipy tqdm requests urllib3
  ```

#### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python fastf1_mcp_server.py
   ```

### Available Tools

#### Core Session Tools
- `get_event_schedule` - Get F1 event calendar
- `get_session` - Load specific session data
- `get_session_results` - Get session results

#### Telemetry & Lap Data
- `get_lap_times` - Get driver lap times
- `get_telemetry` - Get detailed telemetry data

#### Weather & Track Status
- `get_weather_data` - Get weather conditions
- `get_track_status` - Get track status changes

#### Driver & Team Information
- `get_driver_info` - Get driver details
- `get_team_info` - Get team information

#### Championship Standings
- `get_driver_standings` - Get driver championship
- `get_constructor_standings` - Get constructor championship

#### Historical Data
- `get_historical_results` - Get historical race results
- `get_lap_records` - Get circuit lap records

#### Advanced Analytics
- `calculate_driver_statistics` - Calculate driver statistics
- `compare_drivers` - Compare two drivers' performance

#### Configuration
- `configure_cache` - Configure cache settings
- `get_cache_info` - Get cache information

### Usage Examples

```json
{
  "name": "get_session",
  "arguments": {
    "year": 2024,
    "gp": "Monaco",
    "session": "R"
  }
}
```

```json
{
  "name": "get_telemetry",
  "arguments": {
    "year": 2024,
    "gp": "Monaco",
    "session": "R",
    "driver": "VER",
    "lap": 10
  }
}
```

### Supported Sessions

- **FP1, FP2, FP3**: Free Practice sessions
- **Q**: Qualifying
- **SQ**: Sprint Qualifying
- **R**: Race
- **Sprint**: Sprint race

### Supported Driver Codes

- **VER**: Max Verstappen
- **HAM**: Lewis Hamilton
- **LEC**: Charles Leclerc
- **SAI**: Carlos Sainz
- **NOR**: Lando Norris
- **RUS**: George Russell
- **PER**: Sergio Perez
- **ALO**: Fernando Alonso
- And many more...

## Basic F1 MCP Server

A simple MCP server that uses the Ergast API to provide basic F1 data access.

### Features

- **Driver Information**: Get comprehensive driver lists for any F1 season
- **Race Results**: Retrieve detailed race results for specific drivers and seasons
- **Statistical Analysis**: Calculate average positions and performance metrics
- **MCP Compliance**: Fully compliant with MCP protocol version 2024-11-05
- **Robust Error Handling**: Built-in retry mechanisms and error responses

### Installation

#### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  ```bash
  pip install requests urllib3
  ```

#### Setup

```bash
python f1_mcp_server.py
```

### Available Tools

- `get_drivers` - Get driver list for a season
- `get_driver_results` - Get driver race results
- `calculate_average_position` - Calculate average finishing position

## MCP Client Integration

Both servers support standard MCP protocol methods:

- `initialize` - Initialize the server connection
- `tools/list` - List available tools
- `tools/call` - Execute tool functions
- `resources/list` - List available resources
- `resources/read` - Read resource content

### Configuration Example

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "fastf1": {
      "command": "python",
      "args": ["/path/to/DATA_F1_MCP/fastf1_mcp_server.py"]
    }
  }
}
```

## Available Resources

### FastF1 Server
- `f1://schedule/current` - Current season schedule
- `f1://standings/drivers` - Driver championship standings
- `f1://standings/constructors` - Constructor championship standings

### Basic Server
- `f1://drivers/2025` - Current season driver list

## API Data Sources

### FastF1 Server
- **FastF1 Library**: Comprehensive F1 data from official sources
- **Ergast API**: Historical data and championship information
- **F1 Official API**: Real-time data and telemetry

### Basic Server
- **Ergast API**: Historical F1 data from 1950 to present

## Error Handling

Both servers implement comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **API Errors**: Graceful handling of API rate limits and server errors
- **Data Errors**: Validation and fallback for missing or invalid data
- **MCP Errors**: Standard JSON-RPC error responses

### Common Error Codes

- `-32700`: Parse error (invalid JSON)
- `-32601`: Method not found
- `-32602`: Invalid parameters
- `-32603`: Internal error

## Development

### Project Structure

```
DATA_F1_MCP/
├── fastf1_mcp_server.py    # Advanced FastF1-based server
├── f1_mcp_server.py        # Basic Ergast API server
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── examples.py            # Usage examples
├── mcp-config.json       # MCP configuration template
├── temp/                 # Temporary files
└── README.md             # This file
```

### Testing

To test the servers manually:

```bash
# Test FastF1 server
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python fastf1_mcp_server.py

# Test basic server
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python f1_mcp_server.py
```

### Examples

Run the examples to see usage patterns:

```bash
python examples.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Acknowledgments

- [FastF1](https://docs.fastf1.dev/) for comprehensive F1 data access
- [Ergast API](http://ergast.com/mrd/) for historical F1 data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the communication standard
- Formula 1 community for the passion that drives this project

## Support

For issues, questions, or contributions, please use the GitHub repository's issue tracker.