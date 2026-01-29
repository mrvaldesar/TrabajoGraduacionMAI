# Stage 1: Build the Angular app
FROM node:18 as build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist/nlp-frontend /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80

# Default backend URL for local/docker dev if not set
ENV BACKEND_URL=http://backend:8000/api/

# Indica a Nginx que solo sustituya BACKEND_URL, preservando las variables estándar de Nginx como $host
ENV NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template
ENV NGINX_ENVSUBST_FILTER=BACKEND_URL

# Nginx 1.19+ supports auto-envsubst via templates
# Files in /etc/nginx/templates/*.template are processed and output to /etc/nginx/conf.d/
CMD ["nginx", "-g", "daemon off;"]
