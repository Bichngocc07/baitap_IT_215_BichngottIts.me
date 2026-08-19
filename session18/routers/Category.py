from fastapi import APIRouter
from sqlalchemy.orn import Session
from sql.database.database import get_db
router_category = APIRouter(
    prefix = "/categoryes"
    tags = ["Categoyryes"]
)
@router_category.get("")
def get_all_category(db: Session = Depends(get_db)):
    return get_category(db)

@router_category.post("")
def add_categorty(category: Certegory , db:Session=Depends(get_db)):
    return add_new_category(category, db)