# AI-Optimized Microgrid System

A modern microgrid management system that leverages artificial intelligence for optimal energy distribution and consumption.

## Features

- Real-time energy monitoring and management
- AI-powered load forecasting and optimization
- User authentication and authorization
- RESTful API for system control and monitoring
- Data visualization and analytics
- Integration with renewable energy sources

## Tech Stack

- FastAPI (Backend Framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- JWT (Authentication)
- Pandas & NumPy (Data Processing)
- Scikit-learn (Machine Learning)
- Matplotlib & Seaborn (Visualization)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-microgrid.git
cd ai-microgrid
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/microgrid
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
ai-microgrid/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   └── user.py
│   │   └── main.py
│   ├── tests/
│   ├── .env
│   ├── requirements.txt
│   └── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 