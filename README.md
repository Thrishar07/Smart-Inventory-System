
# Smart Inventory & Stockout Prediction System

An intelligent inventory management application that helps small retailers monitor stock levels, analyze sales patterns, predict product demand, identify potential stockouts, and make data-driven reorder decisions.

Built using **Python, FastAPI, PostgreSQL, Streamlit, Machine Learning, and Docker**.

## 1. Project Overview

Small retail businesses often manage inventory manually, making it difficult to identify fast-moving products, predict future demand, and prevent stockouts.

This project addresses that problem by combining inventory management, sales analytics, and machine learning-based demand forecasting into a centralized application.

The system allows supermarket managers to:

- Manage products and suppliers.
- Track available inventory.
- Record product sales.
- Monitor inventory levels.
- Analyze historical sales patterns.
- Predict future product demand.
- Identify products at risk of stockouts.
- Generate reorder recommendations.

## 2. Key Features

### Product Management
- Add and manage products.
- Maintain product information and supplier associations.
- Retrieve product details through REST APIs.

### Supplier Management
- Maintain supplier information.
- Associate suppliers with products.
- Retrieve supplier records.

### Inventory Management
- Track current stock quantities.
- Update inventory records.
- Monitor stock availability.
- Identify low-stock products.

### Sales Management
- Record sales transactions.
- Retrieve historical sales information.
- Maintain sales data for demand analysis.

### Inventory Analytics
- Calculate stockout risk.
- Analyze inventory levels.
- Identify products requiring attention.

### Machine Learning-Based Demand Prediction
- Generate and prepare historical sales datasets.
- Perform feature engineering.
- Train a demand prediction model.
- Save the trained model using Joblib.
- Generate product demand predictions.

### Reorder Recommendations
- Estimate product demand.
- Calculate reorder requirements.
- Provide inventory recommendations using stock and demand information.

### Interactive Dashboard
- View inventory information.
- Manage products and suppliers.
- Record sales.
- Monitor stock levels.
- Explore analytics and demand predictions.

## 3. Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| Dashboard | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Model Serialization | Joblib |
| Data Visualization | Plotly |
| API Testing | Swagger UI, HTTPX |
| Automated Testing | Pytest |
| Containerization | Docker |
| Container Orchestration | Docker Compose |
| Version Control | Git and GitHub |

## 4. System Architecture

The application follows a modular architecture.

```text
                 USER
                   |
                   v
          STREAMLIT DASHBOARD
                   |
             HTTP Requests
                   |
                   v
             FASTAPI BACKEND
                   |
          +--------+---------+
          |        |         |
          v        v         v
       Products Inventory  Sales
          API      API      API
          |        |         |
          +--------+---------+
                   |
                   v
             POSTGRESQL
                   |
                   v
          HISTORICAL SALES DATA
                   |
                   v
          MACHINE LEARNING
                   |
          +--------+---------+
          |                  |
          v                  v
     Demand Prediction  Stockout Analysis
          |                  |
          +--------+---------+
                   |
                   v
          REORDER RECOMMENDATIONS
```

Docker Compose manages three services:

1. PostgreSQL database.
2. FastAPI backend.
3. Streamlit dashboard.

## 5. Project Structure

```text
smart-inventory-system/
│
├── app/
│   ├── api/
│   │   ├── analytics.py
│   │   ├── inventory.py
│   │   ├── predictions.py
│   │   ├── products.py
│   │   ├── recommendations.py
│   │   ├── sales.py
│   │   └── suppliers.py
│   │
│   ├── core/
│   │   └── database.py
│   │
│   ├── ml/
│   │   ├── models/
│   │   │   └── demand_model.joblib
│   │   ├── features.py
│   │   ├── generate_sample_data.py
│   │   ├── predict.py
│   │   ├── prepare_data.py
│   │   └── train_model.py
│   │
│   ├── schemas/
│   │   ├── inventory.py
│   │   ├── product.py
│   │   └── sales.py
│   │
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── daily_sales.csv
│   ├── ml_features.csv
│   └── synthetic_daily_sales.csv
│
├── tests/
│   ├── conftest.py
│   ├── test_inventory.py
│   └── test_products.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## 6. Inventory Business Logic

The system uses inventory calculations to support stock monitoring and reorder decisions.

### Average Daily Demand

Estimates the average number of units sold per day.

```text
Average Daily Demand =
Total Units Sold / Number of Days
```

Example:

If 150 units are sold over 30 days:

```text
Average Daily Demand = 150 / 30
                     = 5 units/day
```

### Estimated Days Until Stockout

Estimates how long the available inventory may last at the current demand rate.

```text
Days Until Stockout =
Current Stock / Average Daily Demand
```

Example:

```text
Current Stock = 20 units
Daily Demand  = 5 units

Days Until Stockout = 20 / 5
                    = 4 days
