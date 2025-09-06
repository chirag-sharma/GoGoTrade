# 🔒 Security Configuration

## Environment Variables Setup

### 1. Copy the template file:
```bash
cp .env.template .env
```

### 2. Update .env with secure values:
- Generate a secure database password (use a password manager)
- Replace `your_secure_password_here` with your actual password
- Generate secure JWT secrets using: `openssl rand -hex 32`

### 3. Never commit .env files:
- The .env file is in .gitignore
- Only commit .env.template (without real passwords)
- Share passwords securely via encrypted channels

## Database Password Security

### Development:
```bash
# Use a secure but memorable password for local development
POSTGRES_PASSWORD=Dev_SecurePass123!
```

### Production:
```bash
# Use a strong, randomly generated password
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

## Environment Separation

### Development (.env):
```
ENVIRONMENT=development
POSTGRES_PASSWORD=your_dev_password
```

### Production (.env.production):
```
ENVIRONMENT=production
POSTGRES_PASSWORD=your_production_password
SECRET_KEY=production_secret_key
```

## Security Best Practices

1. **Never hardcode passwords** in docker-compose.yml
2. **Use environment variables** for all sensitive data
3. **Rotate passwords regularly** in production
4. **Use strong passwords** (minimum 16 characters)
5. **Keep .env files local** (never commit to Git)
6. **Use different passwords** for each environment
