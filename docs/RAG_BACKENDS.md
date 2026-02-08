# RAG Backends Design for ai-slop-gate

## Overview

This document describes the architecture of backends for storing and querying vector embeddings in the RAG (Retrieval-Augmented Generation) layer. The main goal is to enable fast semantic search in CI/CD and cloud environments, with optional scalability for enterprise use cases.

## Backend Options

### Redis (Default)

**Role:** Primary backend for embedding index and vector search.

**Advantages:**
- Very fast in-memory search operations
- Supports Redis Vector Search with cosine similarity and HNSW indexing
- Easy to run in Docker Compose
- Ideal for ephemeral environments (CI/CD pipelines)

**Limitations:**
- Weaker persistence; requires snapshotting or AOF (Append-Only File) for long-term storage

**Use Case:** Default choice for CI/CD pipelines and small to medium teams.

### PostgreSQL + pgvector (Optional)

**Role:** Optional backend for enterprise and cloud deployments requiring persistent storage.

**Advantages:**
- Full data persistence
- Integration with managed services: AWS RDS, Azure Database for PostgreSQL, GCP Cloud SQL
- pgvector extension provides native vector search within PostgreSQL
- Centralized index storage supporting multiple workers

**Limitations:**
- Slightly more complex setup for local development
- Slower than Redis for pure in-memory search operations

**Use Case:** Enterprise deployments, large repositories, and scenarios requiring stable index persistence.

## Abstract Interface

The system uses an abstract interface to decouple the backend implementation from the core logic:

```python
class IndexStore:
    def add(self, embedding, metadata): ...
    def query(self, embedding, top_k): ...
```

**Implementations:**
- `IndexStoreRedis` – Redis-based vector search
- `IndexStorePostgres` – PostgreSQL with pgvector
- `IndexStoreMemory` – In-memory index (optional, for local smoke tests)

The engine and provider components interact exclusively through the `IndexStore` interface, without requiring knowledge of the underlying backend.

## Policy Configuration

RAG backends are configured through `policy.yml`. Here's an example:
```yaml
rag:
  enabled: true
  index_backend: redis   # or 'postgres'
  redis_url: redis://localhost:6379
  postgres_url: postgres://user:pass@host:5432/db
  retrieval:
    top_k: 5
  generation:
    temperature: 0.1
    top_p: 0.8
    max_tokens: 512
  strict_mode:
    enabled: true
    output_format: "json"
    schema_name: "RagAnalysisResult"
    reject_on_invalid_json: true
    reject_on_missing_required_fields: true
```

## Implementation Roadmap

### Phase 1: Redis (Default)

- Implement `IndexStoreRedis` using Redis Search/Redis Vector Search
- Run Redis in Docker Compose for local tests and CI environments
- Create smoke tests: small repository indexing, semantic queries, performance validation

### Phase 2: PostgreSQL + pgvector (Optional)

- Implement `IndexStorePostgres` with pgvector extension
- Integrate with AWS RDS and Azure Database for PostgreSQL
- Add tests for persistence and scalability

### Phase 3: Abstraction Refinement

- Establish `IndexStore` as the definitive base interface
- Ensure engine and provider work exclusively through abstraction
- Validate backend switching works seamlessly

## Deployment Scenarios

**CI/CD Pipelines:** Redis runs as an ephemeral container, discarding data after pipeline completion.

**Cloud Deployments (AWS/Azure):** PostgreSQL runs as a managed database service with persistent storage.

**Local Development:** In-memory index provides fallback for smoke tests and rapid iteration.

## Design Principles

- **Redis as Default:** Chosen for simplicity and speed in typical use cases
- **PostgreSQL as Optional:** Available for enterprise scenarios requiring persistence
- **Abstraction-First:** Abstract interface enables straightforward backend switching
- **Policy-Driven Configuration:** Backend selection is controlled declaratively via `policy.yml`