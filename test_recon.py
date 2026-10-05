import asyncio
from backend.agents.recon.recon_agent import ReconAgent
from backend.models.task import Task

async def main():
    agent = ReconAgent()
    task = Task(action="RUN_RECON", target="https://github.com", context={}, priority="high")
    task.task_id = "TASK-TEST-001"
    response = await agent.execute(task)
    print("Response Status:", response.status)
    print("Errors:", response.errors)
    if response.data:
        print("Data lengths: Forms=", len(response.data.get('forms', [])), "Links=", len(response.data.get('links', [])))

if __name__ == "__main__":
    asyncio.run(main())
