# Hasura CLI

Docker image for running [Hasura cli commands](https://hasura.io/docs/1.0/graphql/manual/hasura-cli/index.html)

# Example
```
steps:
- id: hasura apply metadata
  uses: docker://popperized/hasura-cli:1.0
  args: [hasura, metadata, apply, --endpoint, HASURA_ENDPOINT]
- id: hasura apply migrate
  uses: docker://popperized/hasura-cli:1.0
  args: [hasura, migrate, apply, --endpoint, HASURA_ENDPOINT]
```
