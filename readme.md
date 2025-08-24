
# Contextual News Retrieval API

## 1. Project Objective

This project is designed to fetch, organize, and enrich news articles. It leverages a Large Language Model (LLM) to understand the nuances of a user's query, including their location, to provide the most relevant news.

The system showcases the ability to:
*   Utilize an LLM (Google Gemini) to identify key entities, concepts, and user intent.
*   Retrieve data from a database using multiple strategies (category, source, location, etc.).
*   Process, rank, and enrich results for relevance and comprehensiveness.
*   Implement a location-based trending news algorithm based on simulated user engagement.
*   Expose a clean, RESTful API built with FastAPI.


## 2. System Architecture

The application is built using a modular, service-oriented architecture in Python to ensure a clear separation of concerns, making it scalable and maintainable.

*   **API Layer (`main.py`)**: Built with **FastAPI**, this layer is responsible for defining the RESTful endpoints, handling incoming HTTP requests, validating data using Pydantic models, and returning JSON responses.

*   **Service Layer (`services.py`)**: This is the core business logic layer. It orchestrates the flow of data, coordinating between the API layer, the LLM processor, and the database to fulfill requests.

*   **LLM Interaction Layer (`llm.py`)**: This module encapsulates all interactions with the **Google Gemini Pro** model via the **Langchain** framework. It is responsible for:
    1.  **Query Analysis**: Analyzing a user's natural language query to extract structured data (intent, entities, etc.) using a `JsonOutputParser`.
    2.  **Content Enrichment**: Generating concise, one-sentence summaries for retrieved news articles.

*   **Data Persistence Layer (`database.py`)**: This module handles all communication with the **SQLite** database. It manages the schema for articles and user events and contains all the logic for inserting, fetching, and ranking data based on various criteria.

*   **Data Modeling (`models.py`)**: Using **Pydantic**, this module defines the strict data schemas for API requests, responses, and the structured output expected from the LLM, ensuring data integrity throughout the application.

---

## 3. Technical Stack

*   **Backend Framework**: FastAPI
*   **Database**: SQLite
*   **LLM**: Google Gemini Pro
*   **LLM Framework**: Langchain (`langchain-google-genai`)
*   **Geospatial Calculations**: GeoPy
*   **Data Validation**: Pydantic
*   **API Server**: Uvicorn

---

## 4. API Endpoint Documentation

The API provides both a single "intelligent" endpoint and several direct-access endpoints.

**Base URL**: `http://127.0.0.1:8000`

<img width="1919" height="840" alt="image" src="https://github.com/user-attachments/assets/1577761d-f34b-474b-87c3-ccabd511d005" />

### Intelligent Endpoint

This endpoint uses the LLM to automatically determine the user's intent.

#### `GET /api/v1/news/`
*   **Description**: The primary endpoint for retrieving news. It uses an LLM to analyze the query and fetches data based on the identified intent.
*   **Parameters**:
    *   `query` (required, string): The user's natural language query (e.g., "tech news near SF").
    *   `lat` (optional, float): User's latitude for location-based queries.
    *   `lon` (optional, float): User's longitude for location-based queries.


### Direct Endpoints

These endpoints provide direct access to data without complex query analysis.

#### `GET /api/v1/news/category`
*   **Description**: Retrieves articles from a specific category, ranked by the most recent publication date.
*   **Parameters**: `name` (required, string), `limit` (optional, int).


#### `GET /api/v1/news/source`
*   **Description**: Retrieves articles from a specific news source, ranked by the most recent publication date.
*   **Parameters**: `name` (required, string), `limit` (optional, int).
*   **Example Request**:


#### `GET /api/v1/news/nearby`
*   **Description**: Retrieves articles published within a radius of a location, ranked by closest distance first.
*   **Parameters**: `lat`, `lon` (required, float), `radius` (optional, float), `limit` (optional, int).


### Bonus API: Trending News

#### `POST /api/v1/events`
*   **Description**: Logs a user interaction event (e.g., a 'view' or 'click') which is used to power the trending algorithm.
*   **Request Body**: A JSON object with `article_id`, `user_id`, `event_type`, `user_lat`, `user_lon`.


#### `GET /api/v1/news/trending`
*   **Description**: Returns a list of trending news articles tailored to the user's location, ranked by a computed trending score.
*   **Parameters**: `lat`, `lon` (required, float), `radius` (optional, float), `limit` (optional, int).


---




## 6. Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd contextual-news-api
    ```

2.  **Create an Environment File**: Create a file named `.env` in the root directory and add your Google API Key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be live at `http://127.0.0.1:8000`. The interactive documentation is available at `http://127.0.0.1:8000/docs`.

---



