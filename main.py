import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str 
    price: float


storage = {
    1: Item(name="Phone",  price=1000.0),
    2: Item(name="Laptop", price=2000.0)
    }

@app.get("/items/")
def get_item(id: int) -> Item:
    if id not in storage:
        raise HTTPException(status_code=404, detail="Item not found")
    return storage[id]

@app.post("/items/")
def add_item(item: Item) -> int:
    id = max(storage.keys()) + 1 if storage else 1
    storage[id] = item
    return id

@app.put("/items/")
def update_item(id: int, item: Item) -> None:
    if id not in storage:
        raise HTTPException(status_code=404, detail="Item not found")
    storage[id] = item

@app.delete("/items/")
def delete_item(id: int) -> None:
    if id not in storage:
        raise HTTPException(status_code=404, detail="Item not found")
    del storage[id]

uvicorn.run(app, host="0.0.0.0", port=8888)