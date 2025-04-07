
document.addEventListener('DOMContentLoaded', fetchUsers);

document.getElementById('task-form')?.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const taskName = document.getElementById('task-name').value;
    const completion = document.getElementById('completion');
    const dueDate = document.getElementById('due-date').value;
    const taskboardId = document.getElementById('taskboard-id').value;
    const assignedSelect = document.getElementById('assign-to');
    const assignedUsers = Array.from(assignedSelect.selectedOptions).map(option => option.value);

    console.log('taskboardid',taskboardId);
    const taskData = {
        name: taskName,
        completion: 'Pending',
        taskboard_id: taskboardId,
        due_date: dueDate,
        assigned_to: assignedUsers
    };

    const response = await fetch('/createtask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
    });

    const result = await response.json();
    
    if (result.message === "Task created successfully!") {
        alert('Task created!');
        window.location.reload();  
    } else {
        alert('Error creating task');
    }
});


async function fetchUsers() {
    const response = await fetch('/getusers');
    const users = await response.json();

    const userSelect = document.getElementById('assigned-users');
    if(userSelect)
    {
        userSelect.innerHTML = ''; 

        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.email;
            userSelect.appendChild(option);
        });
    }
}
async function fetchAssignedUsers() {
    const response = await fetch('/getassignedusers');
    const users = await response.json();

    console.log('users',users);
    const userSelect = document.getElementById('assigned-users-remove');
    if(userSelect)
    {
        userSelect.innerHTML = ''; 
        if(users &&  users?.users && users?.users?.length>0)
            {
                users?.users?.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user;
                    option.textContent = user;
                    userSelect.appendChild(option);
                });
            }
            else
            {
                const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No User Present';
                    userSelect.appendChild(option);
            }
    }
}
const removeUserButton=document.getElementById('remove-user-btn')
if(removeUserButton)
{
    removeUserButton.addEventListener('click', async function () {
        const userId = document.getElementById('assigned-users-remove').value;
        const taskboardId = document.getElementById('taskboard-id').value;
    
        if (!userId) {
            alert("Please select a user.");
            return;
        }
    
        const response = await fetch(`/remove/${taskboardId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
    
        const result = await response.json();
        alert(result.message);
    
        if (result.message === "User removed successfully") {
            window.location.reload(); 
        }
    });
}

const addUserButton=document.getElementById('add-user-btn')
if(addUserButton)
{
    document.getElementById('add-user-btn').addEventListener('click', async function () {
        const userId = document.getElementById('assigned-users').value;
        const taskboardId = document.getElementById('taskboard-id').value;
    
        if (!userId) {
            alert("Please select a user.");
            return;
        }
    
        const response = await fetch(`/adduser/${taskboardId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
    
        const result = await response.json();
        alert(result.message);
    
        if (result.message === "User added successfully") {
            window.location.reload(); 
        }
    });
    
}

document.querySelectorAll(".completion-checkbox").forEach(checkbox => {
    checkbox.addEventListener("change", async function () {
        const taskId = this.getAttribute("data-task-id");

        if (this.checked) {
            const response = await fetch(`/update-task/${taskId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ completion: "Completed" })
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById(`status-${taskId}`).innerText = "Completed";
                
                let completedAtElement = document.getElementById(`completed-at-${taskId}`);
                
                if (!completedAtElement) {
                    completedAtElement = document.createElement("p");
                    completedAtElement.innerHTML = `<strong>Completed At:</strong> <span id="completed-at-${taskId}"></span>`;
                    this.parentNode.appendChild(completedAtElement); 
                }
                window.location.reload();
                console.log('cmpleted');
                // document.getElementById(`completed-at-${taskId}`).innerText = new Date().toLocaleString(); 

                this.disabled = true; 
            } else {
                alert("Error updating task status.");
            }
        }
    });
});

document.querySelectorAll(".edit-task-btn").forEach(button => {
    button.addEventListener("click", async function () {
        const taskId = this.getAttribute("data-task-id");
        
        const taskName = document.getElementById(`task-name-${taskId}`).innerText;
        const dueDate = document.getElementById(`due-date-${taskId}`).innerText;

        const newTaskName = prompt("Edit Task Name:", taskName);
        const newDueDate = prompt("Edit Due Date (YYYY-MM-DD):", dueDate);

        if (newTaskName && newDueDate) {
            const response = await fetch(`/update-task/${taskId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name: newTaskName, dueDate: newDueDate })
            });

            const result = await response.json();
            if (result.success) {
                document.getElementById(`task-name-${taskId}`).innerText = newTaskName;
                document.getElementById(`due-date-${taskId}`).innerText = newDueDate;
                alert("Task updated successfully!");
            } else {
                alert("Error updating task.");
            }
        }
    });
});
document.querySelectorAll(".delete-task-btn").forEach(button => {
    button.addEventListener("click", async function () {
        const taskId = this.getAttribute("data-task-id");

        if (confirm("Are you sure you want to delete this task?")) {
            const response = await fetch(`/delete-task/${taskId}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" }
            });

            const result = await response.json();
            if (result.success) {
                // document.getElementById(`task-${taskId}`).remove();
                alert("Task deleted successfully!");
                window.location.reload();
            } else {
                alert("Error deleting task.");
            }
        }
    });
});
fetchUsers();
fetchAssignedUsers();