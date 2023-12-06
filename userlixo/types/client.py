import hydrogram


class Client(hydrogram.client.Client):
    me: hydrogram.types.User
    assistant: hydrogram.client.Client
