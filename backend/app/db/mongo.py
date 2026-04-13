from backend.app.core.settings import settings

_db = None
_use_mock = False

async def connect_db():
    global _db, _use_mock
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        c = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
        await asyncio.wait_for(c.admin.command("ping"), timeout=3)
        _db = c[settings.MONGO_DB]
        print("[RPR] Connected to MongoDB")
    except Exception as e:
        print("[RPR] MongoDB unavailable (" + str(e) + "), using in-memory store")
        _use_mock = True
        _db = _MockDB()

async def close_db():
    global _db, _use_mock
    if _db and not _use_mock:
        # motor client is attached to the db object
        _db.client.close()
        print("[RPR] MongoDB connection closed")

def get_db():
    return _db


class _MockCollection:
    def __init__(self):
        self._docs = []

    async def insert_one(self, doc):
        from bson import ObjectId
        doc = dict(doc)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self._docs.append(doc)
        class R:
            inserted_id = doc["_id"]
        return R()

    async def find_one(self, query):
        return self._match(query)

    async def update_one(self, query, update):
        doc = self._match(query)
        if doc and "$set" in update:
            doc.update(update["$set"])

    def find(self, query=None):
        return _MockCursor(self._docs, query or {})

    async def command(self, cmd):
        return {"ok": 1}

    def _match(self, query):
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None


class _MockCursor:
    def __init__(self, docs, query):
        self._docs = [d for d in docs if all(d.get(k) == v for k, v in query.items())]

    def sort(self, key, direction):
        self._docs = sorted(self._docs, key=lambda d: d.get(key, 0), reverse=(direction == -1))
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __aiter__(self):
        self._iter = iter(self._docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class _MockDB:
    def __init__(self):
        self._collections = {}

    def __getattr__(self, name):
        if name not in self._collections:
            self._collections[name] = _MockCollection()
        return self._collections[name]

    def __getitem__(self, name):
        return self.__getattr__(name)

    async def command(self, cmd):
        return {"ok": 1}
