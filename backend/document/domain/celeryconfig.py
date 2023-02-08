import os

## Broker settings.
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://")

## Using the database to store task state and results.
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://")

# List of modules to import when the Celery worker starts.
imports = ("document.domain.document_generator",)


# task_annotations = {"document.domain.document_generator.main": {"rate_limit": "10/s"}}

# task_queues = {
#     'test-queue': {
#         'exchange': 'test-queue',
#     }
# }
# task_routes = {
#     "worker.celery_worker.long_task": "test-queue"
# }
# task_track_started = True

# worker_concurrency = 1
# worker_prefetch_multiplier = 3
# worker_max_tasks_per_child = 10000
