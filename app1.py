import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import pandas as pd
import os
import re

# =========================
# OCR MODEL
# =========================

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# =========================
# STORAGE
# =========================

history_directory = "data"
os.makedirs(history_directory, exist_ok=True)

# =========================
# OCR PROCESSING
# =========================

def process_receipt(image):
    try:
        image_np = np.array(image)

        results = reader.readtext(image_np, detail=0)

        if not results:
            return []

        text = "\n".join(results)

        text = re.sub(r'(\d), (\d)', r'\1\2', text)
        text = re.sub(r'(\d),(\d)', r'\1\2', text)

        lines = text.split("\n")

        cleaned_lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]

        return cleaned_lines

    except Exception as e:
        st.error(f"OCR Error: {e}")
        return []

# =========================
# CATEGORIZATION
# =========================

def categorize_items(items):
    categories = {
        "Makanan": [
            "beras","sayur","daging","susu",
            "bread butter pudding","cream bruille",
            "choco croissant","bank of chocolat",
            "pop mie","nestle pure life",
            "le minerale","ultra kcng hijau",
            "nutrtjel","kanzlr","knzler",
            "cheezy","red bull","cookie",
            "cappucinno","tea","teh","meg",
            "mie","nasi","pisang","tahu",
            "tempe","indomie","belfood",
            "jeruk","chocolate","coffee",
            "mocha","telur","beef","soto",
            "cappuccino","permen"
        ],
        "Transportasi": [
            "bensin","tiket","tol"
        ],
        "Hiburan": [
            "bioskop","game","streaming","studio"
        ],
        "Pakaian": [
            "baju","sepatu","jaket","shirt","outer"
        ],
        "BodyCare": [
            "ponds","autan","sabun"
        ],
        "Lainnya": []
    }

    categorized_data = {key: [] for key in categories.keys()}

    for item in items:

        item_lower = item.lower()
        matched = False

        for category, keywords in categories.items():

            if category == "Lainnya":
                continue

            if any(keyword in item_lower for keyword in keywords):
                categorized_data[category].append(item)
                matched = True
                break

        if not matched:
            categorized_data["Lainnya"].append(item)

    return categorized_data

# =========================
# CALCULATIONS
# =========================

def calculate_totals(categorized_items):

    totals = {}

    for category, items in categorized_items.items():

        total = 0

        for item in items:

            try:
                price_str = (
                    item.split()[-1]
                    .replace("Rp", "")
                    .replace(",", "")
                    .replace(".", "")
                )

                if price_str.isdigit():
                    total += float(price_str)

            except (IndexError, ValueError):
                pass

        totals[category] = total

    return totals

# =========================
# HISTORY
# =========================

def load_expenses_history(person_name):

    history_file = os.path.join(
        history_directory,
        f"{person_name}_history.csv"
    )

    if os.path.exists(history_file):
        return pd.read_csv(history_file)

    return pd.DataFrame(
        columns=["Category", "Amount"]
    )

def save_expenses_history(person_name, data):

    history_file = os.path.join(
        history_directory,
        f"{person_name}_history.csv"
    )

    data.to_csv(history_file, index=False)

def reset_expenses_history(person_name):

    history_file = os.path.join(
        history_directory,
        f"{person_name}_history.csv"
    )

    if os.path.exists(history_file):
        os.remove(history_file)
        st.success(
            f"Riwayat pengeluaran untuk {person_name} telah direset."
        )