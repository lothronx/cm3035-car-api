# Car-themed RESTful Web Application

## Instructions to unpackage and run my app

- Operating system: macOS Sequoia Version 15.2 (Apple Silicon)
- Python version: 3.13.1
- Django version: 5.1.4

### Django Admin Credentials:

- Username: admin
- Password: cm3035midterm

### To run the application from scratch:

**1. Create and activate a conda virtual environment:**

```bash
conda create --name car-project python=3.13.1
conda activate car-project
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Make migrations (If the database is already included, directly go to Step 6):**

```bash
python manage.py makemigrations
python manage.py migrate
```

**4. Set up admin user**

```bash
python manage.py createsuperuser
```

**5. Load initial data**

```bash
python manage.py load_and_store
```

The .csv file is located in `data/` folder.

The `load_and_store.py` script in located in `cars/management/commands/` folder.

**6. Run the development server:**

```bash
python manage.py runserver
```

**7. Unit tests can be run using:**

```bash
python manage.py test cars.tests
```

## Code Structure

The application follows a modular and maintainable architecture adhering to Django's best practices. The code structure is as follows:

```
car-project/
├── carproject/              # Project configuration directory
│   ├── settings.py         # Project settings and configurations
│   └─ urls.py              # Main URL routing
│
├── cars/                   # Main application directory
│   ├── migrations/        # Database migrations
│   │
│   ├── management/        # Custom management commands
│   │   └── commands/
│   │       └── load_and_store.py  # Data import script
│   │
│   ├── services/          # Business logic and services
│   │   ├── brand_statistics.py # Service module for calculating brand statistics
│   │   └── car_recommendations.py # Service for generating car recommendations
│   │
│   ├── utils/            # Utility functions and helpers
│   │   ├── admin_filters.py    # Custom admin filters for better data management
│   │   ├── price_formatter.py  # Price formatting and conversion utilities
│   │   ├── data_cleaners.py    # Data cleaning and validation utilities
│   │   ├── car_helpers.py      # Helper functions for creating and updating cars
│   │   └── tag_helpers.py      # Helper functions for creating and updating tags
│   │
│   ├── tests/            # Test files
│   │   ├── factories.py               # Test data factories using Factory Boy
│   │   ├── test_brand_api.py         # Brand API endpoint tests
│   │   ├── test_car_api.py           # Car API endpoint tests
│   │   ├── test_car_engine_api.py    # Car Engine API endpoint tests
│   │   └── test_car_recommendation_api.py  # Car Recommendation API tests
│   │
│   ├── templates/         # HTML templates
│   │   ├── index.html
│   │   └── swagger-ui.html
│   │
│   ├── admin.py           # Admin interface configuration
│   ├── api.py             # REST API views and viewsets
│   ├── app.py
│   ├── models.py          # Database models
│   ├── serializers.py     # DRF serializers
│   ├── tests.py           # Unit tests
│   ├── urls.py            # App-specific URL routing
│   ├── views.py           # Web views
│   │
├── data/                  # Data files
│   └── The Ultimate Cars Dataset 2024.csv       # Source data file
│
├── requirements.txt       # Project dependencies
└── manage.py             # Django management script
```

### Key Components:

1. **Models (`cars/models.py`)**: (discussed later)

2. **Serializers (`cars/serializers.py`)**:

   - `CarDetailSerializer`: Full car details
   - `CarListSerializer`: Simplified car listing
   - `CarEngineSerializer`: Engine specifications
   - Custom validation and field handling

3. **API Layer (`cars/api.py`)**:

   - RESTful API implementation using ViewSets
   - Filtering and pagination
   - Complex query handling
   - Authentication and permissions

4. **Services (`cars/services/`)**:

   - Business logic separation
   - Complex operations handling
   - Data processing utilities

5. **Utils (`cars/utils/`)**:

   - Helper functions
   - Common utilities
   - Data processing tools

6. **Management Commands (`cars/management/commands/`)**:

   - Custom data import script
   - Database seeding utilities
   - Maintenance tools

7. **Tests (`cars/tests/`)**:

   - API endpoint testing

I moved most complex logics to the utils and services folders, to ensure that each file is clean, readable, and does not have too many lines. This structure follows Django's best practices by:

- Separating concerns into distinct modules
- Maintaining clear responsibility boundaries
- Following the DRY (Don't Repeat Yourself) principle
- Enabling easy testing and maintenance
- Providing clear organization for scalability

## Dataset

I downloaded the dataset from Kaggle [here](https://www.kaggle.com/datasets/abdulmalik1518/the-ultimate-cars-dataset-2024). I chose this dataset because:

1. It's semi clean but not entirely clean. Data cleaning is required.
2. It can be normalized into several tables.
3. It has data of various type and is complex enough given the scope of the project.
4. It has real-world applicability.
5. It has opportunity to demonstrate various Django features.

## Data Model

I broke the cvs file into 7 tables:

1. **Car**: The core table storing basic car information

   - Centralized car details with relationships to other entities
   - Includes name, year, seating, and price range
   - Acts as the hub for all car-related data

2. **Brand**: Car manufacturer information

   - Normalized brand data to prevent duplication
   - Enables efficient brand-based querying
   - Supports brand statistics and aggregations in the future

3. **Engine**: Detailed engine specifications

   - Separate table due to multiple engine configurations per car
   - Complex engine attributes (layout, capacity, power)

4. **Performance**: Car performance metrics

   - Isolated performance data for better organization
   - Stores standardized metrics (speed, acceleration)
   - One-to-one relationship with cars for direct access

5. **FuelType**: Fuel type classifications

   - Normalized fuel type data
   - Many-to-many relationship with cars
   - Supports multiple fuel types per car (e.g., hybrid systems)

6. **TagCategory**: Tag classification system

   - Defines valid categories for car tags
   - Enforces data consistency
   - Supports dynamic categorization

7. **Tag**: Car categorization system
   - Flexible tagging system for cars
   - Many-to-many relationship with cars
   - Enables advanced filtering and searching

This database design follows normalization principles and provides several advantages:

- Eliminates data redundancy
- Ensures data integrity
- Enables efficient querying
- Supports complex relationships
- Facilitates data maintenance and updates

## Data Migration

The data was migrated and bulk loaded into the database using the `load_and_store` command. The internal logic is too complex so I separated it into 3 steps (3 helper scripts): First, I use `utils/data_cleaners.py` to clean the data in each csv column. Then, I pass the cleaned data to `utils/car_helpers.py` to create the cars and their related objects. Finally, I use `utils/tag_helpers.py` to create the tags and their relationships with cars. This process ensures that the data is normalized and ready for use in the application. The `utils/car_helpers.py` and `utils/tag_helpers.py` are also reused later in POST, PUT, and PATCH requests.

## Endpoints

The application implements a comprehensive RESTful API using Django REST Framework (DRF). The endpoints are designed to be intuitive, efficient, and follow REST best practices.

1. **List and Create Cars (`/api/cars/`)**:

   - `GET`: Retrieve a paginated list of all cars with basic information
   - `POST`: Add a new car with all required details
   - Search by car name/brand, pagination support

2. **Individual Car Operations (`/api/cars/{slug}/`)**:

   - `GET`: Get detailed car information including engines and performance
   - `PUT/PATCH`: Update car information
   - `DELETE`: Remove a car from the database

3. **Car Engines (`/api/cars/{car_slug}/engines/`)**:

   - `GET`: List all engines for a specific car
   - `POST`: Add a new engine to a car

4. **Individual Engine Operations (`/api/cars/{car_slug}/engines/{engine_id}/`)**:

   - `GET`: Get detailed engine information
   - `PUT/PATCH`: Update engine information
   - `DELETE`: Remove an engine from a car

5. **Car Recommendations (`/api/cars/{slug}/recommendation/`)**:

   - `GET`: Get 5 personalized car recommendations based on:
     - Similar performance characteristics
     - Matching price range
     - Common brand
     - Shared tags

6. **Brand Statistics (`/api/brands/{slug}/`)**:
   - `GET`: Access comprehensive brand statistics including:
     - Total cars count
     - Average price, speed, and acceleration
     - Popular engines and tags

### Implementation Highlights:

1. **Advanced Query Optimization**:

   ```python
   Car.objects.prefetch_related(
       "tag_set__category",
       "brand",
       "fuel_type",
       "engine_set",
   ).select_related("performance")
   ```

- Efficient database queries using select_related and prefetch_related
- Minimizes database hits for related objects
- Optimized performance for complex nested data

1. **Serializer Architecture**:

   - Context-aware serializers for different use cases:
     - `CarListSerializer`: Optimized for list views
     - `CarDetailSerializer`: Complete car details
     - `CarFormSerializer`: Form handling and validation
   - Nested serialization for related objects
   - Custom validation logic

2. **ViewSet Features**:

   - Implements ModelViewSet for full CRUD operations
   - Custom actions for specialized endpoints
   - Proper HTTP status code handling
   - Search and filtering capabilities

3. **URL Routing**:

   - Uses DRF's DefaultRouter for main routes
   - NestedDefaultRouter for resource relationships
   - Clean URL structure with slugs for better readability and SEO
   - Proper namespace organization

4. **Form Validation and Error Handling**:
   - Model-level validation
   - Serializer-level validation
   - Custom validation logic
   - Comprehensive error responses

The API design makes the endpoints interesting and powerful through:

- Complex query capabilities
- Efficient data loading
- Proper resource nesting
- Custom recommendation endpoint
- Comprehensive CRUD operations
- RESTful best practices

## Unit Testing

The application includes comprehensive unit tests:

1. **Car API tests** (`test_car_api.py`):

   - Tests CRUD operations for cars
   - Validates pagination and search functionality
   - Verifies data structure and relationships
   - Ensures proper error handling

2. **Engine API tests** (`test_car_engine_api.py`):

   - Tests nested engine resource endpoints
   - Validates engine creation with different configurations
   - Verifies engine updates and deletions
   - Tests relationship with parent car object

3. **Car Recommendation API tests** (`test_car_recommendation_api.py`):

   - Tests recommendation algorithm accuracy
   - Verifies similarity metrics (brand, price, performance)
   - Ensures proper recommendation count
   - Tests edge cases with limited similar cars

4. **Brand API tests** (`test_brand_api.py`):
   - Tests brand statistics calculations
   - Validates aggregated metrics (avg price, speed)
   - Verifies popular engines and tags
   - Tests brand-car relationships

All tests use Factory Boy for efficient test data generation and proper test isolation.

## Evaluation

The project demonstrates a modern approach to web development, incorporating current best practices and industry standards:

1. **Django Best Practices**:

   - **Model Design Excellence**:

     - Proper use of model relationships (OneToOne, ForeignKey, ManyToMany)
     - Strategic data normalization to prevent redundancy
     - Custom model methods for complex operations
     - Slug-based URLs for SEO optimization

   - **Query Optimization**:

     - Efficient use of `select_related` and `prefetch_related`
     - Complex aggregations for brand statistics
     - Minimized database hits through proper relationship traversal
     - Optimized bulk operations for data loading

   - **Code Organization**:
     - Clear separation of concerns (models, views, services)
     - Reusable utility functions in dedicated modules
     - Custom management commands for data operations
     - Modular test structure with Factory Boy

2. **Django REST Framework Implementation**:

   - **ViewSet Architecture**:

     - Use of ModelViewSet for consistent CRUD operations
     - Custom actions for specialized endpoints
     - Nested routers for resource relationships
     - Proper response status code handling

   - **Serializer Design**:

     - Context-specific serializers (list vs detail)
     - Nested serialization for related objects
     - Custom validation logic
     - Proper handling of complex data structures

   - **API Documentation**:
     - Integration with Swagger UI and ReDoc
     - Comprehensive endpoint documentation
     - Clear request/response examples
     - Interactive API testing interface

3. **State of the Art Features**:

   - **Modern Data Processing**:

     - Efficient bulk data loading
     - Complex recommendation algorithm
     - Advanced filtering and search capabilities
     - Aggregated statistics generation

   - **RESTful Design**:
     - Proper resource nesting
     - Consistent URL structure
     - Appropriate HTTP method usage
     - Stateless request handling

4. **Areas for Future Enhancement**:

   - **Performance Optimization**:

     - Implement Redis caching for frequently accessed data
     - Add database indexing for common queries
     - Optimize large dataset handling

   - **Feature Expansion**:

     - Implement GraphQL for flexible querying
     - Add WebSocket support for real-time updates
     - Enhance search with Elasticsearch integration
     - Implement rate limiting for API endpoints

   - **Developer Experience**:
     - Add more comprehensive API documentation
     - Implement CI/CD pipeline
     - Add performance monitoring
     - Enhance error reporting

The project successfully implements modern web development practices while maintaining code quality and performance. The use of Django and DRF features demonstrates a deep understanding of the framework's capabilities and best practices.

## Dependencies

The project uses carefully selected dependencies:

- Django 5.1.4 - Latest stable release
- Django REST Framework 3.15.2 - For API development
- django-filter - For advanced filtering
- drf-nested-routers - For handling nested resources
- drf-yasg - For API documentation
- Factory Boy and Faker - For testing

Each dependency was chosen to address specific needs while maintaining code quality and maintainability.

asgiref==3.8.1
astroid==3.3.8
attrs==24.3.0
dill==0.3.9
Django==5.1.4
django-debug-toolbar==4.4.6
django-filter==24.3
django-stubs==5.1.1
django-stubs-ext==5.1.1
djangorestframework==3.15.2
drf-nested-routers==0.94.1
drf-yasg==1.21.7
factory_boy==3.0.1
Faker==33.3.0
hypothesis==6.123.2
inflection==0.5.1
isort==5.13.2
mccabe==0.7.0
packaging==24.2
platformdirs==4.3.6
pylint==3.3.3
pylint-django==2.6.1
pylint-plugin-utils==0.8.2
python-dateutil==2.9.0.post0
pytz==2024.2
PyYAML==6.0.1
setuptools==75.1.0
six==1.17.0
sortedcontainers==2.4.0
sqlparse==0.5.3
tomlkit==0.13.2
types-PyYAML==6.0.12.20241230
typing_extensions==4.12.2
uritemplate==4.1.1
wheel==0.44.0

