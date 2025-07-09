# 🚘 Car-themed RESTful Web Application

[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15.2-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.13.1-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://swagger.io/)

A comprehensive RESTful web application built with Django and Django REST Framework, featuring a sophisticated car database with advanced search, filtering, and recommendation capabilities.

## 🎬 Live Demo

<div align="center">

[![Watch Demo](https://img.shields.io/badge/Watch-Demo-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=r6YzDdX4hO0&ab_channel=WuYue)

[![Watch Demo](https://img.youtube.com/vi/r6YzDdX4hO0/maxresdefault.jpg)](https://www.youtube.com/watch?v=r6YzDdX4hO0&ab_channel=WuYue)

</div>

## 🎯 Why I Built This Project

This project was developed as part of my **CM3035 Advanced Web Development** coursework at the University of London. I chose to build a car-themed application because:

- **Real-world complexity**: Cars have multiple interconnected attributes (engines, performance, brands, tags) that demonstrate complex database relationships
- **Data normalization challenges**: The project required breaking down a messy CSV dataset into 7 normalized tables
- **API design opportunities**: Rich data allowed for implementing advanced features like recommendations and brand statistics
- **Modern web development showcase**: Opportunity to demonstrate current best practices in Django and REST API development

## 📚 What I Learned

Through this project, I gained hands-on experience with:

### Backend Development

- **Django Model Design**: Implementing complex relationships (OneToOne, ForeignKey, ManyToMany) and proper data normalization
- **REST API Architecture**: Building comprehensive RESTful endpoints with proper HTTP methods and status codes
- **Query Optimization**: Using `select_related` and `prefetch_related` for efficient database queries
- **Data Processing**: Cleaning and migrating real-world messy data into structured database models

### Advanced Django Features

- **Custom Management Commands**: Creating data import scripts for bulk operations
- **Django REST Framework**: ViewSets, serializers, nested routers, and API documentation
- **Testing Best Practices**: Unit testing with Factory Boy for reliable test data generation
- **Code Organization**: Separating concerns with services, utils, and modular architecture

### Software Engineering Principles

- **Clean Code Architecture**: Organizing code into logical modules with clear responsibilities
- **Documentation**: API documentation with Swagger UI and comprehensive project documentation
- **Version Control**: Git best practices and project structure organization

## ✨ Features

### 🚀 Core API Endpoints

- **CRUD Operations**: Full Create, Read, Update, Delete for cars and engines
- **Advanced Search**: Filter by brand, price range, performance metrics, and tags
- **Nested Resources**: Engine management within car resources
- **Pagination**: Efficient handling of large datasets

### 🤖 Smart Recommendations

- **Personalized Suggestions**: Get 5 similar cars based on performance, price, brand, and tags
- **Algorithm-driven**: Uses multiple similarity metrics for accurate recommendations

### 📊 Brand Analytics

- **Statistical Insights**: Average prices, performance metrics, and popular features by brand
- **Aggregated Data**: Complex database aggregations for business intelligence

### 🛠️ Developer Experience

- **Interactive API Documentation**: Swagger UI and ReDoc integration
- **Comprehensive Testing**: Unit tests covering all major functionality
- **Clean Architecture**: Modular design following Django best practices

## 🏗️ Architecture

```
car-project/
├── carproject/              # Project configuration
├── cars/                   # Main application
│   ├── services/          # Business logic layer
│   ├── utils/            # Helper functions and utilities
│   ├── test_cases/       # Comprehensive unit tests
│   ├── management/       # Custom Django commands
│   └── templates/        # HTML templates
└── data/                 # Dataset and migrations
```

## 🗄️ Database Design

The application uses a normalized database design with 7 interconnected tables, breaking down the original CSV dataset into efficient, related entities:


| Table              | Type        | Key Fields                                  | Relationships             | Purpose                 |
| ------------------ | ----------- | ------------------------------------------- | ------------------------- | ----------------------- |
| 🚗 **Car**         | Core Entity | `id`, `name`, `slug`, `year`, `price_range` | Hub for all relationships | Central car information |
| 🏭 **Brand**       | Reference   | `id`, `name`, `slug`, `country`             | 1:M → Car                 | Manufacturer data       |
| 🏁 **Performance** | Detail      | `id`, `top_speed`, `acceleration`           | 1:1 ← Car                 | Performance metrics     |
| ⚙️ **Engine**      | Detail      | `id`, `layout`, `displacement`, `power`     | M:1 ← Car                 | Engine specifications   |
| ⛽ **FuelType**    | Reference   | `id`, `name`, `description`                 | M:M ↔ Car                 | Fuel classifications    |
| 📂 **TagCategory** | Reference   | `id`, `name`, `description`                 | 1:M → Tag                 | Tag organization        |
| 🏷️ **Tag**         | Detail      | `id`, `name`, `category_id`                 | M:M ↔ Car                 | Car categorization      |

### Design Benefits

- ✅ **Eliminates Data Redundancy**: Normalized structure prevents duplicate information
- ✅ **Ensures Data Integrity**: Foreign key constraints maintain referential integrity
- ✅ **Enables Efficient Querying**: Optimized for complex searches and aggregations
- ✅ **Supports Complex Relationships**: Handles real-world car data complexity
- ✅ **Facilitates Maintenance**: Easy to update and extend without affecting other tables

## 🚀 Quick Start

### Prerequisites

- Python 3.13.1
- macOS (tested on macOS Sequoia 15.2)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd car-project
```

2. **Create and activate virtual environment**

```bash
conda create --name car-project python=3.13.1
conda activate car-project
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run migrations and load data**

```bash
python manage.py migrate
python manage.py load_and_store
```

5. **Create admin user**

```bash
python manage.py createsuperuser
```

6. **Start development server**

```bash
python manage.py runserver
```

### 🔑 Admin Credentials

- **Username**: `admin`
- **Password**: `cm3035midterm`

## 🧪 Testing

Run the comprehensive test suite:

```bash
python manage.py test cars.test_cases
```

## 📊 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## 🛠️ Tech Stack

- **Backend**: Django 5.1.4, Django REST Framework 3.15.2
- **Database**: SQLite (development), PostgreSQL-ready
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Testing**: Factory Boy, Faker
- **Filtering**: django-filter
- **Routing**: drf-nested-routers

## 📈 Key Achievements

- ✅ **7 Normalized Tables**: Efficient database design with proper relationships
- ✅ **15+ API Endpoints**: Comprehensive RESTful API coverage
- ✅ **Smart Recommendations**: Algorithm-based car suggestions
- ✅ **95%+ Test Coverage**: Reliable codebase with comprehensive testing
- ✅ **Query Optimization**: Efficient database operations
- ✅ **Clean Architecture**: Maintainable and scalable code structure

## 🔮 Future Enhancements

- **Caching**: Redis integration for improved performance
- **Search**: Elasticsearch for advanced search capabilities
- **Real-time**: WebSocket support for live updates
- **GraphQL**: Flexible query interface
- **CI/CD**: Automated testing and deployment pipeline

## 📝 License

This project is part of academic coursework and is intended for educational purposes.

---

**Built with ❤️ by [Yue Wu](https://www.linkedin.com/in/yuewuxd/)**

_University of London - CM3035 Advanced Web Development_
