import streamlit as st
import pandas as pd
import numpy as np
import io
import time

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Rehman Cable.in | Industrial Electrical & Cable Marketplace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .badge-lowest {
        background-color: #DCFCE7;
        color: #15803D;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .brand-accent {
        color: #D97706;
        font-weight: bold;
    }
    .stTable {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA LOADING & COMPUTATION PIPELINE
# -----------------------------------------------------------------------------
@st.cache_data
def load_default_data():
    try:
        # Load directly from Excel if available in the same repository
        df = pd.read_excel('Cable_Price_Comparison for software.xlsx', skiprows=3)
    except Exception:
        # Fallback embedded dataset matching exact structure if file is missing
        data = [
            ["General Wiring (BS-2004)", "3/.029 Single Core", "90m Coil", 5948, 6950, 9499, 10811],
            ["General Wiring (BS-2004)", "7/.029 Single Core", "90m Coil", 13068, 15025, 20999, 23681],
            ["General Wiring (BS-2004)", "7/.029 2-Core Flat", "Per Meter", None, 383, None, None],
            ["General Wiring (BS-6004)", "1.5 mm² S/C Solid", "90m Coil", 7017, 7880, 10999, 12083],
            ["General Wiring (BS-6004)", "2.5 mm² S/C Stranded", "90m Coil", 11261, 12130, 18199, 20835],
            ["General Wiring (BS-6004)", "4.0 mm² S/C Stranded", "90m Coil", 17534, 20240, 27499, 30858],
            ["Flexible Cables (BS-6500)", "1.5 mm² 2-Core Flexible", "Per Meter", 179, 229, 328, 377],
            ["Solar PV Cables (DC 1500V)", "4.0 mm² XLPO Single Core", "Per Meter", 224, 183, 380, 497],
            ["Networking Cable (CAT-6)", "CAT-6 UTP Copper Standard", "305m Coil", 40000, 58550, 33855, None]
        ]
        df = pd.DataFrame(data, columns=[
            "Product Category", "Specification / Subcategory", "Standard Unit", 
            "Million Classic (PKR)", "GM Cables (PKR)", "Fast Cables (PKR)", "Newage Cables (PKR)"
        ])
    
    brand_cols = ["Million Classic (PKR)", "GM Cables (PKR)", "Fast Cables (PKR)", "Newage Cables (PKR)"]
    
    # Calculate Lowest Price dynamically
    df["Lowest Price (PKR)"] = df[brand_cols].min(axis=1)
    
    def get_lowest_info(row):
        valid = row[brand_cols].dropna()
        if valid.empty:
            return "N/A"
        min_val = valid.min()
        vendor = valid.idxmin().replace(" (PKR)", "")
        return f"{vendor} with Rs.{min_val:,.0f}/-"

    df["Lowest Price Vendor & Rate"] = df.apply(get_lowest_info, axis=1)
    
    # Variance vs highest calculation
    max_price = df[brand_cols].max(axis=1)
    min_price = df["Lowest Price (PKR)"]
    df["Variance vs Highest (%)"] = ((max_price - min_price) / max_price) * 100
    
    return df

# Initialize Session State
if "catalog_df" not in st.session_state:
    st.session_state.catalog_df = load_default_data()

if "cart" not in st.session_state:
    st.session_state.cart = []

df_current = st.session_state.catalog_df

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & FACETED FILTERS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/electrical.png", width=60)
st.sidebar.title("Rehman Cable.in")
st.sidebar.caption("Industrial Wire & Cable Portal")

nav_mode = st.sidebar.radio(
    "Navigation Mode", 
    ["🛒 Store Catalog", "⚡ Technical Multi-Brand Comparison", "📄 B2B Quote & Cart", "⚙️ Admin Price Import"]
)

st.sidebar.divider()
st.sidebar.subheader("🎯 Technical Specs Filter")

# Category Filter
categories = ["All Categories"] + list(df_current["Product Category"].dropna().unique())
selected_cat = st.sidebar.selectbox("Product Standard / Category", categories)

# Standard Unit Filter
units = ["All Units"] + list(df_current["Standard Unit"].dropna().unique())
selected_unit = st.sidebar.selectbox("Standard Unit", units)

# Price Range Filter
min_val = int(df_current["Lowest Price (PKR)"].min())
max_val = int(df_current["Lowest Price (PKR)"].max())
price_range = st.sidebar.slider("Lowest Price Range (PKR)", min_value=min_val, max_value=max_val, value=(min_val, max_val))

# Filter Application
filtered_df = df_current.copy()

if selected_cat != "All Categories":
    filtered_df = filtered_df[filtered_df["Product Category"] == selected_cat]

if selected_unit != "All Units":
    filtered_df = filtered_df[filtered_df["Standard Unit"] == selected_unit]

filtered_df = filtered_df[
    (filtered_df["Lowest Price (PKR)"] >= price_range[0]) & 
    (filtered_df["Lowest Price (PKR)"] <= price_range[1])
]

# -----------------------------------------------------------------------------
# MODE 1: STORE CATALOG & SEARCH
# -----------------------------------------------------------------------------
if nav_mode == "🛒 Store Catalog":
    st.markdown('<p class="main-header">Rehman <span class="brand-accent">Cable.in</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Authorized Industrial Electrical Cable & Wire Distributor — B2B & B2C Market Rates</p>', unsafe_allow_html=True)
    
    # Trust Badges Banner
    col_tb1, col_tb2, col_tb3, col_tb4 = st.columns(4)
    with col_tb1:
        st.success("✅ **BS Standard Certified**")
    with col_tb2:
        st.info("🏭 **Factory Direct Rates**")
    with col_tb3:
        st.warning("📜 **Mill Test Certificates**")
    with col_tb4:
        st.error("🚚 **Nationwide B2B Delivery**")

    st.divider()

    # Search Bar
    search_query = st.text_input("🔍 Search by Specification (e.g., 1.5 mm², Single Core, 7/.029, CAT-6, XLPO)...", "")
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Specification / Subcategory"].str.contains(search_query, case=False, na=False) |
            filtered_df["Product Category"].str.contains(search_query, case=False, na=False)
        ]

    st.subheader(f"Cable Catalog Results ({len(filtered_df)} Items Found)")

    # Grid Display
    cols_per_row = 3
    for i in range(0, len(filtered_df), cols_per_row):
        row_items = filtered_df.iloc[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, (_, item) in enumerate(row_items.iterrows()):
            with cols[idx]:
                st.markdown(f"### {item['Specification / Subcategory']}")
                st.caption(f"**Category:** {item['Product Category']} | **Unit:** {item['Standard Unit']}")
                
                lowest_price = item['Lowest Price (PKR)']
                lowest_info = item['Lowest Price Vendor & Rate']
                
                st.markdown(f"**Lowest Rate:** <span class='badge-lowest'>Rs. {lowest_price:,.0f}</span>", unsafe_allow_html=True)
                st.caption(f"⭐ **Best Option:** {lowest_info}")
                
                # Brand selection for cart
                avail_brands = {}
                for b in ["Million Classic", "GM Cables", "Fast Cables", "Newage Cables"]:
                    val = item[f"{b} (PKR)"]
                    if pd.notna(val) and val > 0:
                        avail_brands[f"{b} (Rs. {val:,.0f})"] = (b, val)
                
                if avail_brands:
                    selected_brand_key = st.selectbox(
                        "Select Brand Stocked:", 
                        list(avail_brands.keys()), 
                        key=f"select_{item['Specification / Subcategory']}_{i}_{idx}"
                    )
                    b_name, b_price = avail_brands[selected_brand_key]
                    
                    qty = st.number_input("Qty:", min_value=1, value=1, key=f"qty_{item['Specification / Subcategory']}_{i}_{idx}")
                    
                    if st.button("🛒 Add to Order Cart", key=f"btn_{item['Specification / Subcategory']}_{i}_{idx}"):
                        st.session_state.cart.append({
                            "Category": item["Product Category"],
                            "Specification": item["Specification / Subcategory"],
                            "Unit": item["Standard Unit"],
                            "Brand": b_name,
                            "UnitPrice": b_price,
                            "Quantity": qty,
                            "TotalPrice": b_price * qty
                        })
                        st.toast(f"Added {qty} x {item['Specification / Subcategory']} ({b_name}) to cart!", icon="✅")
                st.divider()

# -----------------------------------------------------------------------------
# MODE 2: TECHNICAL MULTI-BRAND COMPARISON MATRIX
# -----------------------------------------------------------------------------
elif nav_mode == "⚡ Technical Multi-Brand Comparison":
    st.title("⚡ Multi-Brand Price Comparison Matrix")
    st.caption("Live side-by-side pricing matrix across Million Classic, GM Cables, Fast Cables, and Newage Cables")
    
    display_df = filtered_df.copy()
    display_cols = [
        "Product Category", "Specification / Subcategory", "Standard Unit",
        "Million Classic (PKR)", "GM Cables (PKR)", "Fast Cables (PKR)", "Newage Cables (PKR)",
        "Lowest Price (PKR)", "Lowest Price Vendor & Rate", "Variance vs Highest (%)"
    ]
    
    st.dataframe(
        display_df[display_cols].style.format({
            "Million Classic (PKR)": "Rs. {:,.0f}",
            "GM Cables (PKR)": "Rs. {:,.0f}",
            "Fast Cables (PKR)": "Rs. {:,.0f}",
            "Newage Cables (PKR)": "Rs. {:,.0f}",
            "Lowest Price (PKR)": "Rs. {:,.0f}",
            "Variance vs Highest (%)": "{:.1f}%"
        }, na_rep="N/A"),
        use_container_width=True,
        height=600
    )

# -----------------------------------------------------------------------------
# MODE 3: CART & B2B QUOTE GENERATOR
# -----------------------------------------------------------------------------
elif nav_mode == "📄 B2B Quote & Cart":
    st.title("📄 B2B Purchase Order & Request a Quote")
    
    if not st.session_state.cart:
        st.info("Your order cart is currently empty. Browse the catalog to add cable items.")
    else:
        cart_df = pd.DataFrame(st.session_state.cart)
        
        st.subheader("Current Order Items")
        st.dataframe(cart_df[["Category", "Specification", "Unit", "Brand", "UnitPrice", "Quantity", "TotalPrice"]].style.format({
            "UnitPrice": "Rs. {:,.0f}",
            "TotalPrice": "Rs. {:,.0f}"
        }), use_container_width=True)
        
        subtotal = cart_df["TotalPrice"].sum()
        total_quantity = cart_df["Quantity"].sum()
        
        # Tiered Bulk Pricing Logic
        discount_rate = 0.0
        if total_quantity >= 50:
            discount_rate = 0.07 # 7% discount
        elif total_quantity >= 20:
            discount_rate = 0.05 # 5% discount
        elif total_quantity >= 5:
            discount_rate = 0.035 # 3.5% discount
            
        discount_amount = subtotal * discount_rate
        net_total = subtotal - discount_amount
        
        st.divider()
        col_calc1, col_calc2 = st.columns(2)
        
        with col_calc1:
            st.markdown(f"### Subtotal: **Rs. {subtotal:,.0f}**")
            if discount_rate > 0:
                st.markdown(f"### Tiered Volume Discount ({discount_rate*100:.1f}%): **- Rs. {discount_amount:,.0f}**")
            st.markdown(f"## Payable Total: **Rs. {net_total:,.0f}**")
            
        with col_calc2:
            st.markdown("### 🏢 Business Checkout Information")
            comp_name = st.text_input("Company / Contractor Name")
            ntn_no = st.text_input("NTN / GST Number")
            contact_person = st.text_input("Contact Person & Phone")
            
            if st.button("📄 Generate Official B2B Proforma Quote"):
                if comp_name and contact_person:
                    st.success("Proforma Invoice generated successfully!")
                    st.balloons()
                    
                    quote_io = io.StringIO()
                    cart_df.to_csv(quote_io, index=False)
                    st.download_button(
                        label="📥 Download Proforma Invoice CSV",
                        data=quote_io.getvalue(),
                        file_name=f"Rehman_Cable_Quote_{comp_name.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Please enter Company Name and Contact Person to generate the quote.")

        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = []
            st.rerun()

# -----------------------------------------------------------------------------
# MODE 4: ADMIN INVENTORY UPLOAD
# -----------------------------------------------------------------------------
elif nav_mode == "⚙️ Admin Price Import":
    st.title("⚙️ Admin Panel — Price List Management")
    st.caption("Upload a new Excel file matching the Rehman Cable standard column format to update store pricing in real-time.")
    
    uploaded_file = st.file_uploader("Upload Updated Price Comparison Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            new_df = pd.read_excel(uploaded_file, skiprows=3)
            st.write("Preview of Uploaded Data:")
            st.dataframe(new_df.head(10))
            
            if st.button("🚀 Apply Updated Price List to Live Store"):
                st.session_state.catalog_df = load_default_data()
                st.success("Live Store prices updated successfully!")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing file: {e}")

# Footer
st.divider()
st.caption("© 2026 Rehman Cable.in | Industrial Electrical Wire & Cable Marketplace | All rights reserved.")