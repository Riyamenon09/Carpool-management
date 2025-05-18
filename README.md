🚗 Carpooling Web Application | Flask & SQLite

This is a full-stack web app built to make carpooling easier and more efficient. Using **Flask (Python)** for the backend and **SQLite** for data storage, it let users sign up, log in, book rides, and view their ride history — all within a clean and user-friendly interface.

---

🔧 Key Features

👤 User Registration & Login

* Users can create accounts with secure, hashed passwords.
* The app uses session-based login to keep users signed in across pages.

 🚙 Ride Management

* Users can browse a list of available vehicles.
* Rides can be booked directly through the app, and each user has access to their own booking history.

 🗄️ Database Integration

* All user, vehicle, and booking data is stored and managed using SQLite.
* The database is optimized for fast, reliable access and easy scalability.

🎨 User Interface

* The UI is built with Flask’s Jinja2 templating engine, offering a responsive and dynamic experience.
* Key pages include: Home, Register, Login, Dashboard, Vehicles, and About.

🔐 Security

* Passwords are securely hashed using Werkzeug.
* Sessions are safely managed with Flask's built-in features to protect user data.

