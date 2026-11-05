import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from billtable.export import to_csv, to_rows  # noqa: E402
from billtable.extract import extract_bill  # noqa: E402
from billtable.validate import check  # noqa: E402

st.set_page_config(page_title="Bill to Table", page_icon="🧾")
st.title("🧾 Bill photo to clean table")
st.caption("Upload a photo of a bill or receipt and get structured, checked data you can download.")

try:
    if not os.getenv("GEMINI_API_KEY") and "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

up = st.file_uploader("Bill image", type=["jpg", "jpeg", "png", "webp"])
if up:
    st.image(up, width=300)
    if st.button("Extract", type="primary"):
        with st.spinner("Reading the bill..."):
            try:
                bill = extract_bill(up.getvalue())
            except Exception as e:
                st.error(f"Could not read this bill: {e}")
                st.stop()
        c1, c2, c3 = st.columns(3)
        c1.metric("Vendor", bill.vendor or "?")
        c2.metric("Date", bill.date or "?")
        c3.metric("Total", f"{bill.currency or ''} {bill.total}" if bill.total is not None else "?")
        st.dataframe(to_rows(bill), use_container_width=True)
        for w in check(bill):
            st.warning(w)
        st.download_button("Download CSV", to_csv(bill), "bill.csv", "text/csv")
