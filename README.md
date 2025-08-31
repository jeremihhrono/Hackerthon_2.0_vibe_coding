# Community Health System - Kenya

## Overview

A comprehensive digital health platform designed to support Kenya's community health system. The application manages patient records, facilitates community outreach programs, processes payments through IntaSend M-Pesa integration, and provides role-based access for Community Health Workers (CHWs), doctors, and administrators. Built with Flask and SQLAlchemy, the system emphasizes FHIR-compliant patient data management and healthcare service delivery across Kenya's counties.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **CSS Framework**: Bootstrap 5 with custom CSS variables for Kenya-themed styling
- **JavaScript**: Vanilla JavaScript with modular components for payments, forms, and UI interactions
- **Icons**: Font Awesome for consistent iconography
- **Responsive Design**: Mobile-first approach supporting healthcare workers in field conditions

### Backend Architecture
- **Web Framework**: Flask with Blueprint-style route organization
- **Database ORM**: SQLAlchemy with declarative models
- **Authentication**: Flask-Login with role-based access control (admin, doctor, CHW)
- **Session Management**: Flask sessions with proxy fix for deployment environments
- **Form Handling**: WTForms for validation and CSRF protection
- **Security**: Password hashing with Werkzeug, audit logging for compliance

### Data Storage Solutions
- **Primary Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Connection Pooling**: SQLAlchemy engine with pool recycling and pre-ping health checks
- **Schema Design**: FHIR-inspired patient models with comprehensive health record tracking
- **Audit Trail**: Complete audit logging system for regulatory compliance

### Authentication and Authorization
- **Multi-Role System**: Three distinct roles with different permission levels
- **Decorators**: Custom role-based decorators (@admin_required, @role_required)
- **Session Security**: Secure session management with configurable secret keys
- **User Management**: Complete user lifecycle with registration approval workflow

### Core Data Models
- **User Model**: Healthcare workers with role-based permissions and geographic assignments
- **Patient Model**: FHIR-compliant patient records with comprehensive demographics
- **Health Records**: Medical history, vital signs, diagnoses, and treatment plans
- **Outreach Events**: Community health program management with attendance tracking
- **Payment System**: Integrated billing and CHW allowance management
- **Audit Logging**: Comprehensive activity tracking for compliance and security

## External Dependencies

### Payment Processing
- **IntaSend API**: M-Pesa and card payment processing for patient fees and CHW allowances
- **Webhook Integration**: Real-time payment status updates and transaction verification
- **Multi-Currency Support**: Primarily KES with extensibility for other currencies

### Frontend Libraries
- **Bootstrap 5**: UI component framework and responsive grid system
- **Font Awesome**: Icon library for consistent visual elements
- **jQuery**: Enhanced form interactions and AJAX functionality

### Development Tools
- **Flask Extensions**: SQLAlchemy, Login, WTF for core functionality
- **Werkzeug**: WSGI utilities and security helpers
- **Python Standard Library**: UUID generation, datetime handling, logging

### Infrastructure Requirements
- **Database**: PostgreSQL instance with connection pooling
- **Environment Variables**: Session secrets, database URLs, IntaSend API credentials
- **Deployment**: WSGI-compatible hosting with proxy support for production environments
