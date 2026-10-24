
/* 1. DAILY TASK PLANNER */

const taskInput = document.getElementById("taskInput");
const addTaskBtn = document.getElementById("addTaskBtn");
const taskList = document.getElementById("taskList");

let completedCount = 0;

function updateProgress() {
    const tasks = taskList.querySelectorAll("li");
    const totalTasks = tasks.length;

    completedCount = taskList.querySelectorAll(
        ".task-checkbox:checked"
    ).length;

    const percentage = totalTasks === 0
        ? 0
        : Math.round((completedCount / totalTasks) * 100);

    document.getElementById("completedTasks").textContent =
        completedCount;

    document.getElementById("taskProgress").value = percentage;

    document.getElementById("progressPercent").textContent =
        percentage;
}

function addTask() {
    const taskName = taskInput.value.trim();

    if (taskName === "") {
        alert("Please enter a task!");
        return;
    }

    const li = document.createElement("li");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-checkbox";
    checkbox.style.width = "auto";
    checkbox.style.marginRight = "10px";

    const taskText = document.createElement("span");
    taskText.textContent = taskName;

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.style.marginLeft = "12px";

    checkbox.addEventListener("change", function () {
        taskText.style.textDecoration = checkbox.checked
            ? "line-through"
            : "none";

        updateProgress();
    });

    deleteBtn.addEventListener("click", function () {
        li.remove();
        updateProgress();
    });

    li.appendChild(checkbox);
    li.appendChild(taskText);
    li.appendChild(deleteBtn);

    taskList.appendChild(li);

    taskInput.value = "";
    updateProgress();
}

addTaskBtn.addEventListener("click", addTask);

taskInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        addTask();
    }
});


/* 2. REMINDER SYSTEM */

const reminderForm = document.getElementById("reminderForm");
const reminderText = document.getElementById("reminderText");
const reminderTime = document.getElementById("reminderTime");
const reminderList = document.getElementById("reminderList");

let reminders = [];

reminderForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const name = reminderText.value.trim();
    const time = new Date(reminderTime.value);
    const now = new Date();

    if (name === "") {
        alert("Please enter a reminder name.");
        return;
    }

    if (Number.isNaN(time.getTime()) || time <= now) {
        alert("Please select a future date and time.");
        return;
    }

    const reminder = {
        id: Date.now(),
        name: name,
        time: time.getTime(),
        notified: false
    };

    reminders.push(reminder);

    const li = document.createElement("li");
    li.textContent = name + " — " + time.toLocaleString();

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.style.marginLeft = "12px";

    deleteBtn.addEventListener("click", function () {
        reminders = reminders.filter(function (item) {
            return item.id !== reminder.id;
        });

        li.remove();
    });

    li.appendChild(deleteBtn);
    reminderList.appendChild(li);

    reminderForm.reset();
});

function checkReminders() {
    const now = Date.now();

    reminders.forEach(function (reminder) {
        if (!reminder.notified && now >= reminder.time) {
            reminder.notified = true;
            alert("Reminder: " + reminder.name);
        }
    });
}

setInterval(checkReminders, 1000);
