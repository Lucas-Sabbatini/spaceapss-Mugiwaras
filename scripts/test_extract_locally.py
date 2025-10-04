# Optional local tester (doesn't require azure-functions runtime)
import asyncio
from api.extract.extractor import extract_url

URL = "https://example.com"

async def main():
    data = await extract_url(URL)
    print(data.keys(), data.get("length_chars"))

if __name__ == "__main__":
    asyncio.run(main())
