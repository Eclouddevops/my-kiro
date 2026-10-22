# syntax=docker/dockerfile:1

# ---- Build stage ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# ---- Serve stage ----
# For local dev we serve the built assets with Vite preview; swap for nginx in
# production if desired.
FROM node:20-alpine AS serve
WORKDIR /app
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/vite.config.ts ./
EXPOSE 5173
CMD ["npx", "vite", "preview", "--host", "--port", "5173"]
