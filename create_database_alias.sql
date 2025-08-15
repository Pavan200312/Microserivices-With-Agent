-- Create a database alias to avoid space issues
-- Run this in your PostgreSQL query tool

-- Create a new database without spaces
CREATE DATABASE "newdb";

-- Grant all privileges to postgres user
GRANT ALL PRIVILEGES ON DATABASE "newdb" TO postgres;

-- Copy all data from "new DB" to "newdb"
-- Note: You'll need to run this after creating the new database
-- pg_dump -h localhost -U postgres -d "new DB" | psql -h localhost -U postgres -d newdb
