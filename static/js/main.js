function deleteTask(taskId) {
    if (!confirm('Delete this task?')) return;

    fetch(`/task/${taskId}/delete`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
            // If you have CSRF, add header here: 'X-CSRFToken': csrfToken
        }
    })
    .then(async (res) => {
        if (!res.ok) {
            // try to get server message
            const text = await res.text().catch(() => '');
            throw new Error(`Server responded ${res.status}: ${text}`);
        }
        return res.json();
    })
    .then(data => {
        if (data && data.success) {
            const el = document.getElementById(`task-${taskId}`);
            if (el) el.remove();
            else location.reload();
        } else {
            alert('Could not delete task: ' + (data && data.error ? data.error : 'unknown error'));
        }
    })
    .catch(err => {
        console.error('deleteTask error:', err);
        alert('Failed to delete task. Check console and network tab for details.');
    });
}
