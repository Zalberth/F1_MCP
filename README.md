# F1 MCP Server

A Model Context Protocol (MCP) server that provides Formula 1 racing data through the Ergast API. This server allows AI assistants and other MCP clients to access F1 driver information, race results, and statistical calculations.

## Features

- **Driver Information**: Get comprehensive driver lists for any F1 season
- **Race Results**: Retrieve detailed race results for specific drivers and seasons
- **Statistical Analysis**: Calculate average positions and performance metrics
- **MCP Compliance**: Fully compliant with MCP protocol version 2024-11-05
- **Robust Error Handling**: Built-in retry mechanisms and error responses
- **Resource Management**: Structured resource access through URI-based system

## Installation

### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  ```bash
  pip install requests urllib3
  ```

### Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd DATA_F1_MCP
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install requests urllib3
   ```

3. Make the server executable:
   ```bash
   chmod +x f1_mcp_server.py
   ```

## Usage

### Running the Server

The server communicates via stdin/stdout following the MCP protocol:

```bash
python f1_mcp_server.py
```

### MCP Client Integration

To use this server with an MCP client, configure it in your client's settings. The server supports the following MCP methods:

- `initialize` - Initialize the server connection
- `tools/list` - List available tools
- `tools/call` - Execute tool functions
- `resources/list` - List available resources
- `resources/read` - Read resource content

## Available Tools

### 1. get_drivers

Retrieve the list of F1 drivers for a specific season.

**Parameters:**
- `year` (integer, optional): Season year (default: 2025)

**Example:**
```json
{
  "name": "get_drivers",
  "arguments": {
    "year": 2024
  }
}
```

### 2. get_driver_results

Get race results for a specific driver in a given season.

**Parameters:**
- `driver_id` (string, required): Driver identifier (e.g., "hamilton", "verstappen")
- `year` (integer, required): Season year

**Example:**
```json
{
  "name": "get_driver_results",
  "arguments": {
    "driver_id": "hamilton",
    "year": 2024
  }
}
```

### 3. calculate_average_position

Calculate the average finishing position for a driver in a season.

**Parameters:**
- `driver_id` (string, required): Driver identifier
- `year` (integer, required): Season year

**Example:**
```json
{
  "name": "calculate_average_position",
  "arguments": {
    "driver_id": "verstappen",
    "year": 2024
  }
}
```

## Available Resources

### f1://drivers/2025

Provides the current season's driver list as a JSON resource.

**URI:** `f1://drivers/2025`  
**MIME Type:** `application/json`  
**Description:** Complete list of drivers for the 2025 F1 season

## API Data Source

This server uses the [Ergast API](http://ergast.com/mrd/) to fetch F1 data. The Ergast API provides:

- Historical F1 data from 1950 to present
- Driver, constructor, and race information
- Qualifying and race results
- Championship standings

**Base URL:** `http://api.jolpi.ca/ergast/f1`

## Error Handling

The server implements comprehensive error handling:

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

### Testing

To test the server manually, you can send JSON-RPC requests via stdin:

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python f1_mcp_server.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Acknowledgments

- [Ergast API](http://ergast.com/mrd/) for providing comprehensive F1 data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the communication standard
- Formula 1 community for the passion that drives this project

## Support

For issues, questions, or contributions, please use the GitHub repository's issue tracker.