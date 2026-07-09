import asyncio
import uuid
import os
from app.db.session import AsyncSessionLocal
from app.db.models import Organization, Client, Project
from app.services.case_service import start_case

async def main():
    async with AsyncSessionLocal() as session:
        # Create an org, client and project
        org_id = uuid.uuid4()
        org = Organization(id=org_id, name="Test Org")
        session.add(org)
        await session.commit()
        
        client_id = uuid.uuid4()
        client = Client(id=client_id, company_name="Test Client", email=f"test{client_id}@test.com", org_id=org_id, industry="tech")
        session.add(client)
        await session.commit()
        
        project_id = uuid.uuid4()
        project = Project(id=project_id, name="Test Project", client_id=client_id)
        session.add(project)
        await session.commit()
        
        print(f"Created project: {project.id}")
        
    print("Starting case...")
    try:
        result = await start_case(
            raw_brief="We are a tech company looking to expand into Asia. Should we do it and how?",
            project_id=str(project_id)
        )
        print("Status:", result.get("status"))
        print("Thread ID:", result.get("thread_id"))
        
        data = result.get("data", {})
        if isinstance(data, dict):
            print("Data keys:", data.keys())
        else:
            print("Data:", data)
    except Exception as e:
        print("Error during start_case:", repr(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
