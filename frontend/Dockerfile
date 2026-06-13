FROM node:20-slim

# Enable corepack and activate pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Expose default next.js port
EXPOSE 3000

# Persistent tail command to keep the container running for development
CMD ["tail", "-f", "/dev/null"]
