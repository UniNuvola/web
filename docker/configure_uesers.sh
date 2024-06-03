#!/bin/sh

# enalbe userpass auth and create 2 dummy users
docker exec vault sh -c 'vault login dev-only-token && \
  vault auth enable userpass && \
  vault write auth/userpass/users/alice password=alice policies=defaults && \
  vault write auth/userpass/users/bob password=bob policies=defaults'
