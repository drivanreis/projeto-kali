FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código-fonte
COPY . .

# Copiar arquivo de configuração do TypeScript se houver
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY .eslintrc.json ./
COPY tailwind.config.cjs postcss.config.cjs ./

# Expor porta 5190
EXPOSE 5190

# Inicializar Vite em modo desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5190"]
