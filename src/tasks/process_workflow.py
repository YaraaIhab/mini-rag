from celery_app import celery_app, setup_celery
from celery import chain
import asyncio
import logging

from tasks.file_processing import process_uploaded_file
from tasks.data_indexing import _index_data

logger = logging.getLogger(__name__)


# ----------------------------
# AFTER PROCESS → INDEX
# ----------------------------
@celery_app.task(
    bind=True,
    name="tasks.process_workflow.push_after_process_task",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def push_after_process_task(self, prev_task_result):

    project_id = prev_task_result.get("project_id")
    do_reset = prev_task_result.get("do_reset")

    task_results = asyncio.run(
        _index_data(self, project_id, do_reset)
    )

    return {
        "project_id": project_id,
        "do_reset": do_reset,
        "task_results": task_results
    }


# ----------------------------
# MAIN WORKFLOW
# ----------------------------
@celery_app.task(
    bind=True,
    name="tasks.process_workflow.process_and_push_workflow",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def process_and_push_workflow(
    self,
    project_id: int,
    file_id: int,
    chunk_size: int,
    overlap_size: int,
    do_reset: int
):

    workflow = chain(
        process_uploaded_file.s(
            file_id,
            project_id,
            chunk_size,
            overlap_size,
            do_reset
        ),
        push_after_process_task.s()
    )

    result = workflow.apply_async()

    return {
        "signal": "WORKFLOW_STARTED",
        "workflow_id": result.id,
        "tasks": [
            "tasks.file_processing.process_uploaded_file",
            "tasks.data_indexing.index_data"
        ]
    }