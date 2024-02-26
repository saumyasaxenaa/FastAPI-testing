from fastapi import FastAPI, Depends, HTTPException, status, Response
import models
import schemas
from database import Base, engine, get_db
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post('/item')
async def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    new_item = models.DBItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get('/items')
def get_items(db: Session = Depends(get_db)):
    items = db.query(models.DBItem).all()
    return items


@app.get('/items/{item_id}')
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.DBItem).filter(models.DBItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return item


@app.put('/items/{item_id}')
async def update_item(item_id: int, updated_item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item_query = db.query(models.DBItem).filter(models.DBItem.id == item_id)
    item = item_query.first()
    if item == None:
        raise HTTPException(status_code=404, detail='Item not found')
    item_query.update(updated_item.dict(), synchronize_session=False)
    db.commit()
    return item_query.first()


@app.delete('/items/{item_id}')
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.DBItem).filter(models.DBItem.id == item_id)
    if item.first() == None:
        raise HTTPException(status_code=404, detail='Item not found')
    item.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
