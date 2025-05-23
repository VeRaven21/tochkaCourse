from fastapi import FastAPI

import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from routers import public, admin


app = FastAPI()


# Public
app.include_router(public.router, prefix="/api/v1")

# Admin
app.include_router(admin.router, prefix="/api/v1/admin")
