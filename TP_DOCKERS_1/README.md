## TP 01 : Docker


### 1-1 Why is it better to pass environment variables with `-e` rather than in the Dockerfile?

Anything written in the Dockerfile is baked into the image: anyone who can pull the image can read the password (`docker inspect`, `docker history`), and it ends up in Git. With `-e` (or an `.env` file), secrets stay outside the image and the code repository, and the **same image** can be reused with different values in each environment (dev, test, prod).

```bash
docker run -d --name postgres_container --network app-network \
  -e POSTGRES_DB=db -e POSTGRES_USER=usr -e POSTGRES_PASSWORD=pwd \
  tp-database
```

### 1-2 Why do we need a volume attached to our Postgres container?

A volume stores data outsite the container, on the host, so that it survives the container removal: had we not attached a volume, the destruction of the container would delete all data.

### 1-3 Document your database container essentials: commands and Dockerfile.

**Dockerfile** (`database/Dockerfile`)

```dockerfile
FROM postgres:17.2-alpine

COPY sql/ /docker-entrypoint-initdb.d/
```

The scripts copied into `/docker-entrypoint-initdb.d/` are run in alphabetical order on the first start (empty data folder): `01-CreateScheme.sql` creates the `departments` and `students` tables, `02-InsertData.sql` inserts the initial data.

**Commands**

```bash
# Network shared by all containers
docker network create app-network

# Build the image
docker build -t tp-database ./database

# Run the database with a persistent volume
docker run -d --name postgres_container --network app-network \
  -e POSTGRES_DB=db -e POSTGRES_USER=usr -e POSTGRES_PASSWORD=pwd \
  -v postgresvolume:/var/lib/postgresql/data \
  tp-database

# Adminer to browse the database (http://localhost:8090)
docker run -d --name adminer --network app-network -p 8090:8080 adminer

# Checks
docker ps
docker logs postgres_container
```

### 1-4 Why do we need a multistage build? And explain each step of this dockerfile.

Building a Java app needs a **JDK and Maven**, but running it only needs a **JRE**. A multistage build compiles in a first, heavy image and copies only the resulting `.jar` into a second, light image. The final image is smaller, faster to pull, and more secure (no compiler, no Maven, no source code inside). It also removes the need to install Java or Maven on the host.

```dockerfile
# Build
FROM eclipse-temurin:21-jdk-alpine AS myapp-build   # JDK image to compile, named "myapp-build"
ENV MYAPP_HOME=/opt/myapp                            # variable for the app folder
WORKDIR $MYAPP_HOME                                  # create it and move into it
RUN apk add --no-cache maven                         # install Maven
COPY pom.xml .                                       # copy the build descriptor
COPY src ./src                                       # copy the source code
RUN mvn package -DskipTests                          # compile and package into target/*.jar

# Run
FROM eclipse-temurin:21-jre-alpine                   # light JRE-only image
ENV MYAPP_HOME=/opt/myapp
WORKDIR $MYAPP_HOME
COPY --from=myapp-build $MYAPP_HOME/target/*.jar $MYAPP_HOME/myapp.jar   # take only the jar from stage 1
ENTRYPOINT ["java", "-jar", "myapp.jar"]             # start the API when the container starts
```

The backend reaches the database by its container name on `app-network`, configured in `application.yml`:

```yaml
datasource:
  url: jdbc:postgresql://postgres_container:5432/db
```

### 1-5 Why do we need a reverse proxy?

It's the single entry point that forwards requests to the API while the backend and database stay hidden on the internal network. It's also where HTTPS, load balancing and caching is added.


### 1-6 Why is docker-compose so important?

It defines the entire app in one versioned file, so that a single command can build and stop everything at the same time. It's very important in order to avoid having to do that manually.

### 1-7 Document docker-compose most important commands.

| Command | Purpose |
|---|---|
| `docker compose up -d` | Create and start all services in the background |
| `docker compose up -d --build` | Rebuild the images, then start |
| `docker compose down` | Stop and remove containers and networks |
| `docker compose down -v` | Same, and also delete the volumes (data) |
| `docker compose ps` | List the services and their status |
| `docker compose logs -f <service>` | Follow a service's logs |
| `docker compose build` | Build the images only |
| `docker compose restart <service>` | Restart one service |
| `docker compose exec <service> sh` | Open a shell inside a running service |

### 1-8 Document your docker-compose file.

```yaml
services:
  database:
    build: ./database
    container_name: postgres_container      # hostname used by the backend
    environment:                            # values read from the .env file (not in Git)
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgresvolume:/var/lib/postgresql/data   # data persistence
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:                            # "healthy" only when Postgres accepts connections
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend-api/simpleapi
    container_name: simple-api              # hostname used by the proxy
    networks:
      - app-network
    depends_on:
      database:
        condition: service_healthy          # wait for the database to be ready
    restart: unless-stopped

  httpd:
    build: ./http-server
    container_name: http_server
    ports:
      - "80:80"                             # only exposed service
    networks:
      - app-network
    depends_on:
      - backend
    restart: unless-stopped

networks:
  app-network:

volumes:
  postgresvolume:
```

Key choices:

- **Process segregation:** one service per container (database, API, proxy).
- **Security:** only the proxy publishes a port; the backend and database are reachable only inside `app-network`. Credentials come from a git-ignored `.env` file.
- **Reliability:** healthcheck + `depends_on: service_healthy` start the API only once the database is ready; `restart: unless-stopped` restarts services after a crash or a reboot.
- **Persistence:** a named volume keeps the database data.

### 1-9 Document your publication commands and published images in dockerhub.

```bash
docker login

# Tag with the Docker Hub username and a version
docker tag tp_dockers_1-database iliesn/tp-database:1.0
docker tag tp_dockers_1-backend  iliesn/tp-backend:1.0
docker tag tp_dockers_1-httpd    iliesn/tp-httpd:1.0

# Push
docker push iliesn/tp-database:1.0
docker push iliesn/tp-backend:1.0
docker push iliesn/tp-httpd:1.0
```

(The local image names generated by compose can be checked with `docker image ls`. A `latest` tag is pushed the same way.)

Published images on Docker Hub (`https://hub.docker.com/u/iliesn`):

| Image | Content |
|---|---|
| `iliesn/tp-database` | PostgreSQL 17.2 (alpine) + schema and initial data |
| `iliesn/tp-backend` | Spring Boot simple-api (Java 21 JRE) |
| `iliesn/tp-httpd` | Apache httpd 2.4 reverse proxy to the API |

### 1-10 Why do we put our images into an online repo?

So coworkers, CI/CD pipelines and servers can pull and run them anywhere without rebuilding. Versioned tags also make deployments traceable and easy to roll back.
