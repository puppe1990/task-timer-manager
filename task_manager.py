#!/usr/bin/env python3
"""
Task Timer Manager - A Python terminal application for managing tasks with time tracking.
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys


class Task:
    """Represents a single task with time tracking capabilities."""
    
    def __init__(self, title: str, description: str = "", project: str = "General", 
                 category: str = "General", estimated_hours: float = 0.0, deadline: Optional[str] = None):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.project = project
        self.category = category
        self.estimated_hours = estimated_hours
        self.actual_hours = 0.0
        self.deadline = deadline
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.status = "Not Started"  # Not Started, In Progress, Completed, On Hold
        self.completed_at = None
        self.timer_start_time = None
        self.timer_running = False
        self.session_time = 0.0  # Time accumulated in current session
        
    def _generate_id(self) -> str:
        """Generate a unique ID for the task."""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def add_time(self, hours: float) -> None:
        """Add actual time spent on the task."""
        if hours > 0:
            self.actual_hours += hours
            self.updated_at = datetime.now().isoformat()
    
    def start_timer(self) -> bool:
        """Start the timer for this task."""
        if not self.timer_running:
            self.timer_start_time = time.time()
            self.timer_running = True
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def stop_timer(self) -> float:
        """Stop the timer and return the elapsed time in hours."""
        if self.timer_running and self.timer_start_time:
            elapsed_time = time.time() - self.timer_start_time
            elapsed_hours = elapsed_time / 3600.0  # Convert seconds to hours
            self.session_time += elapsed_hours
            self.actual_hours += elapsed_hours
            self.timer_running = False
            self.timer_start_time = None
            self.updated_at = datetime.now().isoformat()
            return elapsed_hours
        return 0.0
    
    def restart_timer(self) -> float:
        """Restart the timer (stop current session and start new one)."""
        elapsed = self.stop_timer()
        self.start_timer()
        return elapsed
    
    def get_current_session_time(self) -> float:
        """Get the time elapsed in the current session."""
        if self.timer_running and self.timer_start_time:
            current_elapsed = time.time() - self.timer_start_time
            return (self.session_time + current_elapsed / 3600.0)
        return self.session_time
    
    def get_total_time(self) -> float:
        """Get total time including current session."""
        if self.timer_running and self.timer_start_time:
            current_elapsed = time.time() - self.timer_start_time
            return self.actual_hours + (current_elapsed / 3600.0)
        return self.actual_hours
    
    def update_status(self, status: str) -> None:
        """Update the task status."""
        valid_statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
        if status in valid_statuses:
            self.status = status
            self.updated_at = datetime.now().isoformat()
            if status == "Completed":
                self.completed_at = datetime.now().isoformat()
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.deadline or self.status == "Completed":
            return False
        try:
            deadline_date = datetime.fromisoformat(self.deadline)
            return datetime.now() > deadline_date
        except ValueError:
            return False
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage based on time spent vs estimated time."""
        if self.estimated_hours == 0:
            return 0.0
        total_time = self.get_total_time()
        return min(100.0, (total_time / self.estimated_hours) * 100)
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project': self.project,
            'category': self.category,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'deadline': self.deadline,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'completed_at': self.completed_at,
            'timer_running': self.timer_running,
            'session_time': self.session_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create a Task instance from a dictionary."""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            project=data.get('project', 'General'),
            category=data.get('category', 'General'),
            estimated_hours=data.get('estimated_hours', 0.0),
            deadline=data.get('deadline')
        )
        task.id = data['id']
        task.actual_hours = data.get('actual_hours', 0.0)
        task.created_at = data.get('created_at', datetime.now().isoformat())
        task.updated_at = data.get('updated_at', datetime.now().isoformat())
        task.status = data.get('status', 'Not Started')
        task.completed_at = data.get('completed_at')
        task.timer_running = data.get('timer_running', False)
        task.session_time = data.get('session_time', 0.0)
        # Reset timer state when loading from file
        task.timer_start_time = None
        return task
    
    def __str__(self) -> str:
        """String representation of the task."""
        overdue_indicator = " (OVERDUE)" if self.is_overdue() else ""
        timer_indicator = " [TIMER RUNNING]" if self.timer_running else ""
        progress = self.get_progress_percentage()
        total_time = self.get_total_time()
        return f"[{self.id}] {self.title} - {self.status}{overdue_indicator}{timer_indicator}\n" \
               f"  Project: {self.project} | Category: {self.category}\n" \
               f"  Estimated: {self.estimated_hours}h | Actual: {total_time:.2f}h | Progress: {progress:.1f}%\n" \
               f"  Deadline: {self.deadline or 'No deadline'}\n" \
               f"  Description: {self.description}"


class TaskManager:
    """Manages a collection of tasks with persistence."""
    
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self) -> None:
        """Load tasks from the JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []
    
    def save_tasks(self) -> None:
        """Save tasks to the JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, task: Task) -> None:
        """Add a new task."""
        self.tasks.append(task)
        self.save_tasks()
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task with new values."""
        task = self.get_task_by_id(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now().isoformat()
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False
    
    def get_tasks_by_project(self, project: str) -> List[Task]:
        """Get all tasks in a specific project."""
        return [task for task in self.tasks if task.project.lower() == project.lower()]
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get all tasks in a specific category."""
        return [task for task in self.tasks if task.category.lower() == category.lower()]
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks if task.status.lower() == status.lower()]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [task for task in self.tasks if task.is_overdue()]
    
    def get_all_projects(self) -> List[str]:
        """Get all unique projects."""
        projects = set(task.project for task in self.tasks)
        return sorted(list(projects))
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set(task.category for task in self.tasks)
        return sorted(list(categories))
    
    def get_running_timers(self) -> List[Task]:
        """Get all tasks with running timers."""
        return [task for task in self.tasks if task.timer_running]
    
    def stop_all_timers(self) -> None:
        """Stop all running timers."""
        for task in self.tasks:
            if task.timer_running:
                task.stop_timer()
        self.save_tasks()
    
    def get_statistics(self) -> Dict:
        """Get task statistics."""
        total_tasks = len(self.tasks)
        completed_tasks = len(self.get_tasks_by_status("Completed"))
        overdue_tasks = len(self.get_overdue_tasks())
        running_timers = len(self.get_running_timers())
        total_estimated_hours = sum(task.estimated_hours for task in self.tasks)
        total_actual_hours = sum(task.get_total_time() for task in self.tasks)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'running_timers': running_timers,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }


def main():
    """Main application entry point."""
    print("=" * 60)
    print("           TASK TIMER MANAGER")
    print("=" * 60)
    
    task_manager = TaskManager()
    
    while True:
        print("\n" + "=" * 40)
        print("MAIN MENU")
        print("=" * 40)
        print("1. View All Tasks")
        print("2. Add New Task")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Add Time to Task")
        print("6. Start Timer")
        print("7. Stop Timer")
        print("8. Restart Timer")
        print("9. View Running Timers")
        print("10. View Tasks by Project")
        print("11. View Tasks by Category")
        print("12. View Tasks by Status")
        print("13. View Overdue Tasks")
        print("14. View Statistics")
        print("15. Exit")
        
        choice = input("\nEnter your choice (1-15): ").strip()
        
        if choice == '1':
            view_all_tasks(task_manager)
        elif choice == '2':
            add_new_task(task_manager)
        elif choice == '3':
            update_task(task_manager)
        elif choice == '4':
            delete_task(task_manager)
        elif choice == '5':
            add_time_to_task(task_manager)
        elif choice == '6':
            start_timer(task_manager)
        elif choice == '7':
            stop_timer(task_manager)
        elif choice == '8':
            restart_timer(task_manager)
        elif choice == '9':
            view_running_timers(task_manager)
        elif choice == '10':
            view_tasks_by_project(task_manager)
        elif choice == '11':
            view_tasks_by_category(task_manager)
        elif choice == '12':
            view_tasks_by_status(task_manager)
        elif choice == '13':
            view_overdue_tasks(task_manager)
        elif choice == '14':
            view_statistics(task_manager)
        elif choice == '15':
            print("\nThank you for using Task Timer Manager!")
            break
        else:
            print("Invalid choice. Please try again.")


def view_all_tasks(task_manager: TaskManager) -> None:
    """Display all tasks."""
    if not task_manager.tasks:
        print("\nNo tasks found.")
        return
    
    print(f"\n{'='*60}")
    print(f"ALL TASKS ({len(task_manager.tasks)} total)")
    print(f"{'='*60}")
    
    for i, task in enumerate(task_manager.tasks, 1):
        print(f"\n{i}. {task}")


def add_new_task(task_manager: TaskManager) -> None:
    """Add a new task."""
    print("\n" + "="*40)
    print("ADD NEW TASK")
    print("="*40)
    
    title = input("Enter task title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return
    
    description = input("Enter task description (optional): ").strip()
    project = input("Enter project name (default: General): ").strip() or "General"
    category = input("Enter category (default: General): ").strip() or "General"
    
    try:
        estimated_hours = float(input("Enter estimated hours: ") or "0")
    except ValueError:
        print("Invalid hours format. Using 0 hours.")
        estimated_hours = 0.0
    
    deadline = input("Enter deadline (YYYY-MM-DD, optional): ").strip()
    if deadline:
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Ignoring deadline.")
            deadline = None
    
    task = Task(title, description, project, category, estimated_hours, deadline)
    task_manager.add_task(task)
    print(f"\nTask '{title}' added successfully to project '{project}' with ID: {task.id}")


def update_task(task_manager: TaskManager) -> None:
    """Update an existing task."""
    if not task_manager.tasks:
        print("\nNo tasks found.")
        return
    
    print("\n" + "="*40)
    print("UPDATE TASK")
    print("="*40)
    
    # Show available tasks
    print("Available tasks:")
    for i, task in enumerate(task_manager.tasks, 1):
        print(f"{i}. [{task.id}] {task.title}")
    
    try:
        task_index = int(input("\nEnter task number to update: ")) - 1
        if 0 <= task_index < len(task_manager.tasks):
            task = task_manager.tasks[task_index]
            print(f"\nUpdating task: {task.title}")
            
            # Update fields
            new_title = input(f"Enter new title (current: {task.title}): ").strip()
            if new_title:
                task.title = new_title
            
            new_description = input(f"Enter new description (current: {task.description}): ").strip()
            if new_description:
                task.description = new_description
            
            new_project = input(f"Enter new project (current: {task.project}): ").strip()
            if new_project:
                task.project = new_project
            
            new_category = input(f"Enter new category (current: {task.category}): ").strip()
            if new_category:
                task.category = new_category
            
            new_estimated = input(f"Enter new estimated hours (current: {task.estimated_hours}): ").strip()
            if new_estimated:
                try:
                    task.estimated_hours = float(new_estimated)
                except ValueError:
                    print("Invalid hours format. Keeping current value.")
            
            new_status = input(f"Enter new status (current: {task.status}): ").strip()
            if new_status:
                task.update_status(new_status)
            
            new_deadline = input(f"Enter new deadline (current: {task.deadline or 'None'}): ").strip()
            if new_deadline:
                try:
                    datetime.strptime(new_deadline, "%Y-%m-%d")
                    task.deadline = new_deadline
                except ValueError:
                    print("Invalid date format. Keeping current deadline.")
            
            task_manager.save_tasks()
            print("Task updated successfully!")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def delete_task(task_manager: TaskManager) -> None:
    """Delete a task."""
    if not task_manager.tasks:
        print("\nNo tasks found.")
        return
    
    print("\n" + "="*40)
    print("DELETE TASK")
    print("="*40)
    
    # Show available tasks
    print("Available tasks:")
    for i, task in enumerate(task_manager.tasks, 1):
        print(f"{i}. [{task.id}] {task.title}")
    
    try:
        task_index = int(input("\nEnter task number to delete: ")) - 1
        if 0 <= task_index < len(task_manager.tasks):
            task = task_manager.tasks[task_index]
            confirm = input(f"Are you sure you want to delete '{task.title}'? (y/N): ").strip().lower()
            if confirm == 'y':
                task_manager.delete_task(task.id)
                print("Task deleted successfully!")
            else:
                print("Deletion cancelled.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def add_time_to_task(task_manager: TaskManager) -> None:
    """Add time spent to a task."""
    if not task_manager.tasks:
        print("\nNo tasks found.")
        return
    
    print("\n" + "="*40)
    print("ADD TIME TO TASK")
    print("="*40)
    
    # Show available tasks
    print("Available tasks:")
    for i, task in enumerate(task_manager.tasks, 1):
        print(f"{i}. [{task.id}] {task.title} (Current: {task.actual_hours}h)")
    
    try:
        task_index = int(input("\nEnter task number: ")) - 1
        if 0 <= task_index < len(task_manager.tasks):
            task = task_manager.tasks[task_index]
            hours = float(input(f"Enter hours to add to '{task.title}': "))
            if hours > 0:
                task.add_time(hours)
                task_manager.save_tasks()
                print(f"Added {hours} hours to '{task.title}'. Total: {task.actual_hours}h")
            else:
                print("Hours must be positive.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def view_tasks_by_project(task_manager: TaskManager) -> None:
    """View tasks filtered by project."""
    projects = task_manager.get_all_projects()
    if not projects:
        print("\nNo projects found.")
        return
    
    print("\n" + "="*40)
    print("VIEW TASKS BY PROJECT")
    print("="*40)
    print("Available projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project}")
    
    try:
        proj_index = int(input("\nEnter project number: ")) - 1
        if 0 <= proj_index < len(projects):
            project = projects[proj_index]
            tasks = task_manager.get_tasks_by_project(project)
            if tasks:
                print(f"\nTasks in project '{project}':")
                for task in tasks:
                    print(f"\n{task}")
            else:
                print(f"No tasks found in project '{project}'.")
        else:
            print("Invalid project number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def view_tasks_by_category(task_manager: TaskManager) -> None:
    """View tasks filtered by category."""
    categories = task_manager.get_all_categories()
    if not categories:
        print("\nNo categories found.")
        return
    
    print("\n" + "="*40)
    print("VIEW TASKS BY CATEGORY")
    print("="*40)
    print("Available categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    
    try:
        cat_index = int(input("\nEnter category number: ")) - 1
        if 0 <= cat_index < len(categories):
            category = categories[cat_index]
            tasks = task_manager.get_tasks_by_category(category)
            if tasks:
                print(f"\nTasks in category '{category}':")
                for task in tasks:
                    print(f"\n{task}")
            else:
                print(f"No tasks found in category '{category}'.")
        else:
            print("Invalid category number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def view_tasks_by_status(task_manager: TaskManager) -> None:
    """View tasks filtered by status."""
    statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
    
    print("\n" + "="*40)
    print("VIEW TASKS BY STATUS")
    print("="*40)
    print("Available statuses:")
    for i, status in enumerate(statuses, 1):
        print(f"{i}. {status}")
    
    try:
        status_index = int(input("\nEnter status number: ")) - 1
        if 0 <= status_index < len(statuses):
            status = statuses[status_index]
            tasks = task_manager.get_tasks_by_status(status)
            if tasks:
                print(f"\nTasks with status '{status}':")
                for task in tasks:
                    print(f"\n{task}")
            else:
                print(f"No tasks found with status '{status}'.")
        else:
            print("Invalid status number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def view_overdue_tasks(task_manager: TaskManager) -> None:
    """View overdue tasks."""
    overdue_tasks = task_manager.get_overdue_tasks()
    
    print("\n" + "="*40)
    print("OVERDUE TASKS")
    print("="*40)
    
    if overdue_tasks:
        print(f"Found {len(overdue_tasks)} overdue tasks:")
        for task in overdue_tasks:
            print(f"\n{task}")
    else:
        print("No overdue tasks found.")


def view_statistics(task_manager: TaskManager) -> None:
    """View task statistics."""
    stats = task_manager.get_statistics()
    
    print("\n" + "="*40)
    print("TASK STATISTICS")
    print("="*40)
    print(f"Total Tasks: {stats['total_tasks']}")
    print(f"Completed Tasks: {stats['completed_tasks']}")
    print(f"Overdue Tasks: {stats['overdue_tasks']}")
    print(f"Running Timers: {stats['running_timers']}")
    print(f"Completion Rate: {stats['completion_rate']:.1f}%")
    print(f"Total Estimated Hours: {stats['total_estimated_hours']:.1f}")
    print(f"Total Actual Hours: {stats['total_actual_hours']:.1f}")
    
    if stats['total_estimated_hours'] > 0:
        efficiency = (stats['total_actual_hours'] / stats['total_estimated_hours']) * 100
        print(f"Time Efficiency: {efficiency:.1f}%")
    
    # Show project breakdown
    projects = task_manager.get_all_projects()
    if projects:
        print(f"\nProject Breakdown:")
        for project in projects:
            project_tasks = task_manager.get_tasks_by_project(project)
            completed = len([t for t in project_tasks if t.status == "Completed"])
            total_estimated = sum(t.estimated_hours for t in project_tasks)
            total_actual = sum(t.actual_hours for t in project_tasks)
            completion_rate = (completed / len(project_tasks) * 100) if project_tasks else 0
            print(f"  {project}: {len(project_tasks)} tasks, {completed} completed ({completion_rate:.1f}%), {total_estimated:.1f}h estimated, {total_actual:.1f}h actual")


def start_timer(task_manager: TaskManager) -> None:
    """Start a timer for a task."""
    if not task_manager.tasks:
        print("\nNo tasks found.")
        return
    
    # Check if any timers are already running
    running_timers = task_manager.get_running_timers()
    if running_timers:
        print(f"\nWarning: {len(running_timers)} timer(s) are already running:")
        for task in running_timers:
            print(f"  - {task.title}")
        choice = input("\nDo you want to stop all running timers and start a new one? (y/N): ").strip().lower()
        if choice == 'y':
            task_manager.stop_all_timers()
        else:
            return
    
    print("\n" + "="*40)
    print("START TIMER")
    print("="*40)
    print("Available tasks:")
    for i, task in enumerate(task_manager.tasks, 1):
        status_indicator = " [TIMER RUNNING]" if task.timer_running else ""
        print(f"{i}. [{task.id}] {task.title}{status_indicator}")
    
    try:
        task_index = int(input("\nEnter task number: ")) - 1
        if 0 <= task_index < len(task_manager.tasks):
            task = task_manager.tasks[task_index]
            if task.start_timer():
                task_manager.save_tasks()
                print(f"\nTimer started for '{task.title}' at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"Timer is already running for '{task.title}'")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def stop_timer(task_manager: TaskManager) -> None:
    """Stop a timer for a task."""
    running_timers = task_manager.get_running_timers()
    if not running_timers:
        print("\nNo timers are currently running.")
        return
    
    print("\n" + "="*40)
    print("STOP TIMER")
    print("="*40)
    print("Running timers:")
    for i, task in enumerate(running_timers, 1):
        current_time = task.get_current_session_time()
        print(f"{i}. [{task.id}] {task.title} - {current_time:.2f}h")
    
    try:
        timer_index = int(input("\nEnter timer number to stop: ")) - 1
        if 0 <= timer_index < len(running_timers):
            task = running_timers[timer_index]
            elapsed = task.stop_timer()
            task_manager.save_tasks()
            print(f"\nTimer stopped for '{task.title}'")
            print(f"Session time: {elapsed:.2f} hours")
            print(f"Total time: {task.actual_hours:.2f} hours")
        else:
            print("Invalid timer number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def restart_timer(task_manager: TaskManager) -> None:
    """Restart a timer for a task."""
    running_timers = task_manager.get_running_timers()
    if not running_timers:
        print("\nNo timers are currently running.")
        return
    
    print("\n" + "="*40)
    print("RESTART TIMER")
    print("="*40)
    print("Running timers:")
    for i, task in enumerate(running_timers, 1):
        current_time = task.get_current_session_time()
        print(f"{i}. [{task.id}] {task.title} - {current_time:.2f}h")
    
    try:
        timer_index = int(input("\nEnter timer number to restart: ")) - 1
        if 0 <= timer_index < len(running_timers):
            task = running_timers[timer_index]
            elapsed = task.restart_timer()
            task_manager.save_tasks()
            print(f"\nTimer restarted for '{task.title}'")
            print(f"Previous session: {elapsed:.2f} hours")
            print(f"New session started at {datetime.now().strftime('%H:%M:%S')}")
        else:
            print("Invalid timer number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def view_running_timers(task_manager: TaskManager) -> None:
    """View all currently running timers."""
    running_timers = task_manager.get_running_timers()
    
    print("\n" + "="*40)
    print("RUNNING TIMERS")
    print("="*40)
    
    if running_timers:
        print(f"Found {len(running_timers)} running timer(s):")
        for task in running_timers:
            current_time = task.get_current_session_time()
            total_time = task.get_total_time()
            print(f"\n{task}")
            print(f"  Current Session: {current_time:.2f}h")
            print(f"  Total Time: {total_time:.2f}h")
    else:
        print("No timers are currently running.")


if __name__ == "__main__":
    main()
