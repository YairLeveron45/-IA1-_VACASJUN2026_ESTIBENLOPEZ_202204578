FROM node:20-slim

WORKDIR /workspace/FRONTEND

COPY FRONTEND/package*.json ./
RUN npm ci

COPY FRONTEND ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
