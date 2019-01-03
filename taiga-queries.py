
select count(id) from tasks where status!=Done


statuses = project.list_task_statuses()
done_id = None
for status in statuses:
    if status.name == 'Done':
        done_id = status.id
        break

if done_id is None:
    print("Status ID for DONE not found")
    sys.exit(1)

sprints = api.milestones.list(project=project.id)
current_date = some date
for sprint in sprints:
    if current_date < estimated_finish and current_date > estimated_start:
        current_sprint = sprint
        break

tasks = api.tasks.list(project=project.id)

unfinished_tasks = [t for t in tasks if t.status != done_id]
print("Unfinished tasks: {}".format(len(unfinished_tasks)))
