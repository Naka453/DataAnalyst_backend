from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_vector_store_id() -> str:
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
    if not vector_store_id:
        raise ValueError("OPENAI_VECTOR_STORE_ID is not set")
    return vector_store_id


def get_vector_store():
    vector_store_id = get_vector_store_id()
    return client.vector_stores.retrieve(vector_store_id=vector_store_id)


def list_vector_store_files():
    vector_store_id = get_vector_store_id()
    return client.vector_stores.files.list(vector_store_id=vector_store_id)


if __name__ == "__main__":
    vs = get_vector_store()
    files = list_vector_store_files()

    print("VECTOR_STORE_ID =", vs.id)
    print("STATUS =", getattr(vs, "status", None))
    print("USAGE_BYTES =", getattr(vs, "usage_bytes", None))
    print("FILES =")
    for f in files.data:
        print(f"- {f.id} | status={getattr(f, 'status', None)}")