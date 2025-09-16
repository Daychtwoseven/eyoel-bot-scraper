from supabase import create_client, Client
from datetime import date

# Your Supabase credentials
SUPABASE_URL: str = "https://mszplrrnynmcsnxgevdi.supabase.co"
SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zenBscnJueW5tY3NueGdldmRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2NDAzNjEsImV4cCI6MjA3MTIxNjM2MX0.c_wDP_XrvptCOqWWag2-WszeNL58KGBMaYA2OTx4zeg"


def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_all(table: str):
    """Fetch all rows from a Supabase table"""
    supabase = get_supabase_client()
    try:
        response = supabase.table(table).select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching data from {table}: {e}")
        return []


def insert_foreclosure_lead(address: str,
                            workflow: int,
                            document_url: str,
                            document_id: str,
                            file_date: date,
                            sale_date: date):
    """
    Insert a new foreclosure lead into houston_foreclosure_leads table.

    - id (int8) -> Auto-generated
    - created_at (timestamptz) -> Auto-generated (now())
    - address (text) -> Required
    - workflow (int2) -> Nullable
    - document_url (text) -> Required
    - document_id (varchar) -> Required
    - file_date (date) -> Required
    - sale_date (date) -> Required
    """
    supabase = get_supabase_client()
    try:
        data = {
            "address": address,
            "workflow": workflow,
            "document_url": document_url,
            "document_id": document_id,
            "file_date": file_date.isoformat() if file_date else None,
            "sale_date": sale_date.isoformat() if sale_date else None,
        }
        response = supabase.table("houston_foreclosure_leads").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"❌ Error inserting foreclosure lead: {e}")
        return None


if __name__ == "__main__":
    # Example: fetch all rows

    new_lead = insert_foreclosure_lead(
        address="123 Main St, Houston, TX",
        workflow=1,
        document_url="https://example.com/doc.pdf",
        document_id="FRCL-2025-5676",
        file_date=date(2025, 1, 15),
        sale_date=date(2025, 2, 1)
    )
    print("✅ Inserted:", new_lead)

    rows = fetch_all("houston_foreclosure_leads")
    print("📦 Data:", rows)