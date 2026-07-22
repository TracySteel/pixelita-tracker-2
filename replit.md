# Overview

Pixelita is a lightweight Flask-based tracking pixel server designed to monitor QR code scans and user interactions. The application serves a transparent 1x1 pixel image that can be embedded in web pages or QR code landing pages to track user engagement. When accessed, it logs visitor data including timestamps, unique identifiers (PIDs), IP addresses, and user agent strings to a CSV file for analytics purposes.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
The application is built on Flask, a lightweight Python web framework chosen for its simplicity and minimal overhead. Flask is well-suited for this microservice-style application that serves a single primary endpoint.

## Proxy Configuration
Uses Werkzeug's ProxyFix middleware to properly handle proxy headers in production environments. This ensures accurate IP address logging when deployed behind reverse proxies or load balancers.

## Data Storage
Implements file-based CSV storage using pandas for data manipulation. This approach was chosen for simplicity and eliminates the need for a separate database server, making deployment straightforward. The CSV format allows for easy data export and analysis.

## Security Measures
Includes CSV injection prevention by sanitizing user inputs. Any field starting with potentially dangerous characters (=, +, -, @, tabs, returns, spaces) is prefixed with an apostrophe to neutralize potential formula injection attacks.

## Static File Serving
Serves static content from a dedicated 'pixelita' folder, including the test HTML page and the transparent tracking pixel image.

## Request Handling
The main tracking endpoint (`/hit.gif`) accepts a `pid` parameter to identify unique tracking instances and logs comprehensive request metadata for analytics.

# External Dependencies

## Python Packages
- **Flask**: Core web framework for handling HTTP requests and responses
- **pandas**: Data manipulation library used for CSV file operations and data structuring
- **gunicorn**: WSGI HTTP server for production deployment (noted as duplicated in requirements.txt)

## File Dependencies
- **transparent.png**: 1x1 transparent pixel image served as the tracking beacon
- **pixel_log.csv**: Data storage file for tracking logs, automatically created with proper headers if missing

## Runtime Requirements
The application expects a writable filesystem for CSV log storage and requires the transparent PNG file to be present for proper tracking functionality.