import streamlit as st
import json
import os
from utils.supabase_utils import supabase

LOCAL_FILE = "offline_cache.json"

# -----------------------------
# OFFLINE-CACHE LADEN
# -----------------------------
def load_cache():
    if not os.path.exists(LOCAL_FILE):
        return {"pending": []}
    try:
        with open(LOCAL_FILE, "r") as f:
            return json.load(f)
    except:
        return {"pending": []}

# -----------------------------
# OFFLINE-CACHE SPEICHERN
# -----------------------------
def save_cache(cache):
    with open(LOCAL_FILE, "w") as f:
        json.dump(cache, f, indent=4)

# -----------------------------
# EINTRAG SPEICHERN (ONLINE ODER OFFLINE)
# -----------------------------
def safe_insert(table, data):
    try:
        # Online speichern
        supabase.table(table).insert(data).execute()
        return True
    except:
        # Offline speichern
        cache = load_cache()
        cache["pending"].append({"table": table, "data": data})
        save_cache(cache)
        return False

# -----------------------------
# SYNC AUSFÜHREN
# -----------------------------
def sync_pending():
    cache = load_cache()
    if len(cache["pending"]) == 0:
        return 0

    synced = 0
    remaining = []

    for entry in cache["pending"]:
        try:
            supabase.table(entry["table"]).insert(entry["data"]).execute()
            synced += 1
        except:
            remaining.append(entry)

    cache["pending"] = remaining
    save_cache(cache)

    return synced
