# Usage Example
# python script.py create "Test Title" "Test Description"
# python script.py get --num_pages 5
# python script.py update <PAGE_ID> "2023-01-15T00:00:00Z"
# python script.py delete <PAGE_ID>

import argparse
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    return res

#title = "Test Title"
#description = "Test Description"
#published_date = datetime.now().astimezone(timezone.utc).isoformat()
#data = {
    #"URL": {"title": [{"text": {"content": description}}]},
    #"Title": {"rich_text": [{"text": {"content": title}}]},
    #"Published": {"date": {"start": published_date, "end": None}}
#}

#create_page(data)

def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # Comment this out to dump all data to a file
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results

#pages = get_pages()

#for page in pages:
    page_id = page["id"]
    props = page["properties"]
    url = props["URL"]["title"][0]["text"]["content"]
    title = props["Title"]["rich_text"][0]["text"]["content"]
    published = props["Published"]["date"]["start"]
    published = datetime.fromisoformat(published)

def update_page(page_id: str, data: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"properties": data}

    res = requests.patch(url, json=payload, headers=headers)
    return res

#page_id = "the page id"

#new_date = datetime(2023, 1, 15).astimezone(timezone.utc).isoformat()
#update_data = {"Published": {"date": {"start": new_date, "end": None}}}

#update_page(page_id, update_data)

def delete_page(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"archived": True}

    res = requests.patch(url, json=payload, headers=headers)
    return res

def main():
    parser = argparse.ArgumentParser(description="Interact with the Notion API")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new page")
    create_parser.add_argument("title", type=str, help="Title of the page")
    create_parser.add_argument("description", type=str, help="Description of the page")

    get_parser = subparsers.add_parser("get", help="Get pages from the database")
    get_parser.add_argument("--num_pages", type=int, help="Number of pages to retrieve")

    update_parser = subparsers.add_parser("update", help="Update an existing page")
    update_parser.add_argument("page_id", type=str, help="ID of the page to update")
    update_parser.add_argument("new_date", type=str, help="New date in ISO format (YYYY-MM-DD)")

    delete_parser = subparsers.add_parser("delete", help="Delete (archive) a page")
    delete_parser.add_argument("page_id", type=str, help="ID of the page to delete")

    args = parser.parse_args()

    if args.command == "create":
        title = args.title
        description = args.description
        published_date = datetime.now().astimezone(timezone.utc).isoformat()

        data = {
            "URL": {"title": [{"text": {"content": description}}]},
            "Title": {"rich_text": [{"text": {"content": title}}]},
            "Published": {"date": {"start": published_date, "end": None}}
        }

        response = create_page(data)
        print(response.json())

    elif args.command == "get":
        num_pages = args.num_pages
        pages = get_pages(num_pages=num_pages)
        for page in pages:
            page_id = page["id"]
            props = page["properties"]
            url = props["URL"]["title"][0]["text"]["content"]
            title = props["Title"]["rich_text"][0]["text"]["content"]
            published = props["Published"]["date"]["start"]
            print(f"Page ID: {page_id}, Title: {title}, URL: {url}, Published: {published}")

    elif args.command == "update":
        page_id = args.page_id
        new_date = args.new_date
        update_data = {"Published": {"date": {"start": new_date, "end": None}}}
        response = update_page(page_id, update_data)
        print(response.json())

    elif args.command == "delete":
        page_id = args.page_id
        response = delete_page(page_id)
        print(response.json())

if __name__ == "__main__":
    main()
