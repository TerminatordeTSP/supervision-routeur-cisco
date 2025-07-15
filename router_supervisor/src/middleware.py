"""
Database Error Handling Middleware

This middleware catches database-related errors and provides helpful error pages
to guide users on how to fix common database issues.
"""

from django.http import HttpResponse
from django.db import OperationalError, ProgrammingError
import logging

logger = logging.getLogger(__name__)


class DatabaseErrorMiddleware:
    """
    Middleware to handle database errors gracefully and provide helpful error messages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except (OperationalError, ProgrammingError) as e:
            return self.handle_database_error(request, e)

    def handle_database_error(self, request, error):
        """
        Handle database errors and return a helpful error page.
        """
        logger.error(f"Database error on {request.path}: {error}")
        
        # Check if it's a missing table error
        if "does not exist" in str(error) and "relation" in str(error):
            return self.missing_table_error(error)
        
        # Check if it's a connection error
        if "connection" in str(error).lower():
            return self.connection_error(error)
        
        # Generic database error
        return self.generic_database_error(error)

    def missing_table_error(self, error):
        """Handle missing table errors (usually means migrations not run)"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Setup Required</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f8f9fa;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .success {{ color: #28a745; }}
                pre {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 4px; 
                    border-left: 4px solid #007bff;
                    overflow-x: auto;
                }}
                .step {{ 
                    margin: 20px 0; 
                    padding: 15px; 
                    border-left: 4px solid #17a2b8; 
                    background: #e7f3ff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">🚨 Database Setup Required</h1>
                
                <p class="warning">
                    <strong>The database tables are missing!</strong> 
                    This usually happens when Django migrations haven't been run yet.
                </p>
                
                <div class="step">
                    <h3>🔧 Quick Fix</h3>
                    <p>If you're using Docker, restart the container to trigger automatic database setup:</p>
                    <pre>docker-compose restart router_django</pre>
                </div>
                
                <div class="step">
                    <h3>🛠️ Manual Fix</h3>
                    <p>Run these commands to set up the database manually:</p>
                    <pre>
# Enter the Django container
docker-compose exec router_django bash

# Run database initialization
python3 /code/router_supervisor/manage.py initialize_db

# Or run migrations manually
python3 /code/router_supervisor/manage.py makemigrations
python3 /code/router_supervisor/manage.py migrate</pre>
                </div>
                
                <div class="step">
                    <h3>🔍 Check Database Health</h3>
                    <p>After running migrations, you can check the database status:</p>
                    <pre>python3 /code/router_supervisor/manage.py dbhealth</pre>
                </div>
                
                <details>
                    <summary>Technical Details</summary>
                    <pre class="error">{error}</pre>
                </details>
                
                <p><a href="javascript:window.location.reload()">🔄 Reload page after fixing</a></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, status=503)

    def connection_error(self, error):
        """Handle database connection errors"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Connection Error</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f8f9fa;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .error {{ color: #dc3545; }}
                pre {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 4px; 
                    border-left: 4px solid #dc3545;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">🔌 Database Connection Error</h1>
                <p>Cannot connect to the database. Please check if the database server is running.</p>
                
                <h3>Troubleshooting Steps:</h3>
                <ol>
                    <li>Check if PostgreSQL container is running: <code>docker-compose ps</code></li>
                    <li>Restart the database: <code>docker-compose restart db</code></li>
                    <li>Check database logs: <code>docker-compose logs db</code></li>
                </ol>
                
                <details>
                    <summary>Technical Details</summary>
                    <pre class="error">{error}</pre>
                </details>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, status=503)

    def generic_database_error(self, error):
        """Handle generic database errors"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Error</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f8f9fa;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .error {{ color: #dc3545; }}
                pre {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 4px; 
                    border-left: 4px solid #dc3545;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">⚠️ Database Error</h1>
                <p>A database error occurred. Please contact the administrator or try again later.</p>
                
                <details>
                    <summary>Technical Details</summary>
                    <pre class="error">{error}</pre>
                </details>
                
                <p><a href="javascript:window.location.reload()">🔄 Try again</a></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, status=500)
