# ── Stage 1: build ────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Declare build-time args (forwarded from docker-compose build args)
ARG VITE_CONTENTPILOT_URL
ARG VITE_CONTENTPILOT_NAME
ARG VITE_PRODUCT_NAME
ARG VITE_PRODUCT_DOMAIN
ARG VITE_IMPRESSUM_URL
ARG VITE_DATENSCHUTZ_URL
ARG VITE_AGB_URL
ARG VITE_CONTACT_URL
ARG VITE_SUPPORT_EMAIL

# Expose as ENV so Vite picks them up during build
ENV VITE_CONTENTPILOT_URL=$VITE_CONTENTPILOT_URL
ENV VITE_CONTENTPILOT_NAME=$VITE_CONTENTPILOT_NAME
ENV VITE_PRODUCT_NAME=$VITE_PRODUCT_NAME
ENV VITE_PRODUCT_DOMAIN=$VITE_PRODUCT_DOMAIN
ENV VITE_IMPRESSUM_URL=$VITE_IMPRESSUM_URL
ENV VITE_DATENSCHUTZ_URL=$VITE_DATENSCHUTZ_URL
ENV VITE_AGB_URL=$VITE_AGB_URL
ENV VITE_CONTACT_URL=$VITE_CONTACT_URL
ENV VITE_SUPPORT_EMAIL=$VITE_SUPPORT_EMAIL

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# ── Stage 2: serve ────────────────────────────────────────────
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx/docker-internal.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
