import motor.motor_asyncio
from datetime import datetime, timedelta
from config import DB_URL, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user  # Collection for users
        self.channels = self.db.channels  # Collection for channels
        self.formatting = self.db.formatting  # Collection for formatting templates
        self.admins = self.db.admins  # Collection for admins
        self.posts = self.db.posts  # Collection for posts

    #============ User System ============#
    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            prefix=None,
            suffix=None,
            metadata=False,
            metadata_code="By :- @Madflix_Bots",
            last_active=datetime.now()
        )

    async def add_user(self, id):
        if not await self.is_user_exist(id):
            user = self.new_user(id)
            await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    # Thumbnail
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    # Caption
    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)
    
    #============ Admin System ============#
    async def add_admin(self, admin_id):
        """Add an admin to the database."""
        await self.admins.update_one(
            {"_id": int(admin_id)},
            {"$set": {"_id": int(admin_id)}},
            upsert=True
        )

    async def remove_admin(self, admin_id):
        """Remove an admin from the database."""
        await self.admins.delete_one({"_id": int(admin_id)})

    async def is_admin(self, admin_id):
        """Check if a user is an admin."""
        return await self.admins.find_one({"_id": int(admin_id)}) is not None

    async def get_all_admins(self):
        """Retrieve all admins as a list."""
        return [admin async for admin in self.admins.find({})]

    #============ Analytics ============#
    async def get_daily_active_users(self):
        """Count users active in the last 24 hours."""
        return await self.col.count_documents({
            "last_active": {"$gt": datetime.now() - timedelta(days=1)}
        })

    async def update_user_activity(self, user_id):
        """Update a user's last active timestamp."""
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"last_active": datetime.now()}}
        )

# Initialize the database
db = Database(DB_URL, DB_NAME)