```

### Reorder Point

The reorder point estimates the inventory level at which a new order should be placed.

```text
Reorder Point =
(Average Daily Demand × Lead Time) + Safety Stock
```

Where:

- Average Daily Demand = expected daily product sales.
- Lead Time = number of days required for supplier delivery.
- Safety Stock = additional inventory maintained to reduce stockout risk.

Example:

```text
Daily Demand = 5 units
Lead Time    = 7 days
Safety Stock = 10 units

Reorder Point = (5 × 7) + 10
              = 45 units
```

When inventory reaches the reorder point, the business should consider placing a new order.

*Note: These examples explain standard inventory management concepts. Actual calculations and assumptions depend on the implementation.*

## 7. Machine Learning Workflow

The demand prediction module follows a structured machine learning workflow.

```text
Historical Sales Data
         |
         v
Data Generation / Collection
         |
         v
Data Preprocessing
         |
         v
Feature Engineering
         |
         v
Model Training
         |
         v
Trained Model (.joblib)
         |
         v
Demand Prediction
         |
         v
Inventory Recommendations
```

The machine learning module contains:

- `generate_sample_data.py`: Generates sample sales records.
- `prepare_data.py`: Prepares sales data for modelling.
- `features.py`: Creates model input features.
- `train_model.py`: Trains and saves the demand forecasting model.
- `predict.py`: Loads the trained model and generates predictions.

The trained model is serialized using Joblib and stored in `app/ml/models/`.

**Important:** The included datasets are sample/synthetic data, not verified real supermarket sales records. Predictions should be validated against real historical data before production use.

## 8. Database Design

The application uses PostgreSQL for persistent data storage.

Main database tables:

| Table | Purpose |
|---|---|
| `products` | Stores product information |
| `suppliers` | Stores supplier information |
| `inventory` | Tracks available stock |
| `sales` | Stores sales transactions |

Relationships:

- Products can be associated with suppliers.
- Inventory records reference products.
- Sales records reference products.

## 9. REST API

The backend is built using FastAPI.

| Endpoint group | Functionality |
|---|---|
| `/products` | Product management |
| `/suppliers` | Supplier management |
| `/inventory` | Inventory operations |
| `/sales` | Sales operations |
| `/analytics` | Inventory analytics |
| `/predictions` | Demand forecasting |
| `/recommendations` | Reorder recommendations |

Interactive API documentation is available through Swagger UI:

```text
http://localhost:8000/docs
```

## 10. Installation and Local Setup

### Prerequisites

- Python 3.12 or compatible Python version.
- PostgreSQL.
- Git.
- Docker and Docker Compose (for containerized execution).

### Clone the Repository

```bash
git clone https://github.com/Thrishar07/Smart-Inventory-System.git

cd Smart-Inventory-System
```

### Create a Virtual Environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root.

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_inventory
DB_USER=inventory_app
DB_PASSWORD=your_database_password
```

Replace the example password with your own local PostgreSQL password.

Do not commit `.env` or expose database credentials.

### Start the Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### Start the Dashboard

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run dashboard/app.py
```

Dashboard:

```text
http://localhost:8501
```

## 11. Running with Docker

The project supports containerized execution using Docker Compose.

### Build and Start Containers

```bash
docker compose up -d --build
```

### Check Container Status

```bash
docker compose ps
```

### View Logs

```bash
docker compose logs -f
```

### Stop Containers

```bash
docker compose down
```

The PostgreSQL database uses a named Docker volume to preserve database data when containers are stopped and removed.

Avoid using `docker compose down -v` unless you intentionally want to delete the database volume.

## 12. Testing

The project includes automated tests using Pytest.

Run:

```bash
python -m pytest -v
```

The test suite includes product and inventory API tests, along with shared test configuration.

## 13. Future Improvements

- Integrate real-time sales data.
- Improve demand forecasting accuracy.
- Add model evaluation and monitoring.
- Implement role-based authentication.
- Add automated supplier reorder workflows.
- Integrate an LLM-powered inventory assistant.
- Use Retrieval-Augmented Generation (RAG) for inventory-related questions.
- Add Redis caching for frequently accessed data.
- Deploy the application to cloud infrastructure.
- Add monitoring and observability.

## 14. Learning Outcomes

Through this project, I explored:

- Designing REST APIs using FastAPI.
- Connecting Python applications to PostgreSQL.
- Implementing CRUD operations.
- Building inventory and sales management workflows.
- Processing data using Pandas and NumPy.
- Developing a machine learning pipeline.
- Integrating trained models into backend APIs.
- Building interactive dashboards using Streamlit.
- Containerizing multi-service applications using Docker Compose.
- Managing source code using Git and GitHub.

## 15. Author

**Thrisha R**

GitHub: [Thrishar07](https://github.com/Thrishar07)

---

**Project:** Smart Inventory & Stockout Prediction System

**Status:** Core application and Docker containerization implemented. Cloud deployment and further improvements planned.