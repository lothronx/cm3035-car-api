# Car Project API Documentation

This document provides an overview of the RESTful API endpoints available in the Car Project. The API is designed to manage cars, their engines, brands, and provide recommendations.

## API Endpoints Overview

### Cars Management

#### 1. List and Create Cars (`/api/cars/`)

- **GET**: Retrieve a paginated list of all cars with basic information including name, brand, price, tags, and url to the car's detail page,
- **POST**: Add a new car to the database with all required details, including name, brand, year, fuel types, etc..
- **Highlights**:
  - Search functionality by car name or brand
  - Pagination support

#### 2. Individual Car Operations (`/api/cars/{slug}/`)

- **GET**: Get detailed information about a specific car including its engines and performance data
- **PUT/PATCH**: Update car information
- **DELETE**: Remove a car from the database
- **Highlights**:
  - Uses slug-based URLs for better SEO and readability

### Engine Management

#### 3. Car Engines (`/api/cars/{car_slug}/engines/`)

- **GET**: List all engines associated with a specific car, including cylinder layout, cylinder count, aspiration, etc..
- **POST**: Add a new engine to a car
- **Highlights**:
  - Engine specifications (power, torque, displacement)
  - Support for multiple engines per car
  - Ordered by engine ID for consistency

#### 4. Individual Engine Operations (`/api/cars/{car_slug}/engines/{engine_id}/`)

- **GET**: Get detailed information about a specific engine
- **PUT/PATCH**: Update engine information
- **DELETE**: Remove an engine from a car

### Recommendation System

#### 5. Car Recommendations (`/api/cars/{slug}/recommendation/`)

- **GET**: Receive personalized car recommendations based on:
  - Similar performance characteristics
  - Matching price range
  - Common brand
  - Shared tags
- **Highlights**:
  - Help users discover similar cars based on their interests
  - Extensive use of aggregations and annotations

### Brand Management

#### 6. Brand Details (`/api/brands/{slug}/`)

- **GET**: Access comprehensive brand information including:
  - Total number of cars of the brand in the database
  - Average price, top speed, and acceleration of all cars of the brand
  - Popular engines used by the brand
  - Popular tags associated with the brand
- **Highlights**:
  - Detailed brand statistics
  - The complexity of queries used

## Dependencies

Python version: 3.13.1

Django version: 5.1.4

python packages:
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
drf-yasg==1.21.7
hypothesis==6.123.2
isort==5.13.2
mccabe==0.7.0
platformdirs==4.3.6
pylint==3.3.3
pylint-django==2.6.1
pylint-plugin-utils==0.8.2
pyyaml==6.0.1
setuptools==75.1.0
sortedcontainers==2.4.0
sqlparse==0.5.3
tomlkit==0.13.2
types-PyYAML==6.0.12.20241230
typing_extensions==4.12.2
uritemplate==4.1.1
wheel==0.44.0
