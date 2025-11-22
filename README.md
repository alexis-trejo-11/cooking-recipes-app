# Cooking Recipe Platform

A modern, full-stack web application for sharing and discovering cooking recipes. Built with FastAPI (backend) and Angular (frontend), this platform combines enterprise-grade architecture with an intuitive user experience.

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Angular-DD0031.svg)](https://angular.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Cooking Recipe Platform is a comprehensive full-stack application that enables users to create, share, discover, and organize cooking recipes. With a focus on user experience, performance, and maintainability, the platform implements modern development practices including Clean Architecture, Domain-Driven Design, and responsive UI design.

### What Makes This Platform Special

- **Production-Ready Architecture**: Built with enterprise patterns and best practices
- **Secure Authentication**: JWT-based authentication with refresh token rotation
- **Rich Recipe Management**: Comprehensive recipe creation with ingredients, steps, nutritional info, and media
- **Social Features**: User reviews, ratings, favorites, and recipe sharing
- **Advanced Search**: Multi-criteria filtering with pagination and sorting
- **Responsive Design**: Mobile-first approach with modern UI/UX
- **Type-Safe**: End-to-end type safety with Python type hints and TypeScript
- **Real-Time Updates**: Reactive state management with Angular signals
- **Performance Optimized**: Redis caching, database indexing, lazy loading, and CDN-ready

## ✨ Key Features

### Recipe Management

- **Create & Edit Recipes**: Rich recipe editor with ingredients, preparation steps, cooking times, and nutritional information
- **Recipe Discovery**: Browse featured recipes, search by multiple criteria (cuisine, difficulty, ingredients, tags)
- **Recipe Details**: Comprehensive recipe view with step-by-step instructions, ingredient lists, and cooking tips
- **Recipe Versions**: Track recipe modifications with version control
- **Soft Deletion**: Recipes can be deleted and restored without data loss

### User Features

- **User Authentication**: Secure signup and login with email verification
- **User Profiles**: Customizable profiles with bio, profile picture, and preferences
- **Personal Collections**: Manage your own recipes, favorites, and recipe history
- **Recipe Reviews**: Rate and comment on recipes with 5-star rating system
- **Favorite System**: Save recipes for quick access later

### Social & Community

- **User Reviews**: Share feedback and experiences with the community
- **Recipe Ratings**: See average ratings and total review counts
- **Author Profiles**: View recipes by specific authors
- **Recipe Analytics**: Track recipe views and popularity

### Search & Discovery

- **Advanced Filtering**: Filter by cuisine, difficulty, meal type, cooking time, rating, and ingredients
- **Full-Text Search**: Search recipes by name and description
- **Pagination**: Efficient browsing with configurable page sizes
- **Sorting Options**: Sort by date, rating, popularity, or cooking time

### Security & Performance

- **JWT Authentication**: Secure token-based authentication with refresh mechanism
- **Rate Limiting**: Protect API from abuse with Redis-based rate limiting
- **CORS Configuration**: Secure cross-origin resource sharing
- **Input Validation**: Comprehensive validation on both frontend and backend
- **SQL Injection Protection**: Parameterized queries and ORM usage
- **XSS Prevention**: Content sanitization and CSP headers

## 🛠️ Technology Stack

### Backend (FastAPI)

#### Core Framework

- **[FastAPI 0.104.1](https://fastapi.tiangolo.com/)** - Modern, high-performance web framework
- **[Uvicorn 0.24.0](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[Python 3.11+](https://www.python.org/)** - Latest Python features

#### Database & ORM

- **[SQLAlchemy 2.0.23](https://www.sqlalchemy.org/)** - Powerful async ORM
- **[Alembic 1.12.1](https://alembic.sqlalchemy.org/)** - Database migration management
- **[aiosqlite 0.19.0](https://aiosqlite.omnilib.dev/)** / **PostgreSQL** - Database engines

#### Validation & Security

- **[Pydantic 2.5.0](https://docs.pydantic.dev/)** - Data validation using Python type hints
- **[PyJWT 2.8.0](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation
- **[bcrypt 4.1.2](https://github.com/pyca/bcrypt/)** - Password hashing

#### Caching & Performance

- **[Redis 5.0.1](https://redis.io/)** - In-memory caching and rate limiting
- **[aioredis 2.0.1](https://aioredis.readthedocs.io/)** - Async Redis client

#### Testing

- **[pytest 7.4.3](https://pytest.org/)** - Testing framework
- **[pytest-asyncio 0.21.1](https://pytest-asyncio.readthedocs.io/)** - Async test support

### Frontend (Angular)

#### Core Framework

- **[Angular 20.3.9](https://angular.io/)** - Modern web application framework
- **[TypeScript 5.0+](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[RxJS](https://rxjs.dev/)** - Reactive programming library

#### UI & Styling

- **[SCSS](https://sass-lang.com/)** - Advanced CSS preprocessor
- **Responsive Design** - Mobile-first approach
- **CSS Grid & Flexbox** - Modern layout techniques

#### State Management

- **[Angular Signals](https://angular.io/guide/signals)** - Reactive state management
- **Services** - Centralized state and business logic

#### HTTP & API

- **[HttpClient](https://angular.io/api/common/http/HttpClient)** - Angular HTTP module
- **Interceptors** - Request/response transformation and error handling

#### Routing & Guards

- **[Angular Router](https://angular.io/guide/router)** - Client-side routing
- **Route Guards** - Authentication and authorization protection

## 📁 Project Structure

```
cooking_receipt_web_app/
│
├── recipe-back-end/              # FastAPI Backend
│   ├── alembic/                  # Database migrations
│   │   ├── versions/             # Migration scripts
│   │   └── env.py                # Migration environment
│   │
│   ├── app/                      # Main application package
│   │   ├── config/               # Configuration modules
│   │   │   ├── app_settings.py   # Application settings
│   │   │   ├── sql_session.py    # Database configuration
│   │   │   ├── redis_config.py   # Redis configuration
│   │   │   └── rate_limiter.py   # Rate limiting setup
│   │   │
│   │   ├── modules/              # Feature modules (DDD bounded contexts)
│   │   │   ├── auth/             # Authentication & User Management
│   │   │   │   ├── domain/       # Business logic layer
│   │   │   │   ├── application/  # Use cases layer
│   │   │   │   ├── infrastructure/ # Technical implementation
│   │   │   │   └── presentation/ # HTTP/API layer
│   │   │   │
│   │   │   └── recipe/           # Recipe Management
│   │   │       ├── domain/       # Business logic layer
│   │   │       ├── application/  # Use cases layer
│   │   │       ├── infrastructure/ # Technical implementation
│   │   │       └── presentation/ # HTTP/API layer
│   │   │
│   │   └── utils/                # Shared utilities
│   │
│   ├── tests/                    # Test suite
│   │   ├── unit/                 # Unit tests
│   │   ├── application/          # Use case tests
│   │   ├── infrastructure/       # Repository tests
│   │   └── controller/           # Integration tests
│   │
│   ├── docs/                     # Documentation
│   │   ├── API_ENDPOINTS.md      # Complete API reference
│   │   ├── ARCHITECTURE.md       # Architecture deep dive
│   │   ├── DATABASE_SCHEMA.md    # Database documentation
│   │   └── DEPLOYMENT.md         # Deployment guide
│   │
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   ├── docker-compose.yml        # Multi-container setup
│   └── README.md                 # Backend documentation
│
├── recipe-front-end/             # Angular Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/       # UI components
│   │   │   │   ├── pages/        # Page components
│   │   │   │   │   ├── auth/     # Authentication pages
│   │   │   │   │   ├── home/     # Homepage
│   │   │   │   │   ├── recipe/   # Recipe pages
│   │   │   │   │   │   ├── recipe-detail/
│   │   │   │   │   │   └── recipes/
│   │   │   │   │   └── user/     # User pages
│   │   │   │   │       ├── dashboard/
│   │   │   │   │       ├── profile/
│   │   │   │   │       ├── my-recipes/
│   │   │   │   │       ├── my-favorites/
│   │   │   │   │       ├── create-recipe/
│   │   │   │   │       └── edit-recipe/
│   │   │   │   │
│   │   │   │   └── shared/       # Shared components
│   │   │   │       ├── header/
│   │   │   │       ├── footer/
│   │   │   │       ├── recipe-card/
│   │   │   │       ├── recipe-grid/
│   │   │   │       ├── recipe-form/
│   │   │   │       └── search-bar/
│   │   │   │
│   │   │   ├── services/         # Angular services
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── recipe.service.ts
│   │   │   │   ├── review.services.ts
│   │   │   │   └── user.service.ts
│   │   │   │
│   │   │   ├── guards/           # Route guards
│   │   │   │   ├── auth.guard.ts
│   │   │   │   └── public.guard.ts
│   │   │   │
│   │   │   ├── interceptors/     # HTTP interceptors
│   │   │   │   ├── auth.interceptor.ts
│   │   │   │   ├── case.interceptor.ts
│   │   │   │   └── rate-limiter.interceptor.ts
│   │   │   │
│   │   │   ├── models/           # TypeScript models
│   │   │   │   ├── auth_models.ts
│   │   │   │   ├── recipe_models.ts
│   │   │   │   ├── review_models.ts
│   │   │   │   └── user_models.ts
│   │   │   │
│   │   │   ├── app.config.ts     # App configuration
│   │   │   ├── app.routes.ts     # Routing configuration
│   │   │   └── app.ts            # Root component
│   │   │
│   │   ├── environments/         # Environment configs
│   │   ├── index.html            # HTML entry point
│   │   ├── main.ts               # Application bootstrap
│   │   └── styles.scss           # Global styles
│   │
│   ├── angular.json              # Angular CLI configuration
│   ├── package.json              # Node dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   └── README.md                 # Frontend documentation
│
└── README.md                     # This file (project overview)
```

## 🚀 Getting Started

### Prerequisites

#### Backend Requirements

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)
- Redis (optional, for rate limiting and caching)

#### Frontend Requirements

- Node.js 18.x or higher
- npm or yarn package manager
- Angular CLI 20.x

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/alexisTrejo11/cooking_receipt_web_app.git
cd cooking_receipt_web_app
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd recipe-back-end

# Create virtual environment
python -m venv env

# Activate virtual environment
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
python main.py
```

The API will be available at:

- **HTTP**: `http://localhost:8080`
- **API Docs**: `http://localhost:8080/docs`
- **Alternative Docs**: `http://localhost:8080/redoc`

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd recipe-front-end

# Install dependencies
npm install

# Start development server
ng serve
```

The application will be available at:

- **URL**: `http://localhost:4200`

#### 4. Docker Setup (Alternative)

```bash
# From backend directory
cd recipe-back-end

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

#### Backend (.env)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./cooking_app.db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRES_DAYS=90

# Application
DEBUG=True

# Rate Limiting
RATE_LIMIT_ENABLED=True

# Server Ports
SERVER_PORT=8080
SSL_PORT=8443
```

#### Frontend (environment.ts)

```typescript
export const environment = {
  production: false,
  apiUrl: "http://localhost:8080",
  apiVersion: "v1",
};
```

## 🏛️ Architecture

### Backend Architecture (Clean Architecture + DDD)

The backend follows **Clean Architecture** principles combined with **Domain-Driven Design** to create a maintainable, testable, and scalable system.

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  FastAPI Controllers, Request/Response Models, Middleware    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Application Layer                          │
│  Use Cases, Application Services, DTOs, Workflows           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     Domain Layer                             │
│  Entities, Value Objects, Domain Services, Business Rules   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Infrastructure Layer                         │
│  Repositories, External Services, Database, Redis           │
└─────────────────────────────────────────────────────────────┘
```

#### Key Patterns

- **Repository Pattern**: Abstract data access
- **Specification Pattern**: Encapsulate query logic
- **Use Case Pattern**: Single-responsibility business operations
- **Value Objects**: Immutable, self-validating objects
- **Factory Pattern**: Complex object creation
- **Dependency Injection**: Invert dependencies

### Frontend Architecture (Angular Component-Based)

The frontend uses Angular's modern component-based architecture with reactive state management.

```
┌─────────────────────────────────────────────────────────────┐
│                      Components                              │
│  Pages, Shared Components, UI Elements                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      Services                                │
│  Business Logic, State Management, API Communication        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   HTTP Interceptors                          │
│  Authentication, Error Handling, Request Transformation     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      API Layer                               │
│  HTTP Requests to FastAPI Backend                           │
└─────────────────────────────────────────────────────────────┘
```

#### Key Features

- **Signal-based State**: Reactive state management with Angular Signals
- **Route Guards**: Authentication and authorization
- **Lazy Loading**: Module-based code splitting
- **Interceptors**: Request/response transformation
- **Type Safety**: End-to-end TypeScript typing

## 📚 Documentation

### Backend Documentation

- **[API Endpoints](recipe-back-end/docs/API_ENDPOINTS.md)** - Complete API reference with request/response examples
- **[Architecture Guide](recipe-back-end/docs/ARCHITECTURE.md)** - Deep dive into Clean Architecture and DDD implementation
- **[Database Schema](recipe-back-end/docs/DATABASE_SCHEMA.md)** - Detailed database structure and relationships
- **[Deployment Guide](recipe-back-end/docs/DEPLOYMENT.md)** - Production deployment instructions

### Frontend Documentation

- **[Frontend README](recipe-front-end/README.md)** - Angular application setup and development

## 🧪 Testing

### Backend Testing

```bash
# Navigate to backend directory
cd recipe-back-end

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_domain.py

# Run with verbose output
pytest -v
```

**Test Coverage:**

- Unit Tests: Domain entities and value objects
- Application Tests: Use case logic
- Infrastructure Tests: Repository implementations
- Integration Tests: API endpoints

### Frontend Testing

```bash
# Navigate to frontend directory
cd recipe-front-end

# Run unit tests
ng test

# Run e2e tests
ng e2e

# Run with coverage
ng test --code-coverage
```

## 🚢 Deployment

### Production Deployment

#### Docker Deployment (Recommended)

```bash
# Build and deploy with Docker Compose
cd recipe-back-end
docker-compose -f docker-compose.prod.yml up -d
```

#### Cloud Platforms

- **AWS**: Elastic Beanstalk, ECS, Lambda
- **Google Cloud**: Cloud Run, App Engine, GKE
- **Azure**: App Service, Container Instances
- **Heroku**: Simple deployment with Procfile

For detailed deployment instructions, see the [Deployment Guide](recipe-back-end/docs/DEPLOYMENT.md).

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

#### Backend

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for classes and methods
- Maintain test coverage above 85%
- Follow Clean Architecture principles

#### Frontend

- Follow Angular style guide
- Use TypeScript strict mode
- Write unit tests for components and services
- Follow component-based architecture
- Use reactive programming patterns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Alexis Trejo** - [@alexisTrejo11](https://github.com/alexisTrejo11)

## 🙏 Acknowledgments

- FastAPI community for excellent documentation
- Angular team for the powerful framework
- SQLAlchemy team for the robust ORM
- All contributors and users of this project

## 📞 Support

For support, email marcoalexispt.02@gmail.com or open an issue on GitHub.

---

**Built with passion using FastAPI, Angular, and modern development practices**
