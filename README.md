# Real-Time Chat Application

## Overview
This project is a real-time chat application built using Django Channels and WebSockets. It enables seamless and secure communication with end-to-end encryption while efficiently managing concurrent connections with Channels Redis. Additionally, it features a unique and exclusive live message preview system that enhances user interaction and privacy.

## Features
- **Real-Time Messaging:** Instant message sending and receiving using WebSockets.
- **End-to-End Encryption:** Ensuring secure communication between users.
- **Live Message Preview:** Users can preview messages while typing before sending, visible only in real-time.
- **User-Controlled Preview Toggle:** Users can enable or disable the message preview feature based on their preference.
- **Scalable Architecture:** Utilizes Django Channels and Redis for handling multiple concurrent connections efficiently.

## Technologies Used
- **Backend:** Django, Django Channels, Django Rest Framework
- **WebSockets:** Django Channels WebSockets
- **Message Broker:** Redis
- **Database:** PostgreSQL (or SQLite for development)
- **Frontend:** HTML, CSS, JavaScript (AJAX for asynchronous operations)

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Redis Server
- PostgreSQL (or SQLite for local testing)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chat-app.git
   cd chat-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables and update `settings.py` accordingly.

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start Redis server:
   ```bash
   redis-server
   ```

7. Start Django server:
   ```bash
   python manage.py runserver
   ```

8. Run Django Channels worker:
   ```bash
   daphne -b 0.0.0.0 -p 8001 chatapp.asgi:application
   ```

## Usage
1. Register or log in to access the chat interface.
2. Find users by their username and start a conversation with them.
3. Use the live message preview toggle to enable/disable message previews while typing.
4. Enjoy real-time, encrypted messaging.

## Future Enhancements
- **Group Chat Support**
- **File Sharing & Media Support**
- **Push Notifications**
- **UI Improvements For More Features**

## License
This project is licensed under the MIT License.

---
For any inquiries or contributions, feel free to submit a pull request or open an issue!

