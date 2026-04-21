# Docker DOQL Example - Infrastructure Summary

## Overview

This example demonstrates a comprehensive Docker-based infrastructure simulation mapped to DOQL's `app.doql.less` format. The infrastructure represents a typical multi-tier distributed system with load balancing, application servers, databases, caching, message queues, monitoring, logging, and **multi-language microservices** for AI entity detection testing.

## Infrastructure Components

### Hardware Layer (15 Components)

| Component | Type | Image | CPU Limit | Memory Limit | Ports | Networks |
|-----------|------|-------|-----------|--------------|-------|----------|
| load-balancer | Load Balancer | nginx:alpine | 0.5 cores | 512M | 8880, 8443 | frontend, backend |
| app-server-1 | Application Server | python:3.12-slim | 1.0 cores | 1G | 8001 | backend, database |
| app-server-2 | Application Server | python:3.12-slim | 1.0 cores | 1G | 8002 | backend, database |
| database | Database Server | postgres:15-alpine | 2.0 cores | 2G | 5432 | database |
| cache | Cache Server | redis:7-alpine | 0.5 cores | 512M | 6379 | database |
| message-queue | Message Broker | rabbitmq:3-management-alpine | 1.0 cores | 1G | 5672, 15672 | backend |
| worker | Worker Node | python:3.12-slim | 0.5 cores | 512M | - | backend, database |
| monitoring | Monitoring Server | prom/prometheus:latest | 0.5 cores | 512M | 9090 | frontend, backend |
| logging | Log Aggregator | fluent/fluent-bit:latest | 0.25 cores | 256M | 24224 | backend |
| go-service | Application Server | golang:1.21-alpine | 0.5 cores | 512M | 8081 | backend, database |
| rust-service | Application Server | rust:1.75-slim | 0.5 cores | 512M | 8082 | backend, database |
| java-service | Application Server | openjdk:21-jdk-slim | 1.0 cores | 1G | 8083 | backend, database |
| node-service | Application Server | node:20-alpine | 0.5 cores | 512M | 8084 | backend, database |
| ruby-service | Application Server | ruby:3.2-alpine | 0.5 cores | 512M | 8085 | backend, database |
| php-service | Application Server | php:8.2-apache | 0.5 cores | 512M | 8086 | backend, database |

**Total Resource Allocation:**
- CPU: 10.75 cores
- Memory: 10.75 GB

### Software Services Layer (14 Services)

1. **web-api** (REST API)
   - Runtime: Python 3.12
   - Endpoints: `/health` (GET), `/api` (GET)
   - Instances: app-server-1, app-server-2

2. **database-service** (Relational Database)
   - Engine: PostgreSQL 15
   - Instance: database
   - Databases: appdb

3. **cache-service** (Key-Value Store)
   - Engine: Redis 7
   - Instance: cache

4. **message-service** (Message Queue)
   - Engine: RabbitMQ 3
   - Instance: message-queue
   - Queues: task_queue

5. **worker-service** (Background Worker)
   - Runtime: Python 3.12
   - Instance: worker
   - Processes: message-processing

6. **monitoring-service** (Metrics Server)
   - Engine: Prometheus
   - Instance: monitoring
   - Scrape Interval: 15s

7. **logging-service** (Log Shipper)
   - Engine: Fluent Bit
   - Instance: logging
   - Input: tail
   - Output: stdout

8. **go-api** (REST API - Go)
   - Runtime: Go 1.21
   - Endpoints: `/health` (GET), `/api` (GET)
   - Instance: go-service
   - Features: static-typing, compiled, garbage-collected

9. **rust-api** (REST API - Rust)
   - Runtime: Rust 1.75
   - Endpoints: `/health` (GET), `/api` (GET)
   - Instance: rust-service
   - Features: static-typing, compiled, memory-safe, zero-cost-abstractions

10. **java-api** (REST API - Java)
    - Runtime: Java 21
    - Endpoints: `/health` (GET), `/api` (GET)
    - Instance: java-service
    - Features: static-typing, compiled, garbage-collected, object-oriented

11. **node-api** (REST API - Node.js)
    - Runtime: JavaScript (Node 20)
    - Endpoints: `/health` (GET), `/api` (GET)
    - Instance: node-service
    - Features: dynamic-typing, event-driven, asynchronous

12. **ruby-api** (REST API - Ruby)
    - Runtime: Ruby 3.2
    - Endpoints: `/health` (GET), `/api` (GET)
    - Instance: ruby-service
    - Features: dynamic-typing, object-oriented, metaprogramming

13. **php-api** (REST API - PHP)
    - Runtime: PHP 8.2
    - Endpoints: `/health` (GET), `/api` (GET)
    - Instance: php-service
    - Features: dynamic-typing, server-side-scripting, web-focused

### Network Topology (3 Networks)

| Network | Type | Driver | Services | Exposure |
|---------|------|--------|----------|----------|
| frontend | Public | bridge | load-balancer, monitoring | External |
| backend | Private | bridge | load-balancer, app-server-1, app-server-2, message-queue, worker, monitoring, logging, go-service, rust-service, java-service, node-service, ruby-service, php-service | Internal |
| database | Isolated | bridge | app-server-1, app-server-2, database, cache, worker, go-service, rust-service, java-service, node-service, ruby-service, php-service | Restricted |

### Storage Volumes (3 Volumes)

| Volume | Type | Driver | Service | Mount Path |
|--------|------|--------|---------|------------|
| db-data | Persistent | local | database | /var/lib/postgresql/data |
| cache-data | Persistent | local | cache | /data |
| prometheus-data | Persistent | local | monitoring | /prometheus |

