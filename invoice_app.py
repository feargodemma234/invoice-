import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

DB_FILE = "invoice_users.db"

st.set_page_config(page_title="Smart Invoice NG", layout="centered", page_icon="🧾")

@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, password TEXT, business_name TEXT, logo_path TEXT, invoices_left INTEGER)''')
    return conn, c

conn, c = init_db()

def get_user(email):
    return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def create_user(email, password, business):
    if get_user(email):
        return False
    c.execute("INSERT INTO users VALUES (?,?,?,?,?)", (email, password, business, "", 3))
    conn.commit()
    return True

def update_invoices(email, left):
    c.execute("UPDATE users SET invoices_left=? WHERE email=?", (left, email))
    conn.commit()

class PDF(FPDF):
    def header(self):
        if st.session_state.get('logo') and os.path.exists(st.session_state.logo):
            self.image(st.session_state.logo, 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, st.session_state.business, 0, 1, 'C')
        self.ln(15)

def generate_pdf(items, customer, total):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Invoice to: {customer}", ln=1)
    pdf.cell(0, 10, txt=f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Item", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(40, 10, "Total", 1, ln=1)
    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(80, 10, item[0], 1)
        pdf.cell(30, 10, str(item[1]), 1)
        pdf.cell(40, 10, f"₦{item[2]:,}", 1)
        pdf.cell(40, 10, f"₦{item[1]*item[2]:,}", 1, ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"GRAND TOTAL: ₦{total:,}", ln=1, align='R')
    filename = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# --- INIT SESSION STATE ---
for key in ['logged_in', 'items', 'email', 'business', 'logo', 'invoices_left']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'items' else False if key == 'logged_in' else ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🧾 Smart Invoice NG")
    st.caption("Create professional invoices. 3 FREE invoices")

    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary"):
            user = get_user(email)
            if user and user[1] == password:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.business = user[2]
                st.session_state.logo = user[3]
                st.session_state.invoices_left = user[4]
                st.rerun()
            else: st.error("Wrong email or password")
    
    with tab2:
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        business = st.text_input("Business Name")
        if st.button("Create Account"):
            if create_user(email, password, business):
                st.success("Account created! Please Login")
            else:
                st.error("This email already exists. Please Login")

# --- DASHBOARD ---
else:
    st.title(f"{st.session_state.business}")
    
    # FIXED: Define columns before using them
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Free Invoices Left", st.session_state.invoices_left)
    with col2:
        item_count = len(st.session_state.items) if isinstance(st.session_state.items, list) else 0
        st.metric("Items on Invoice", item_count)
    with col3:
        if st.session_state.invoices_left <= 0:
            st.link_button("Upgrade ₦500/mo", "https://opay.ng/s/36QEa", type="primary")

    st.sidebar.title("⚙️ Settings")
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    st.header("Create New Invoice")
    customer = st.text_input("Customer Name / WhatsApp Number")

    with st.form("item_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3,1,2])
        item_name = col1.text_input("Item Name")
        qty = col2.number_input("Qty", min_value=1, value=1, step=1)
        price = col3.number_input("Price ₦", min_value=0, step=100)
        if st.form_submit_button("Add Item"):
            if item_name:
                st.session_state.items.append((item_name, int(qty), int(price)))
                st.rerun()

    if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
        st.subheader("Invoice Items")
        for i, item in enumerate(st.session_state.items):
            st.write(f"**{i+1}.** {item[0]} - {item[1]} x ₦{item[2]:,}")

        total = sum([item[1]*item[2] for item in st.session_state.items])
        st.subheader(f"Total: ₦{total:,}")

        if st.button("Generate PDF Invoice", type="primary"):
            if st.session_state.invoices_left <= 0:
                st.error("No free invoices left. Please upgrade")
            else:
    # SAFETY FIX: Force items to be a list
    if not isinstance(st.session_state.items, list):
        st.session_state.items = []

    st.title(f"{st.session_state.business}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Free Invoices Left", st.session_state.invoices_left)
    with col2:
        st.metric("Items on Invoice", len(st.session_state.items))
    with col3:
        if st.session_state.invoices_left <= 0:
            st.link_button("Upgrade ₦500/mo", "https://opay.ng/s/36QEa", type="primary")

    st.sidebar.title("⚙️ Settings")
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    st.header("Create New Invoice")
    customer = st.text_input("Customer Name / WhatsApp Number")

    with st.form("item_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3,1,2])
        item_name = col1.text_input("Item Name")
        qty = col2.number_input("Qty", min_value=1, value=1, step=1)
        price = col3.number_input("Price ₦", min_value=0, step=100)
        if st.form_submit_button("Add Item"):
            if item_name:
                st.session_state.items.append((item_name, int(qty), int(price)))
                st.rerun()

    if len(st.session_state.items) > 0:
        st.subheader("Invoice Items")
        for i, item in enumerate(st.session_state.items):
            st.write(f"**{i+1}.** {item[0]} - {item[1]} x ₦{item[2]:,}")

        total = sum([item[1]*item[2] for item in st.session_state.items])
        st.subheader(f"Total: ₦{total:,}")

        if st.button("Generate PDF Invoice", type="primary"):
            if st.session_state.invoices_left <= 0:
                st.error("No free invoices left. Please upgrade")
            else:
                pdf_file = generate_pdf(st.session_state.items, customer, total)
                st.success("Invoice Generated!")
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=pdf_file)

                clean_number = ''.join(filter(str.isdigit, customer))
                if clean_number.startswith('0'):
                    clean_number = '234' + clean_number[1:]
                whatsapp_link = f"https://wa.me/{clean_number}"
                st.link_button("📱 Send via WhatsApp", whatsapp_link)

                update_invoices(st.session_state.email, st.session_state.invoices_left - 1)
                st.session_state.invoices_left -= 1
                st.session_state.items = []
                st.rerun()