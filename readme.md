Of course. Here is a comprehensive documentation for the project, structured as a professional `README.md` file. You can share this directly with your interviewer. It explains the project's objective, architecture, technical choices, and provides a full guide on how to set up, run, and test every feature.

---

# Contextual News Retrieval API

## 1. Project Objective

This project is a backend system designed to fetch, organize, and enrich news articles. It leverages a Large Language Model (LLM) to understand the nuances of a user's query, including their location, to provide the most relevant news.

The system showcases the ability to:
*   Utilize an LLM (Google Gemini) to identify key entities, concepts, and user intent.
*   Retrieve data from a database using multiple strategies (category, source, location, etc.).
*   Process, rank, and enrich results for relevance and comprehensiveness.
*   Implement a location-based trending news algorithm based on simulated user engagement.
*   Expose a clean, RESTful API built with FastAPI.

---

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

### Intelligent Endpoint

This endpoint uses the LLM to automatically determine the user's intent.

#### `GET /api/v1/news/`
*   **Description**: The primary endpoint for retrieving news. It uses an LLM to analyze the query and fetches data based on the identified intent.
*   **Parameters**:
    *   `query` (required, string): The user's natural language query (e.g., "tech news near SF").
    *   `lat` (optional, float): User's latitude for location-based queries.
    *   `lon` (optional, float): User's longitude for location-based queries.
*   **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/?query=business%20news%20from%20reuters&lat=40.71&lon=-74.00"
    ```

### Direct Endpoints

These endpoints provide direct access to data without complex query analysis.

#### `GET /api/v1/news/category`
*   **Description**: Retrieves articles from a specific category, ranked by the most recent publication date.
*   **Parameters**: `name` (required, string), `limit` (optional, int).
*   **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/category?name=Technology"
    ```

#### `GET /api/v1/news/source`
*   **Description**: Retrieves articles from a specific news source, ranked by the most recent publication date.
*   **Parameters**: `name` (required, string), `limit` (optional, int).
*   **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/source?name=Reuters"
    ```

#### `GET /api/v1/news/nearby`
*   **Description**: Retrieves articles published within a radius of a location, ranked by closest distance first.
*   **Parameters**: `lat`, `lon` (required, float), `radius` (optional, float), `limit` (optional, int).
*   **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/nearby?lat=37.4419&lon=-122.1430&radius=10"
    ```

### Bonus API: Trending News

#### `POST /api/v1/events`
*   **Description**: Logs a user interaction event (e.g., a 'view' or 'click') which is used to power the trending algorithm.
*   **Request Body**: A JSON object with `article_id`, `user_id`, `event_type`, `user_lat`, `user_lon`.
*   **Example Request**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/events" -H "Content-Type: application/json" -d '{"article_id": "1", "user_id": "user-A", "event_type": "click", "user_lat": 37.4419, "user_lon": -122.1430}'
    ```

#### `GET /api/v1/news/trending`
*   **Description**: Returns a list of trending news articles tailored to the user's location, ranked by a computed trending score.
*   **Parameters**: `lat`, `lon` (required, float), `radius` (optional, float), `limit` (optional, int).
*   **Example Request**:
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/trending?lat=37.4419&lon=-122.1430&radius=20"
    ```

---

## 5. Core Logic Implementation

### LLM Query Analysis
The system uses a Langchain prompt template that instructs the Gemini model to act as an expert query analyzer. By providing it with Pydantic model instructions via a `JsonOutputParser`, we force the LLM to return a predictable and validated JSON object, making the integration robust and error-resistant.

### Ranking Mechanisms
Ranking is handled differently based on the user's intent to maximize relevance:
*   **Category/Source**: Ranked by `publication_date` descending (most recent first).
*   **Score/Search**: Ranked by `relevance_score` descending (most relevant first).
*   **Nearby**: Ranked by geographical distance (closest first), calculated using the accurate `geopy.distance.geodesic` method.

### Trending News Algorithm
The trending score is calculated in real-time based on three key factors specified in the requirements:
1.  **Recency**: The algorithm only considers user events that occurred in the last 24 hours.
2.  **Volume and Type**: It aggregates scores from all recent events. Different event types have different weights (`click` > `view`) to reflect varying levels of user engagement.
3.  **Geographical Relevance**: An event's contribution to the trending score is weighted by its proximity to the user making the request. The score decays linearly, from a full weight at 0km distance to zero weight at the edge of the requested radius. This ensures the results are hyper-local.

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

## 7. How to Test the Trending Feature

This feature requires a two-step process to demonstrate its functionality.

**Step 1: Reset the Database (for a clean test)**
*   Stop the server (`Ctrl+C`).
*   Delete the `news_database.db` file.
*   Restart the server. It will automatically recreate the database and load the articles.

**Step 2: Log Sample User Events**
*   Log two events for **Article "1"** in **Palo Alto** (`lat: 37.4419, lon: -122.1430`).
*   Log one event for **Article "2"** in **San Francisco** (`lat: 37.7749, lon: -122.4194`).
    *Use the `POST /api/v1/events` endpoint with the `curl` commands from the documentation above.*

**Step 3: Query for Trending News**
*   Make a request to the `GET /api/v1/news/trending` endpoint from the perspective of a user in **Palo Alto** with a 20km radius.
    ```bash
    curl -X GET "http://127.0.0.1:8000/api/v1/news/trending?lat=37.4419&lon=-122.1430&radius=20"
    ```

**Expected Result**:
*   The API will return a JSON array containing **only Article "1"**. This correctly demonstrates the system's ability to identify that Article "1" is trending locally while filtering out the event from San Francisco, which is outside the specified radius.