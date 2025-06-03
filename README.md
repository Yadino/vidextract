# VidExtract

**AI-Based Video Description Extractor**

VidExtract is a full-stack application that allows users to upload videos and extract meaningful descriptions of their visual and audio content using various AI models. The extracted information is stored in a searchable database, enabling users to chat with an AI assistant to retrieve relevant moments from the video.

## Project Structure

The project is organized into three main components:

### 1. Video Analyzer (`video_analyzer` directory)

This is the core processing unit responsible for analyzing the uploaded videos. It utilizes a combination of powerful AI models to understand the video content:

- **Visual Analysis:**
  - **YOLOv8:** Used for object detection within video frames, identifying and locating various objects present in the scenes.
  - **BLIP:** Employed for scene captioning, generating descriptive text summaries of the visual content in different segments of the video.

- **Audio Analysis:**
  - **OpenAI Whisper:** Transcribes spoken English language from the audio track into text.
  - **YAMNET:** Detects various sound events and effects present in the audio.

The video analyzer processes the video, combines the insights from these models, and generates structured information about key moments, including timestamps and descriptions. This information is then passed to the API for storage.

### 2. API (`api` directory)

The API serves as the backend of the application. It is built using FastAPI and handles:

- Receiving video uploads from the client.
- Interacting with the `video_analyzer` to process videos.
- Storing the extracted event data in a PostgreSQL database with the `pgvector` extension for semantic search capabilities.
- Providing a chat endpoint that allows the client to query the database using natural language.
- Utilizing OpenAI embeddings for semantic search to find video moments relevant to user queries.

### 3. Client (`client` directory)

The client is a single-page application built with React and TypeScript, using Material UI for the user interface. It provides the user interface for:

- Uploading videos via a drag-and-drop interface.
- Displaying the status of video analysis (uploading, analyzing, saving).
- Providing a chat interface to interact with the AI assistant and retrieve video highlights based on queries or display all extracted moments.

## Deployment with Docker Compose

The application can be easily deployed using Docker Compose, which sets up the client, API, and database services in separate containers.

**Prerequisites:**

- Docker Desktop (or Docker Engine and Docker Compose) installed on your system.

**Instructions:**

1.  **Navigate to the project root:** Open your terminal or command prompt and navigate to the root directory of the `vidextract` project (where the `compose.yaml` file is located).

2.  **Build and run the containers:** Execute the following command:

    ```bash
    docker compose up --build
    ```

    -   `docker compose up`: Starts the services defined in `compose.yaml`.
    -   `--build`: Builds the Docker images before starting the containers (useful for the first run or after code changes).

3.  **Access the application:** Once the containers are running, open your web browser and go to `http://localhost:3000`. You should see the client application.

4.  **Stopping the application:** To stop the running containers, press `Ctrl+C` in the terminal where `docker compose up` is running. To stop and remove the containers, networks, and volumes, run:

    ```bash
    docker compose down
    ```

This setup provides a convenient and isolated environment to run the VidExtract application.
