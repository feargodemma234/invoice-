import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

DB_FILE = "invoice_users.db"

# --- DB SETUP ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (email TEXT PRIMARY KEY, password TEXT, business_name TEXT, logo_path TEXT, invoices_left INTEGER)''')
conn.commit()

def get_user(email):
    return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def create_user(email, password):
    c.execute("INSERT INTO users VALUES (?,?,?,?,?)", (email, password, "My Business", "", 3))
    conn.commit()

def update_invoices(email, left):
    c.execute("UPDATE users SET invoices_left=? WHERE email=?", (left, email))
    conn.commit()

# --- PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        if st.session_state.logo:
            self.image(st.session_state.logo, 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, st.session_state.business, 0, 1, 'C')
        self.ln(20)

def generate_pdf(items, customer, total):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice to: {customer}", ln=1)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%d-%m-%Y')}", ln=1)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Item", 1)
    pdf.cell(40, 10, "Qty", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(40, 10, "Total", 1, ln=1)

    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(80, 10, item[0], 1)
        pdf.cell(40, 10, str(item[1]), 1)
        pdf.cell(40, 10, f"₦{item[2]}", 1)
        pdf.cell(40, 10, f"₦{item[1]*item[2]}", 1, ln=1)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"GRAND TOTAL: ₦{total}", ln=1, align='R')

    filename = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# --- APP ---
if 'logged_in' not in st.session_state:
    st.set_page_config(page_title="Smart Invoice NG", layout="centered")
    st.title("🧾 Smart Invoice NG")
    st.write("Create professional invoices and send to WhatsApp. 3 FREE invoices")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email)
            if user and user[1] == password:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.business = user[2]
                st.session_state.logo = user[3]
                st.session_state.invoices_left = user[4]
                st.rerun()
            else: st.error("Wrong details")
    with tab2:
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        business = st.text_input("Business Name")
        if st.button("Create Account"):
            create_user(email, password)
            c.execute("UPDATE users SET business_name=? WHERE email=?", (business, email))
            conn.commit()
            st.success("Account created! Login now")

else:
    st.set_page_config(page_title="Dashboard", layout="wide")
    st.title(f"Welcome, {st.session_state.business}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Free Invoices Left", st.session_state.invoices_left)
    with col2:
        if st.session_state.invoices_left <= 0:
            st.link_button("Upgrade - ₦500/month", "https://opay.ng/s/36QEa", type="primary")

    st.sidebar.title("Settings")
    new_business = st.sidebar.text_input("Business Name", st.session_state.business)
    logo = st.sidebar.file_uploader("Upload Logo", type=['png','jpg'])
    if st.sidebar.button("Save"):
        logo_path = ""
        if logo:
            logo_path = f"logo_{st.session_state.email}.png"
            with open(logo_path, "wb") as f: f.write(logo.getbuffer())
        c.execute("UPDATE users SET business_name=?, logo_path=? WHERE email=?",
                  (new_business, logo_path, st.session_state.email))
        conn.commit()
        st.sidebar.success("Saved!")

    st.header("Create New Invoice")
    customer = st.text_input("Customer Name / WhatsApp Number")

    if 'items' not in st.session_state: st.session_state.items = []

    with st.form("item_form"):
        col1, col2, col3 = st.columns(3)
        item_name = col1.text_input("Item")
        qty = col2.number_input("Qty", min_value=1, value=1)
        price = col3.number_input("Price ₦", min_value=0)
        if st.form_submit_button("Add Item"):
            st.session_state.items.append((item_name, qty, price))

    for i, item in enumerate(st.session_state.items):
        st.write(f"{i+1}. {item[0]} - {item[1]} x ₦{item[2]}")

    total = sum([i[1]*i[2] for i in st.session_state.items])
    st.subheader(f"Total: ₦{total}")

    if st.button("Generate PDF Invoice", type="primary"):
        if st.session_state.invoices_left <= 0:
            st.error("No free invoices left. Please upgrade")
        elif not st.session_state.items:
            st.warning("Add at least 1 item")
        else:
            pdf_file = generate_pdf(st.session_state.items, customer, total)
            st.success("Invoice Generated!")
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name=pdf_file)

            whatsapp_link = f"https://wa.me/{customer}?text=Hello%20{customer},%20please%20see%20your%20invoice%20attached"
            st.link_button("Send via WhatsApp", whatsapp_link)

            if get_user(st.session_state.email)[4] > 0:
                update_invoices(st.session_state.email, st.session_state.invoices_left - 1)
                st.session_state.invoices_left -= 1
            st.session_state.items = []
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()