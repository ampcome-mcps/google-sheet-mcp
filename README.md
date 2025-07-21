# 📊 Google Sheets MCP Server

A comprehensive **Model Context Protocol (MCP) server** for Google Sheets API v4 with **Nango authentication**. This server provides structured output for all Google Sheets operations with automatic token management and robust error handling.

## ✨ Features

- 🔐 **Nango Authentication** - Secure OAuth token management
- 📋 **Complete API Coverage** - All Google Sheets API v4 endpoints
- 🛡️ **Robust Error Handling** - Custom exceptions and detailed error messages  
- 📊 **Structured Output** - Pydantic models for type-safe responses
- 🔄 **Auto Token Refresh** - Seamless authentication handling
- 🚀 **Production Ready** - Comprehensive logging and validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Sheets API access
- Nango account and integration setup

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd google-sheets-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export NANGO_CONNECTION_ID="your-connection-id"
   export NANGO_INTEGRATION_ID="google-sheets"  
   export NANGO_BASE_URL="https://api.nango.dev"
   export NANGO_SECRET_KEY="your-secret-key"
   ```

4. **Run the server**
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NANGO_CONNECTION_ID` | Your Nango connection ID | ✅ |
| `NANGO_INTEGRATION_ID` | Integration ID (usually "google-sheets") | ✅ |
| `NANGO_BASE_URL` | Nango API base URL | ✅ |
| `NANGO_SECRET_KEY` | Your Nango secret key | ✅ |

### Nango Setup

1. **Create a Nango account** at [nango.dev](https://nango.dev)
2. **Set up Google Sheets integration** in your Nango dashboard
3. **Get your credentials** from the Nango dashboard
4. **Configure the environment variables** as shown above

## 📚 Available Tools

### 📊 Spreadsheet Operations
- `spreadsheets_create` - Create new spreadsheets
- `spreadsheets_get` - Get spreadsheet metadata
- `spreadsheets_batch_update` - Apply multiple updates
- `spreadsheets_get_by_data_filter` - Get filtered data

### 📝 Value Operations
- `values_get` - Get values from ranges
- `values_update` - Update cell values
- `values_append` - Append data to sheets
- `values_clear` - Clear cell values
- `values_batch_get` - Get multiple ranges
- `values_batch_update` - Update multiple ranges
- `values_batch_clear` - Clear multiple ranges

### 🔍 Data Filter Operations
- `values_batch_get_by_data_filter` - Get values with filters
- `values_batch_update_by_data_filter` - Update values with filters
- `values_batch_clear_by_data_filter` - Clear values with filters

### 🏷️ Metadata Operations
- `developer_metadata_get` - Get metadata by ID
- `developer_metadata_search` - Search metadata

### 🛠️ Utility Operations
- `get_server_info` - Server status and configuration
- `test_connection` - Test API connectivity
- `refresh_nango_token` - Manually refresh tokens

## 💡 Usage Examples

### Creating a New Spreadsheet
```json
{
  "tool": "spreadsheets_create",
  "arguments": {
    "title": "My New Spreadsheet",
    "sheets": [
      {
        "properties": {
          "title": "Sales Data"
        }
      }
    ]
  }
}
```

### Updating Cell Values
```json
{
  "tool": "values_update",
  "arguments": {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "range": "A1:C2",
    "values": [
      ["Name", "Age", "City"],
      ["John Doe", "30", "New York"]
    ],
    "value_input_option": "USER_ENTERED"
  }
}
```

### Adding Data with Formulas
```json
{
  "tool": "values_update",
  "arguments": {
    "spreadsheet_id": "your-spreadsheet-id",
    "range": "A1:C3",
    "values": [
      ["Product", "Quantity", "Total"],
      ["Widget", "5", "=B2*10"],
      ["Gadget", "3", "=B3*15"]
    ],
    "value_input_option": "USER_ENTERED"
  }
}
```

### Batch Operations
```json
{
  "tool": "values_batch_update",
  "arguments": {
    "spreadsheet_id": "your-spreadsheet-id",
    "data": [
      {
        "range": "Sheet1!A1:B2",
        "values": [["Header 1", "Header 2"], ["Data 1", "Data 2"]]
      },
      {
        "range": "Sheet2!A1:A3", 
        "values": [["Item 1"], ["Item 2"], ["Item 3"]]
      }
    ],
    "value_input_option": "RAW"
  }
}
```

## 🔍 Parameter Reference

### Common Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `spreadsheet_id` | string | The spreadsheet ID from the URL | Required |
| `range` | string | A1 notation (e.g., "A1:C3", "Sheet1!A1") | Required |
| `values` | array | 2D array of values `[["row1"], ["row2"]]` | Required |
| `value_input_option` | string | `"RAW"` or `"USER_ENTERED"` | `"USER_ENTERED"` |
| `major_dimension` | string | `"ROWS"` or `"COLUMNS"` | `"ROWS"` |

### Value Input Options

- **`RAW`** - Values are stored exactly as provided
- **`USER_ENTERED`** - Values are parsed (formulas calculated, dates formatted)

### Range Notation Examples

- `A1` - Single cell
- `A1:C3` - Rectangle from A1 to C3
- `A:A` - Entire column A
- `1:1` - Entire row 1
- `Sheet1!A1:B5` - Range in specific sheet
- `'My Sheet'!A1:C3` - Sheet with spaces in name

## ⚠️ Error Handling

The server provides detailed error messages for common issues:

### Authentication Errors
```
AuthenticationError: Missing required environment variables: NANGO_SECRET_KEY
```
**Solution**: Check your Nango environment variables

### Permission Errors  
```
AuthorizationError: Permission denied: The caller does not have permission
```
**Solution**: Check spreadsheet sharing permissions

### Validation Errors
```
ValidationError: Bad request: Range 'InvalidRange' is not valid A1 notation
```
**Solution**: Use proper A1 notation like 'A1:B2'

### Resource Not Found
```
ResourceNotFoundError: Requested entity was not found
```
**Solution**: Verify the spreadsheet ID is correct

## 🧪 Testing

### Test Connection
```json
{
  "tool": "test_connection",
  "arguments": {}
}
```

This creates a test spreadsheet to verify your setup is working correctly.

### Get Server Info
```json
{
  "tool": "get_server_info", 
  "arguments": {}
}
```

Returns server status, authentication state, and available tools.

## 📋 Requirements

Create a `requirements.txt` file:

```
mcp>=1.0.0
pydantic>=2.0.0
requests>=2.25.0
fastmcp>=0.1.0
```

## 🚨 Troubleshooting

### Server Won't Start
1. Check Python version (3.8+ required)
2. Verify all environment variables are set
3. Ensure dependencies are installed

### Authentication Issues
1. Verify Nango credentials in dashboard
2. Check integration is properly configured
3. Test with `refresh_nango_token` tool

### API Errors
1. Check spreadsheet exists and is accessible
2. Verify proper A1 notation in ranges
3. Ensure required parameters are provided

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "valueInputOption is required" | Missing required parameter | Use default `"USER_ENTERED"` |
| "Invalid range" | Malformed A1 notation | Check range format |
| "Permission denied" | Access issues | Check sharing settings |
| "Connection timeout" | Network issues | Check internet connection |

## 📖 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Nango Documentation](https://docs.nango.dev)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [A1 Notation Guide](https://developers.google.com/sheets/api/guides/concepts#expandable-1)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

For issues and questions:
- Check the troubleshooting section above
- Review Google Sheets API documentation
- Verify Nango integration setup

---

**Happy spreadsheeting! 📊✨**