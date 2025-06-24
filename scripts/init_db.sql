-- Database initialization script for Router Supervisor
-- This script is executed when PostgreSQL container starts

-- Create the database if it doesn't exist
SELECT 'CREATE DATABASE routerdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'routerdb')\gexec

-- Connect to the database
\c routerdb;

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create a schema for metrics if needed
CREATE SCHEMA IF NOT EXISTS metrics;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE routerdb TO "user";
GRANT ALL PRIVILEGES ON SCHEMA public TO "user";
GRANT ALL PRIVILEGES ON SCHEMA metrics TO "user";

-- Create indexes for better performance (these will be created after Django migrations)
-- These are just placeholders - Django will create the actual tables

-- Log the completion
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END $$;
