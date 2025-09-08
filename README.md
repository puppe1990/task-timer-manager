# Task Timer Manager

A comprehensive Python terminal application for managing tasks with time tracking capabilities. This application allows you to create, view, update, and delete tasks while tracking estimated vs. actual time spent, categorizing tasks, setting deadlines, and monitoring progress.

## Features

### Core Functionality
- **Task Management**: Create, read, update, and delete tasks
- **Time Tracking**: Track estimated vs. actual time spent on tasks
- **Task Categorization**: Organize tasks by custom categories
- **Deadline Management**: Set and track task deadlines with overdue detection
- **Progress Tracking**: Monitor task completion status and progress percentages
- **Data Persistence**: Save and load tasks from JSON file

### Advanced Features
- **Status Management**: Track task status (Not Started, In Progress, Completed, On Hold)
- **Overdue Detection**: Automatically identify overdue tasks
- **Statistics Dashboard**: View comprehensive task statistics and completion rates
- **Category Filtering**: Filter and view tasks by category
- **Status Filtering**: Filter and view tasks by status
- **Time Efficiency Tracking**: Compare estimated vs. actual time spent

## Installation

1. **Clone or download** this repository to your local machine
2. **Ensure Python 3.6+** is installed on your system
3. **No additional dependencies** required - uses only Python standard library

## Usage

### Running the Application

```bash
python task_manager.py
```

### Main Menu Options

1. **View All Tasks** - Display all tasks with detailed information
2. **Add New Task** - Create a new task with title, description, category, estimated hours, and deadline
3. **Update Task** - Modify existing task properties
4. **Delete Task** - Remove a task from the system
5. **Add Time to Task** - Log actual time spent on a task
6. **View Tasks by Category** - Filter tasks by category
7. **View Tasks by Status** - Filter tasks by status
8. **View Overdue Tasks** - Display all overdue tasks
9. **View Statistics** - Show comprehensive task statistics
10. **Exit** - Close the application

### Task Properties

Each task includes:
- **ID**: Unique identifier (auto-generated)
- **Title**: Task name (required)
- **Description**: Detailed task description (optional)
- **Category**: Task category for organization (default: "General")
- **Estimated Hours**: Expected time to complete (default: 0)
- **Actual Hours**: Time actually spent (tracked via time logging)
- **Deadline**: Due date in YYYY-MM-DD format (optional)
- **Status**: Current task status
- **Created/Updated Timestamps**: Automatic tracking
- **Progress Percentage**: Calculated from actual vs. estimated time

### Data Storage

Tasks are automatically saved to `tasks.json` in the application directory. The file is created automatically on first use and updated whenever tasks are modified.

## Example Usage

### Creating a Task
```
1. Select "Add New Task" from main menu
2. Enter task title: "Complete project documentation"
3. Enter description: "Write comprehensive README and API docs"
4. Enter category: "Documentation"
5. Enter estimated hours: 8.0
6. Enter deadline: 2024-01-15
```

### Adding Time to a Task
```
1. Select "Add Time to Task" from main menu
2. Choose task from the list
3. Enter hours to add: 2.5
4. Time is automatically added to the task's actual hours
```

### Viewing Statistics
The statistics view shows:
- Total number of tasks
- Completed tasks count
- Overdue tasks count
- Completion rate percentage
- Total estimated vs. actual hours
- Time efficiency percentage

## File Structure

```
task-timer-manager/
├── task_manager.py      # Main application file
├── tasks.json          # Data storage file (created automatically)
├── requirements.txt    # Dependencies (none required)
└── README.md          # This documentation
```

## Technical Details

### Task Class
- Encapsulates all task properties and methods
- Handles time tracking and status updates
- Provides progress calculation and overdue detection
- Supports JSON serialization/deserialization

### TaskManager Class
- Manages collection of tasks
- Handles data persistence (JSON file)
- Provides filtering and statistics methods
- Implements CRUD operations

### Data Persistence
- Uses JSON format for human-readable storage
- Automatic loading on startup
- Automatic saving on modifications
- Error handling for corrupted data files

## Error Handling

The application includes comprehensive error handling for:
- Invalid date formats
- Invalid numeric inputs
- File I/O errors
- JSON parsing errors
- Invalid task selections

## Future Enhancements

Potential improvements could include:
- Export/import functionality
- Task templates
- Recurring tasks
- Time reporting by date ranges
- Integration with external calendar systems
- Command-line arguments for batch operations

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.
