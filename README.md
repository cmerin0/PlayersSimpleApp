# Soccer Players API

This repository contains a Flask-based REST API for managing soccer players, teams, and user authentication. It uses Docker Compose for easy setup and deployment.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Health Checks](#health-checks)
- [Contributing](#contributing)
- [License](#license)

## Features

-   **User Authentication:** Secure login, registration, and logout functionalities.
-   **Team Management:** Create, read, update, and delete team information.
-   **Player Management:** Create, read, update, and delete player information.
-   **Database Integration:** Uses MySQL for persistent data storage.
-   **Caching:** Utilizes Redis for caching frequently accessed data.
-   **Load Balancing and Reverse Proxy:** Nginx acts as a reverse proxy for load balancing and handling HTTPS.
-   **Containerized Deployment:** Docker Compose for easy setup and deployment across different environments.
-   **Health Checks:** healthchecks for each service.

## Prerequisites

-   Docker and Docker Compose installed.

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/cmerin0/PlayersSimpleApp
    cd playersapp
    ```

2.  Create a `.env` file in the root directory and populate it with the required environment variables (see [Environment Variables](#environment-variables)).

3.  Start the Docker containers:

    ```bash
    docker-compose up --build
    ```

## Usage

Once the containers are running, you can access the API at `http://localhost` (or `https://localhost` if you have configured SSL certificates in `nginx/certs`).

## API Endpoints

### User Authentication

-   `POST /login`: Authenticate a user and return a JWT token.
-   `POST /register`: Register a new user.
-   `POST /logout`: Logout the current user (requires authentication).

### Users

-   `GET /users`: Retrieve a list of users (requires authentication).

### Teams

-   `GET /teams`: Retrieve a list of teams.
-   `POST /teams`: Create a new team (requires authentication).
-   `GET /teams/{id}`: Retrieve a specific team by ID.
-   `PUT /teams/{id}`: Update a team by ID (requires authentication).
-   `DELETE /teams/{id}`: Delete a team by ID (requires authentication).
-   `GET /teams/players`: retrieve all players from all teams.

### Players

-   `GET /players`: Retrieve a list of players.
-   `POST /players`: Create a new player (requires authentication).
-   `GET /players/{id}`: Retrieve a specific player by ID.
-   `PUT /players/{id}`: Update a player by ID (requires authentication).
-   `POST /players/{id}`: update or add a player to a team (requires authentication).

### Health

-   `GET /health`: Health check endpoint for the application.
-   `GET /health` on nginx: health check endpoint for the proxy.

## Project Structure

.  
├── .docker-compose.yaml  
├── .dockerignore  
├── Dockerfile  
├── main.py  
├── Readme.md  
├── requirements.txt  
├── .github/  
├── nginx/  
│   └── certs/  
├── src/  
└── tests/  

-   `docker-compose.yml`: Defines the services, networks, and volumes.  
-   `.env`: Stores environment variables.  
-   `main.py`: Contains the Flask application code.  
-   `nginx/nginx.conf`: Nginx configuration file for reverse proxy and load balancing.  
-   `nginx/certs/`: Directory for SSL certificates (if HTTPS is used).  

## Environment Variables

Create a `.env` file in the root directory and add the following variables:

- APP_PORT=5000  
- MYSQL_ROOT_PASSWORD=<your_mysql_root_password>  
- MYSQL_USER=<your_mysql_user>  
- MYSQL_PASSWORD=<your_mysql_password>  
- MYSQL_DATABASE=<your_mysql_database>  
- MYSQL_PORT=3306  
- SECRET_KEY=<your_flask_secret_key>  

-   `APP_PORT`: Port on which the Flask application runs.  
-   `MYSQL_ROOT_PASSWORD`: Root password for MySQL.  
-   `MYSQL_USER`: MySQL user for the application.  
-   `MYSQL_PASSWORD`: MySQL password for the application user.  
-   `MYSQL_DATABASE`: MySQL database name.  
-   `MYSQL_PORT`: Port that mysql is running on.  
-   `SECRET_KEY`: Secret key for Flask application.  

## Health Checks

Each service includes a health check to ensure it is running correctly.

-   **App:** Checks if the Flask application is responding to `/health`.
-   **DB:** Checks if the MySQL database is responding to ping requests.
-   **Proxy:** Checks if the Nginx proxy is responding to `/health` over HTTPS.
-   **Cache:** Uses redis internal health check.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

[MIT](LICENSE)