### Interfaces (8 Interfaces)

| Type | Port | Protocol | Service |
|------|------|----------|---------|
| http | 8880 | HTTP | load-balancer |
| https | 8443 | HTTPS | load-balancer |
| postgresql | 5432 | PostgreSQL | database |
| redis | 6379 | Redis | cache |
| amqp | 5672 | AMQP | message-queue |
| management | 15672 | HTTP | message-queue |
| prometheus | 9090 | HTTP | monitoring |
| fluent-bit | 24224 | TCP | logging |

### Workflows (8 Workflows)

1. **deploy** (manual)
   - Step 1: `docker compose up -d`
   - Step 2: `docker compose ps`
   - Step 3: `docker compose logs --tail=50`

2. **health-check** (scheduled, every 5 minutes)
   - Step 1: `docker compose ps`
   - Step 2: `docker compose exec app-server-1 curl http://localhost:8000/health`
   - Step 3: `docker compose exec database pg_isready -U appuser`

3. **scale-up** (manual)
   - Step 1: `docker compose up -d --scale app-server-1=3`

4. **scale-down** (manual)
   - Step 1: `docker compose up -d --scale app-server-1=1`

5. **backup-db** (scheduled, daily at 2 AM)
   - Step 1: `docker compose exec database pg_dump -U appuser appdb > backup.sql`

6. **logs** (manual)
   - Step 1: `docker compose logs --tail=100`

7. **stop** (manual)
   - Step 1: `docker compose down`

8. **restart** (manual)
   - Step 1: `docker compose restart`

### Deployment Configuration

- **Target**: docker-compose
- **Orchestrator**: docker-compose
- **Strategy**: rolling-update

### Environments

1. **production**
   - Runtime: docker
   - Orchestrator: docker-compose
   - Networks: frontend, backend, database

2. **development**
   - Runtime: docker
   - Orchestrator: docker-compose
   - Networks: backend, database

## DOQL Format Structure

The generated `app.doql.less` file demonstrates the following DOQL concepts:

1. **Application Metadata**: name, version, type
2. **Hardware Declaration**: type, image, container, ports, CPU/memory limits, networks, role
3. **Service Declaration**: type, runtime/engine, version, instances/endpoints
4. **Network Topology**: type, driver, services, exposure level
5. **Storage Volumes**: type, driver, service, mount path
6. **Workflows**: trigger type (manual/scheduled), steps with commands
7. **Interfaces**: type, port, protocol, service
8. **Deployment**: target, orchestrator, strategy
9. **Environments**: runtime, orchestrator, networks

## Key Features Demonstrated

1. **Hardware Abstraction**: Physical/virtual resources mapped to containers with resource limits
2. **Service Discovery**: Clear mapping between hardware and software services
3. **Network Segmentation**: Three-tier network architecture (public, private, isolated)
4. **Data Persistence**: Persistent volumes for database, cache, and monitoring data
5. **Operational Workflows**: Automated deployment, health checking, scaling, backup, and maintenance
6. **Multi-Environment Support**: Production and development environment configurations
7. **Interface Documentation**: All external and internal service interfaces documented
8. **Multi-Language Support**: Services in 7 different programming languages (Python, Go, Rust, Java, Node.js, Ruby, PHP) for AI entity detection testing
9. **Language-Specific Features**: Each service demonstrates language-specific paradigms (static vs dynamic typing, compiled vs interpreted, etc.)
10. **AI Entity Detection Testbed**: Comprehensive infrastructure for testing AI code analysis and entity detection across multiple languages

## Usage

To run this example:

```bash
cd examples/docker-doql-example
./run-doql.sh
```

To view the generated DOQL file:

```bash
cat app.doql.less
```

To stop the infrastructure:

```bash
docker compose down
```

## Architecture Diagram

```
Internet
   |
   v
[Frontend Network]
   |
   +-- Load Balancer (nginx:8880)
   |      |
   |      v
   +-- Monitoring (Prometheus:9090)
          |
          v
[Backend Network]
   |
   +-- App Server 1 (Python:8001)
   +-- App Server 2 (Python:8002)
   +-- Go Service (Go:8081)          [static-typing, compiled]
   +-- Rust Service (Rust:8082)       [memory-safe, zero-cost]
   +-- Java Service (Java:8083)       [garbage-collected, OOP]
   +-- Node Service (Node:8084)      [event-driven, async]
   +-- Ruby Service (Ruby:8085)      [metaprogramming, dynamic]
   +-- PHP Service (PHP:8086)        [web-focused, server-side]
   |      |
   |      +-- Message Queue (RabbitMQ:5672)
   |      |      |
   |      |      v
   |      +-- Worker (Python)
   |      |
   |      +-- Logging (Fluent Bit:24224)
   |
   v
[Database Network - Isolated]
   |
   +-- Database (PostgreSQL:5432)
   |      |
   +-- Cache (Redis:6379)
```

## Summary

This DOQL example provides a comprehensive mapping of a realistic Docker-based microservices infrastructure, demonstrating how DOQL's `app.doql.less` format can capture:
- Hardware resource allocation and constraints
- Software service topology and dependencies
- Network segmentation and security zones
- Storage management and persistence
- Operational automation through workflows
- Multi-environment deployment strategies

The format is designed to be both human-readable and machine-parsable, enabling infrastructure-as-code practices and automated infrastructure analysis.
