# ChronoTask Prototype

ChronoTask is a Python-based productivity and task management application designed to help users organize tasks, manage time, and improve productivity through an interactive desktop interface.

The project combines task management, scheduling, time-management tools, and additional productivity features into one application. It was developed using Python and applies Object-Oriented Programming (OOP) concepts to organize the application's different components and features.

---

## Features

### Calendar and Task Management

- View tasks through a calendar interface
- Add and manage tasks
- Organize tasks by date
- Visual task indicators on the calendar
- Priority-based task organization

### Priority Matrix

The Priority Matrix helps users organize tasks based on importance and urgency, making it easier to determine which tasks should be completed first.

### Chrono Clock

Chrono Clock provides time-management tools for completing tasks.

Features include:

- Digital clock
- Timer
- FIFO (First In, First Out) task queue
- Draggable interface
- Resizable interface
- Tasks can return to the main application when the Chrono Clock is closed

### ChronoK

ChronoK is one of ChronoTask's productivity features designed to assist users with organizing and managing activities within the application.

### Koyomi

Koyomi provides additional scheduling and productivity functionality that works alongside the main ChronoTask system.

### Shamisen

Shamisen is an additional feature integrated into the ChronoTask application.

### Customization

- Application settings
- Theme changing
- Persistent user data and preferences

---

## Object-Oriented Programming

ChronoTask was developed using Object-Oriented Programming (OOP) principles.

The application separates its functionality into different classes and modules instead of placing all functionality inside a single program.

### OOP Concepts Used

#### Classes and Objects

Different parts of ChronoTask are represented using classes. Objects are created from these classes to control the application's interfaces and functionality.

#### Encapsulation

Related data and methods are grouped inside their appropriate classes. This helps keep the program organized and separates different responsibilities.

#### Inheritance

Some interface components inherit functionality from PySide6/Qt classes and extend them with functionality required by ChronoTask.

#### Abstraction

Complex operations such as task management, database operations, timers, and interface behavior are separated into methods and classes.

#### Modularity

ChronoTask separates major features into different Python files and modules, making the source code easier to understand, maintain, debug, and extend.

---

## Technologies Used

- Python
- PySide6 / Qt
- SQLite
- Object-Oriented Programming (OOP)
- Git
- GitHub

---

## Project Structure

The repository contains the source code required to run and understand the ChronoTask prototype.

Major parts of the project include:

- Main ChronoTask application
- Calendar and task system
- Priority Matrix
- Chrono Clock
- ChronoK
- Koyomi
- Shamisen
- Settings and theme system
- Database and data files
- Supporting resources and assets

---

## Setup Instructions

### 1. Download the Project

Clone or download the ChronoTask repository from GitHub.

If using Git:

```bash
git clone YOUR-REPOSITORY-URL
```

Open the downloaded project folder.

### 2. Install Python

Make sure Python is installed on the computer before running the source code.

### 3. Install Required Dependencies

Open a terminal inside the ChronoTask project folder.

If the project contains a `requirements.txt` file, run:

```bash
pip install -r requirements.txt
```

### 4. Run ChronoTask

Run the main Python file:

```bash
python main.py
```

The exact main Python filename may differ depending on the final project structure.

---

## Data Persistence

ChronoTask uses local data storage to preserve application information between sessions.

This allows information such as tasks and other application data to remain available after the application is closed and opened again.

---

## Purpose of the Prototype

The ChronoTask Prototype was developed to demonstrate how task management, scheduling, time-management tools, and productivity features can be combined into a single desktop application.

The project also demonstrates the practical application of Object-Oriented Programming in the development of a modular desktop application.

---

## Testing

This repository contains the latest working version of the ChronoTask prototype and can be used for application testing and evaluation.

Testers can explore features such as:

- Creating and managing tasks
- Calendar navigation
- Task prioritization
- Priority Matrix
- Chrono Clock
- ChronoK
- Koyomi
- Shamisen
- Application customization
- Data persistence

---

## Project Status

**ChronoTask Prototype**

The application is currently intended for prototype testing, demonstration, and academic evaluation.
