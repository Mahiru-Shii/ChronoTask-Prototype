ChronoTask Prototype
ChronoTask is a Python-based productivity and task management application designed to help users organize tasks, manage time, and improve productivity through an interactive desktop interface.

The project combines task management, scheduling, time-management tools, and additional productivity features into one application. It was developed using Python and applies Object-Oriented Programming (OOP) concepts to organize the application's different components and features.

Features
Calendar and Task Management
View tasks through a calendar interface
Add and manage tasks
Organize tasks by date
Visual task indicators on the calendar
Priority-based task organization
Priority Matrix
Tasks can be organized based on their importance and urgency, helping users determine which tasks should be completed first.

Chrono Clock
Chrono Clock provides time-management tools for completing tasks.

Features include:

Digital clock
Timer
FIFO (First In, First Out) task queue
Draggable and resizable interface
Tasks can return to the main application when the Chrono Clock window is closed
ChronoK
ChronoK is one of ChronoTask's productivity features designed to assist users with organizing and managing their activities within the application.

Koyomi
Koyomi provides additional scheduling and productivity functionality that works alongside the main ChronoTask system.

Shamisen
Shamisen provides an additional application feature integrated into the ChronoTask environment.

Customization
Application settings
Theme changing
Persistent user data and preferences
Object-Oriented Programming
ChronoTask was developed using Object-Oriented Programming (OOP) principles.

The application separates its functionality into different classes and modules instead of placing all functionality inside a single program.

OOP Concepts Used
Classes and Objects
Different parts of ChronoTask are represented using classes. Objects are created from these classes to control the application's interfaces and functionality.

Encapsulation
Related data and methods are grouped inside their appropriate classes. This keeps the program organized and prevents unrelated components from directly controlling internal functionality.

Inheritance
Some interface components inherit functionality from existing PySide6/Qt classes and extend those classes with functionality required by ChronoTask.

Abstraction
Complex operations such as task management, database operations, timers, and interface behavior are separated into methods and classes so other parts of the program can use them without needing to know every implementation detail.

Modularity
ChronoTask separates major features into different Python files and modules, making the source code easier to understand, maintain, debug, and extend.

Technologies Used
Python
PySide6 / Qt
SQLite
Object-Oriented Programming (OOP)
Git and GitHub
Project Structure
The repository contains the source code required to run and understand the ChronoTask prototype.

Major parts of the project include:

Main ChronoTask application
Calendar and task system
Chrono Clock
ChronoK
Koyomi
Shamisen
Settings and theme system
Database and data files
Supporting resources and assets
Setup Instructions
Requirements
To run ChronoTask from the Python source code, make sure Python is installed on the computer.

1. Clone the Repository
Clone or download this repository:

git clone

Then open the project folder.

2. Install Required Dependencies
Open a terminal inside the project directory and install the required Python packages.

If the project contains a requirements.txt file:

pip install -r requirements.txt

3. Run ChronoTask
Run the main Python file of the project:

python main.py

Note: The exact main file name may differ depending on the final project structure.

Data Persistence
ChronoTask uses local data storage to preserve application information between sessions.

This allows information such as tasks and other application data to remain available after the application is closed and opened again.

Purpose of the Prototype
The ChronoTask Prototype was developed to demonstrate how task management, scheduling, time-management tools, and productivity features can be combined into a single desktop application.

The prototype also demonstrates the practical use of Object-Oriented Programming in building a modular desktop application.

Testing
This repository contains the latest working version of the ChronoTask prototype and can be used for application testing and evaluation.

Testers can explore the application's major features, including:

Creating and managing tasks
Calendar navigation
Task prioritization
Chrono Clock
ChronoK
Koyomi
Shamisen
Application customization
Data persistence
Project Status
ChronoTask Prototype

The application is currently intended for prototype testing, demonstration, and academic evaluation.
