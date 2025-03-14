import asyncio
import aiohttp
import pandas as pd
import logging
from aiohttp import ClientSession
import threading

# API Endpoints
API_URL = "http://127.0.0.1:8000/api/employees/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"

# Admin credentials (replace with actual credentials)
USERNAME = "admin"
PASSWORD = "admin"

# CSV file path
CSV_FILE_PATH = "employees.csv"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Batch size for sending records in chunks
BATCH_SIZE = 500
MAX_RETRIES = 3  # Maximum retry attempts for failed requests


async def get_auth_token():
    """Fetch JWT token using admin credentials."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                TOKEN_URL,
                json={"username": USERNAME, "password": PASSWORD},
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access")  # Get access token
                else:
                    logging.error(f"❌ Authentication failed! Status: {response.status}, Response: {await response.text()}")
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"❌ Error during authentication: {e}")
            return None


async def send_batch(session: ClientSession, batch: list, auth_token: str):
    """Send a batch of employee records asynchronously."""
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(API_URL, json=batch, headers=headers) as response:
                if response.status == 201:
                    logging.info(f"✅ Successfully uploaded {len(batch)} records.")
                    return True
                else:
                    logging.error(f"⚠️ Failed to upload. Status: {response.status}, Response: {await response.text()}")
        except aiohttp.ClientError as e:
            logging.error(f"❌ Request failed: {e}")

        logging.info(f"🔄 Retrying batch ({attempt + 1}/{MAX_RETRIES})...")
        await asyncio.sleep(2)  # Wait before retrying

    logging.error(f"❌ Failed after {MAX_RETRIES} retries.")
    return False


async def process_csv(file_path: str):
    """Read CSV and process employee records in bulk."""
    auth_token = await get_auth_token()
    if not auth_token:
        logging.error("❌ Exiting due to authentication failure.")
        return

    df = pd.read_csv(file_path)
    employee_records = df.to_dict(orient="records")


    async with aiohttp.ClientSession() as session:

        tasks = []
        for i in range(0, len(employee_records), BATCH_SIZE):
            batch = employee_records[i : i + BATCH_SIZE]
            tasks.append(send_batch(session, batch, auth_token))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(process_csv(CSV_FILE_PATH))
