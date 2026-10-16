### 2-1 What are testcontainers?

Java libraries that start real Docker containers during tests. Here, a temporary PostgreSQL container is started so the integration tests run against a real, disposable database, then it's removed.

### 2-2 For what purpose do we need to use secured variables?

To use credentials in the pipeline without writing them in the code, to prevent any leaks/security breaches.

### 2-3 Why did we put `needs: test-backend` on this job?

Jobs run in parallel by default. `needs` makes the image build wait for the tests and run only if they succeed, so broken code is never built or published.

### 2-4 For what purpose do we need to push docker images?

To store the tested images in a registry (Docker Hub) so they can be pulled and run anywhere (teammates, servers, deployment) without rebuilding them.