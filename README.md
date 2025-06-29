# Helion Energy AI Scheduling Concierge

![Project: AI Booking Agent](https://img.shields.io/badge/Project-AI%20Booking%20Agent-blue)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blueviolet)
![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-green)
![Agent: LangGraph](https://img.shields.io/badge/Agent-LangGraph-orange)
![Frontend: Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)

This project is a sophisticated, conversational AI agent designed to assist users in booking appointments with the team at Helion Energy. It provides a seamless, natural language interface for scheduling, managing, and querying calendar events, powered by a robust and scalable backend architecture.

## 🚀 Live Demo

Interact with the live agent here:

https://w2usbnhyazjxp7s6a8fzv7.streamlit.app/

**Note:** The backend is hosted on a free-tier service, so the first request may take up to 30 seconds to wake the server.

## ✨ Core Features

This agent is more than a simple bot; it's a fully-featured scheduling assistant with a focus on robustness and user experience.

- **Natural Language Conversation:** Engage in a back-and-forth dialogue to book, reschedule, or delete appointments.
- **Google Calendar Integration:** All confirmed bookings are synced directly with a shared Google Calendar.
- **Intelligent Time Slot Suggestions:** The agent can find and propose available times based on the user's request (e.g., "tomorrow afternoon," "next Friday").
- **Automatic Timezone Handling:** The agent automatically detects the user's timezone, converses in their local time, and seamlessly handles conversions to the team's local time (Asia/Kolkata), ensuring clarity for a global user base.
- **Robust Concurrency & Conflict Management:** The system is designed to prevent double-bookings, even under concurrent user requests. It correctly handles:
  - **Race Conditions:** Prevents two users from booking the same slot at the exact same time.
  - **Overlapping Events:** Prevents booking a slot that overlaps with an existing meeting.
  - **Configurable Meeting Buffers:** Enforces a configurable buffer time (e.g., 15 minutes) between meetings to prevent back-to-back scheduling.
- **Stateful Agent Recovery:** The agent intelligently handles booking failures. If a proposed slot is taken while the user is confirming, it will inform the user and offer to find new times.
- **Secure Authentication:** User registration and login are handled via JWT-based authentication.

## 🛠️ Technical Stack

| **Component**           | **Technology** | **Purpose**                                                                 |
|-------------------------|----------------|-----------------------------------------------------------------------------|
| Backend Framework       | FastAPI        | For building a high-performance, asynchronous API.                          |
| Agent Framework         | LangGraph      | To create a stateful, cyclic, and reliable AI agent with complex logic.     |
| LLM Orchestration       | LangChain      | For integrating with LLMs and managing agent tools.                         |
| Database                | MongoDB        | A flexible NoSQL database for storing user and event data.                  |
| Frontend                | Streamlit      | To create a simple and effective real-time chat interface.                  |
| Containerization        | Docker         | For packaging the backend application for consistent deployment.            |

## 🏗️ Architectural Deep Dive

This project was designed with a professional, scalable, and maintainable architecture, emphasizing a clear separation of concerns.

### Project Structure

The codebase is organized into distinct modules, each with a specific responsibility:

- **`api/`**: Contains FastAPI routers and API endpoint definitions.
- **`agent/`**: Implements the core AI agent logic, tools, and LangGraph prompts.
- **`core/`**: Includes global configurations, security settings, and application-wide utilities.
- **`database/`**: Manages database connection setup and interaction.
- **`dependencies/`**: Contains FastAPI-specific dependency injection logic.
- **`services/`**: Encapsulates the business logic, decoupling the API layer from data access.
- **`schemas/`**: Defines Pydantic models for data validation and serialization.
- **`main.py`**: The FastAPI application entry point that ties everything together.

This structure ensures that the API layer, business logic, and agent reasoning are all decoupled, making the system easier to test, debug, and extend.


### Key Technical Decisions

- **Concurrency Handling:** A significant focus was placed on building a system that could handle real-world scheduling conflicts. The `confirm_and_book_event` and `update_event` tools use a robust check-then-write pattern with configurable buffer logic to ensure data integrity and prevent double-bookings.
- **Agent Persona & Prompt Engineering:** The agent's personality is carefully crafted through a detailed system prompt to be professional, futuristic, and helpful, reflecting the Helion Energy brand. The prompt also contains explicit instructions for complex workflows, such as recovering from booking failures and handling users with unknown timezones.
- **Decoupled Services:** The architecture utilizes a Dependency Injection pattern via the `ServiceProvider`. This centralizes the instantiation of services (like `AuthService`, `UserService`, `CalendarService`) and makes the system highly testable by allowing for easy mocking of dependencies.

## ⚙️ Running the Project Locally

You can run the entire application stack locally using Docker and Docker Compose.

### Prerequisites

- Docker and Docker Compose installed.
- A MongoDB instance (local or a free cloud instance like MongoDB Atlas).
- Google Calendar API credentials.

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/purushothdl/booking-agent-proto
   cd booking-agent-proto
   ```

2. **Create the environment file:**

   Create a `.env` file in the project root by copying the example:

   ```bash
   cp .env.example .env
   ```

3. **Configure your environment:**

   Open the `.env` file and fill in the required values:

   - `MONGO_URI`: Your MongoDB connection string.
   - `DATABASE_NAME`: Name of the MongoDB database.
   - `GOOGLE_CREDENTIALS_BASE64`: Your base64-encoded Google service account credentials JSON.
   - `CALENDAR_ID`: The ID of the Google Calendar to book events on.
   - `GOOGLE_API_KEY`: Google API key for calendar access.
   - `JWT_SECRET_KEY`: Secret key for JWT token generation.
   - `JWT_ALGORITHM`: Algorithm used for JWT token signing (default: `HS256`).
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiry time for JWT tokens (default: `60`).
   - `COMPANY_TIMEZONE`: Timezone for the company (default: `Asia/Kolkata`).
   - `COMPANY_WORKING_HOURS`: Working hours for the company (default: `10:00 AM to 6:00 PM`).
   - `MEETING_BUFFER_MINUTES`: Buffer time between meetings (default: `15`).
   - Your GEMINI API Key or other LLM provider keys.

4. **Build and run with Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   The `.env` file will be automatically loaded by Docker Compose, and the environment variables will be available to the application.

5. **Access the applications:**

   - **Backend API:** http://localhost:8000
   - **API Docs (Swagger UI):** http://localhost:8000/docs
   - **Streamlit Frontend:** http://localhost:8501

## 🔮 Future Work & Potential Enhancements

While this implementation fulfills the core requirements, here are the next logical steps for evolving it into a production-grade service:

- **Database-Backed Chat History:** Persisting conversations would allow users to resume interactions across sessions and would enable future features like conversation summarization.
- **User-Managed Availability:** A future version could allow team members to log in and set their own custom availability schedules, providing more granular control over the booking process.
- **Comprehensive Test Suite:** Expanding the `tests/` directory with more unit and integration tests to cover all critical business logic and tool functionalities.