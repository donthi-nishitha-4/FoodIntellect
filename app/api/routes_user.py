from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, AnalysisHistory


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/profile")
def create_profile(
    name: str,
    email: str,
    age: int = None,
    dietary_preference: str = None,
    allergies: str = None,
    db: Session = Depends(get_db)
):

    user = User(
        name=name,
        email=email,
        age=age,
        dietary_preference=dietary_preference,
        allergies=allergies
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "success": True,
        "user_id": user.id,
        "message": "Profile created successfully"
    }


@router.get("/profile/{user_id}")
def get_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        return {
            "success": False,
            "message": "User not found"
        }

    return {
        "success": True,

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "dietary_preference":
                user.dietary_preference,
            "allergies":
                user.allergies
        }
    }


@router.get("/history/{user_id}")
def get_history(
    user_id: int,
    db: Session = Depends(get_db)
):

    history = db.query(
        AnalysisHistory
    ).filter(
        AnalysisHistory.user_id == user_id
    ).all()

    result = []

    for item in history:

        result.append({

            "id": item.id,

            "product_name":
                item.product_name,

            "barcode":
                item.barcode,

            "ingredients":
                item.ingredients,

            "analysis":
                item.analysis,

            "created_at":
                str(item.created_at)
        })

    return {
        "success": True,
        "history": result
    }