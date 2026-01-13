
# Dockerfile para Vue. PARA CUANDO SEA PRODUCCION DEFINITIVA
FROM node:20

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar todo el código
COPY . .

# Construir la app para producción
RUN npm run build

# Servir la app con un servidor estático (Nginx)
FROM nginx:stable-alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


# Dockerfile.dev para Vue con recarga automática
# FROM node:20

# WORKDIR /app

# # Copiar package.json y package-lock.json
# COPY package*.json ./

# # Instalar dependencias
# RUN npm install

# # Copiar todo el código
# COPY . .

# # Exponer el puerto de Vite o Vue CLI
# EXPOSE 8080

# # Servidor de desarrollo
# # CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0"]
# # CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--watch-options-poll=1000"]
# CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0"]


