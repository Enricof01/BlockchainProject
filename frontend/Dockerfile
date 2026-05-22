FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

# Startet den Vite Entwicklungs-Server
CMD ["npm", "run", "dev", "--", "--host"]