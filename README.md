## Environment Variables

The application requires the following environment variables to be set:

- `DATABASE_URL`: The URL of the database. Example:
  ```
  DATABASE_URL=postgresql://username:password@hostname:port/database_name
  ```
  - `username`: Your database username
  - `password`: Your database password
  - `hostname`: The database server's hostname or IP address
  - `port`: The port number (default for PostgreSQL is 5432)
  - `database_name`: The name of your database

You can set these variables in your system or in a `.env` file in the project root.
