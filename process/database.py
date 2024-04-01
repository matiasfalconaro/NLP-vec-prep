import requests

class ChromaHTTPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def create_collection(self, collection_name: str, get_or_create: bool = True, metadata: dict = None):
        """Create or retrieve a collection."""
        url = f"{self.base_url}/api/v1/collections"
        payload = {
            "name": collection_name,
            "get_or_create": get_or_create,
            "metadata": metadata or {}
        }
        response = requests.post(url, json=payload)
        if response.status_code in [201, 200]:
            print("Collection created or retrieved successfully.")
            return response.json()
        else:
            print(f"Failed to create or retrieve collection: {response.text}")
            response.raise_for_status()  # Raises an HTTPError for bad responses

    def add_to_collection(self, collection_id, embeddings=[], metadatas=[], documents=[], uris=[], ids=[]):
        """Add items to a specified collection."""
        url = f"{self.base_url}/api/v1/collections/{collection_id}/add"
        payload = {
            "embeddings": embeddings,
            "metadatas": metadatas,
            "documents": documents,
            "uris": uris,
            "ids": ids
        }
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to add to collection: {response.text}")
            response.raise_for_status()