from better_auth import auth, constants
from better_auth.database.drizzle import DrizzleAdapter
from better_auth.models import User
from better_auth.types import BetterAuthOptions
from sqlalchemy.ext.asyncio import create_async_engine
from .models import ExtendedUser
import os
from ..db.pg_client import save_user_profile
import asyncio

# Initialize database connection for Neon Postgres
DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_async_engine(DATABASE_URL)

# Create Drizzle adapter for Neon Postgres
adapter = DrizzleAdapter(engine)

# Better-Auth configuration
auth_config = BetterAuthOptions(
    secret=os.getenv("BETTER_AUTH_SECRET", "your-secret-key-change-in-production"),
    database_url=DATABASE_URL,
    user_model=ExtendedUser,  # Using ExtendedUser from models.py
    email_password=True,
    session={
        "enabled": True,
        "cookie_name": "__better_auth_session",
        "expires_in_days": 7,
    },
    callbacks={
        "after_register": lambda user: asyncio.create_task(save_extended_profile(user)),
        "after_sign_in": lambda user: print(f"User signed in: {user.email}"),
    }
)

async def save_extended_profile(user):
    """
    Save extended profile information for new users
    """
    try:
        # Create default profile with software/hardware background
        profile_data = {
            "software_background": {
                "level": getattr(user, 'software_level', 'beginner'),
                "stack": getattr(user, 'software_stack', ''),
            },
            "hardware_background": {
                "level": getattr(user, 'hardware_level', 'none'),
                "platforms": getattr(user, 'hardware_platforms', ''),
            },
            "preferences": {}
        }

        # Save the profile to the database
        success = await save_user_profile(str(user.id), profile_data)
        if success:
            print(f"Extended profile saved for user: {user.email}")
        else:
            print(f"Failed to save extended profile for user: {user.email}")
    except Exception as e:
        print(f"Error saving extended profile for user {user.email}: {str(e)}")

# Initialize Better-Auth
better_auth = auth(auth_config)