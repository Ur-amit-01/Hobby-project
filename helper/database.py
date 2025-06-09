import motor.motor_asyncio
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
            metadata_code="By :- @Madflix_Bots"
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

    #============ Channel System ============#
    async def add_channels(self, channel_ids):
        """Add multiple channels to the database."""
        added_channels = []
        already_existing = []

        for channel_id in channel_ids:
            channel_id = int(channel_id)  # Ensure it's an integer
            if not await self.is_channel_exist(channel_id):
                await self.channels.insert_one({"_id": channel_id})
                added_channels.append(channel_id)
            else:
                already_existing.append(channel_id)

        return added_channels, already_existing

    async def delete_channels(self, channel_ids):
        """Delete multiple channels from the database."""
        deleted_channels = []
        not_found = []

        for channel_id in channel_ids:
            channel_id = int(channel_id)
            if await self.is_channel_exist(channel_id):
                await self.channels.delete_one({"_id": channel_id})
                deleted_channels.append(channel_id)
            else:
                not_found.append(channel_id)

        return deleted_channels, not_found

    async def is_channel_exist(self, channel_id):
        """Check if a channel exists in the database."""
        return await self.channels.find_one({"_id": int(channel_id)}) is not None

    async def get_all_channels(self):
        """Retrieve all channels as a list."""
        return [channel async for channel in self.channels.find({})]

    #============ Formatting System ============#
    async def save_formatting(self, channel_id, formatting_text):
        """Save or update formatting text for a channel."""
        await self.formatting.update_one(
            {"_id": int(channel_id)},
            {"$set": {"formatting_text": formatting_text}},
            upsert=True
        )

    async def get_formatting(self, channel_id):
        """Retrieve formatting text for a channel."""
        result = await self.formatting.find_one({"_id": int(channel_id)})
        return result.get("formatting_text") if result else None

    #============ Admib ============
    


	async def get_daily_active_users():
    	return await users_collection.count_documents({
        	"last_active": {"$gt": datetime.now() - timedelta(days=1)}
    })
# Initialize the database
db = Database(DB_URL, DB_NAME)
