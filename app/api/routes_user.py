"""
FastAPI User Profile Routes (Member 3 Workstream)

Endpoints for managing user allergy profiles and health preferences.
"""
from fastapi import APIRouter
from schemas.contracts import UserProfile

router = APIRouter(prefix="/api/user", tags=["User Profiles"])

# Memory store placeholder
USERS_DB = {
    "usr_demo": UserProfile(
        user_id="usr_demo",
        name="Demo User",
        allergies=["peanuts", "milk", "gluten"],
        dietary_preferences=["low_sugar"]
    )
}


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Retrieve user profile by ID."""
    return USERS_DB.get(user_id, UserProfile(user_id=user_id, name="Guest"))


@router.post("/", response_model=UserProfile)
async def update_user_profile(profile: UserProfile):
    """Save or update user profile settings."""
    USERS_DB[profile.user_id] = profile
    return profile
