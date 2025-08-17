#!/bin/bash
# setup_env.sh

# Generate secure random values
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)

# Create .env file
cat > .env << EOL
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEYS=key1,key2,key3
EOL

# Set permissions
chmod 600 .env

echo "Environment file created successfully with secure random values"
echo "Please update DATABASE_URL and API_KEYS with your actual values"