# Deployment Guide

This guide provides step-by-step instructions to deploy the project in Window 10/11 operating system.

## Prerequisites

### 1. Install Python with necessary libraries

Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/).

Verify installation:
```bash
python --version
```

In terminal run the following command:
```bash
pip install bcrypt cryptography PyMySQL python-dotenv
```

### 2. Install Docker Desktop

Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).

Verify installation:
```bash
docker --version
docker-compose --version
```

## Configuration

### 3. Create Environment Files

Create three `.env` files with the following content:

#### 3.1 Project Root `.env`

Create `.env` in the project root directory:

```env
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=ComputingU
DB_CHARSET=utf8mb4

# Data Encryption Key (Required)
DATA_ENCRYPTION_KEY=my_secret_encryption_key_12345678901234567890123456789012

# Optional Settings
USE_DB_SESSIONS=false
RSA_KEY_ID=default
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

#### 3.2 Backend `.env`

Create `backend/.env` with the same content as above:

```env
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=ComputingU
DB_CHARSET=utf8mb4

# Data Encryption Key (Required)
DATA_ENCRYPTION_KEY=my_secret_encryption_key_12345678901234567890123456789012

# Optional Settings
USE_DB_SESSIONS=false
RSA_KEY_ID=default
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

#### 3.3 Percona Compose `.env`

Create `percona-compose/.env`:

```env
# MySQL Root Password
MYSQL_ROOT_PASSWORD=supersecurepassword

# Database Configuration
MYSQL_DATABASE=ComputingU
MYSQL_USER=app_user
MYSQL_PASSWORD=app_user_password
```

#### 3.4 Set encryption key for AES encryption/decryption

In docker-compose.yml, in line 36 add the line
```sql
SET @encryption_key = 'c29a02b23662ced73f8c007c877a85c8aab576b1b7f888ac37c364b5a75a681b';
```

## Database Setup

### 4. Start Docker Container

Open a terminal and navigate to the `percona-compose` directory:

```bash
cd percona-compose
docker-compose up -d
```

Wait for the container to start. Verify it's running:

```bash
docker ps
```

### 5. Initialize Database

Connect to MySQL:

```bash
docker exec -it percona-server mysql -u root -p
```

When prompted, enter the password: `supersecurepassword`

### 6. Verify Database Setup

In the MySQL prompt, verify tables were created:

```sql
USE ComputingU;
SHOW TABLES;
```

You should see tables like `students`, `guardians`, `staffs`, `courses`, `grades`, `disciplinary_records`, `accountLog`, `dataUpdateLog`, `audit_log`, and `sessions`.

Exit MySQL:
```sql
EXIT;
```

### 7. Execute Database Script (If necessary)

If the database fail to show the table.

Copy and paste the entire content of `database_init_sql/University.sql` into the MySQL prompt, then press Enter.

Alternatively, you can execute it directly:

```bash
docker exec -i percona-server mysql -u root -p supersecurepassword < ../database_init_sql/University.sql
```

## Backend Setup

### 8. Setting up the certificate for the application

Open PowerShell as Administrator, Press Win + X, choose Windows PowerShell (Admin).

Install Chocolatey (one-time setup)
```bash
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Install mkcert via Chocolatey
```bash
choco install mkcert
```

Trust mkcert’s local CA
```bash
mkcert -install
```

Open a new terminal and change to the folder \security,generate development certificates
```bash
mkcert -cert-file localhost-cert.pem -key-file localhost-key.pem localhost 127.0.0.1 ::1
```

replace the cert.pem and key.pem with the content in localhost-cert.pem and localhost-key.pem correspondingly

### 9. Install Python Dependencies

Open a new terminal and navigate to the project root:

```bash
cd <project-root>
pip install -r requirements.txt
```

### 10. Start Backend Server

Navigate to the backend directory and run:

```bash
cd backend
python main.py
```

The server will start on `http://127.0.0.1:8000`.

## Frontend Access

### 11. Open Frontend

Open `frontend/index.html` in your web browser.

You can:
- Double-click the file to open it in your default browser
- Or manually navigate to the file location and open it

## Test Users

Use these credentials to test the system:

- **Student**: `test_student@example.com` / `StudentTest123`
- **Guardian**: `test_guardian@example.com` / `GuardianTest123`
- **Staff**: `test_staff@example.com` / `StaffTest123`

## Troubleshooting

- **Database connection error**: Ensure Docker container is running (`docker ps`)
- **Port 3306 already in use**: Stop other MySQL instances or change the port in `docker-compose.yml`
- **Encryption key error**: Ensure `.env` files exist with `DATA_ENCRYPTION_KEY` set
- **Module not found**: Run `pip install -r requirements.txt` again

## Stopping the System

To stop the Docker container:

```bash
cd percona-compose
docker-compose down
```

To stop the backend server, press `Ctrl+C` in the terminal running `main.py`.


