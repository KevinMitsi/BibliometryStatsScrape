FROM node:14 AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build --prod

FROM nginx:alpine
COPY --from=builder /app/dist/bibliometry_view /usr/share/nginx/html
EXPOSE 4200
CMD ["nginx", "-g", "daemon off;"]