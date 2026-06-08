# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ─────────────────────────────────────────────────
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy SPA nginx config (no SSL here – SSL terminates at host Nginx)
COPY nginx/docker-internal.conf /etc/nginx/conf.d/default.conf

EXPOSE 3010

CMD ["nginx", "-g", "daemon off;"]
