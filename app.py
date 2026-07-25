import streamlit as st
import pandas as pd
import numpy as np
import io
import time

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Rehman Cables | Industrial Electrical Online Store",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS FOR E-COMMERCE STORE LOOK (NEWAGE STYLE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Top Banner Header */
    .top-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .store-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .store-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 5px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(90deg, #D97706 0%, #B45309 100%);
        color: white;
        padding: 18px 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* E-Commerce Product Card */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-color: #CBD5E1;
    }
    
    .category-badge {
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    
    .price-lowest {
        color: #16A34A;
        font-size: 1.35rem;
        font-weight: 800;
    }
    
    .price-original {
        color: #94A3B8;
        text-decoration: line-through;
        font-size: 0.9rem;
        margin-left: 8px;
    }

    .best-option-box {
        background-color: #F0FDF4;
        border: 1px dashed #86EFAC;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #166534;
        margin: 10px 0px;
    }

    /* Hide standard Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA ENGINE & INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_data
def load_default_data():
    try:
        df = pd.read_excel('Cable_Price_Comparison for software.xlsx', skiprows=3)
    except Exception:
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
    df["Lowest Price (PKR)"] = df[brand_cols].min(axis=1)
    
    def get_lowest_info(row):
        valid = row[brand_cols].dropna()
        if valid.empty:
            return "N/A"
        min_val = valid.min()
        vendor = valid.idxmin().replace(" (PKR)", "")
        return f"{vendor} @ Rs. {min_val:,.0f}"

    df["Lowest Price Vendor & Rate"] = df.apply(get_lowest_info, axis=1)
    max_price = df[brand_cols].max(axis=1)
    min_price = df["Lowest Price (PKR)"]
    df["Variance vs Highest (%)"] = ((max_price - min_price) / max_price) * 100
    
    return df

if "catalog_df" not in st.session_state:
    st.session_state.catalog_df = load_default_data()

if "cart" not in st.session_state:
    st.session_state.cart = []

df_current = st.session_state.catalog_df

# -----------------------------------------------------------------------------
# TOP NAVIGATION HEADER
# -----------------------------------------------------------------------------
cart_count = len(st.session_state.cart)

st.markdown(f"""
<div class="top-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="store-title">⚡ REHMAN CABLE <span style="color:#F59E0B;">eSTORE</span></h1>
            <p class="store-subtitle">Authorized Multibrand Industrial Wire & Cable Online Marketplace</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #1E293B; border: 1px solid #334155; padding: 8px 16px; border-radius: 20px; font-weight: 600; color: #F8FAFC;">
                🛒 Cart: <b>{cart_count} Item(s)</b>
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS (NEWAGE STYLE)
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/electrical.png", width=50)
st.sidebar.title("Store Navigation")

nav_mode = st.sidebar.radio(
    "Go To Page:", 
    ["🛍️ Online Cable Store", "📊 Multi-Brand Price Comparison", "🛒 Cart & B2B Checkout", "⚙️ Admin Price Portal"]
)

st.sidebar.divider()
st.sidebar.subheader("🔎 Product Filters")

# Category Filter
categories = ["All Categories"] + list(df_current["Product Category"].dropna().unique())
selected_cat = st.sidebar.selectbox("Filter Category", categories)

# Unit Filter
units = ["All Units"] + list(df_current["Standard Unit"].dropna().unique())
selected_unit = st.sidebar.selectbox("Standard Unit", units)

# Price Range Filter
min_val = int(df_current["Lowest Price (PKR)"].min())
max_val = int(df_current["Lowest Price (PKR)"].max())
price_range = st.sidebar.slider("Price Range (PKR)", min_value=min_val, max_value=max_val, value=(min_val, max_val))

# Filter DataFrame
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
# MODE 1: E-COMMERCE STORE CATALOG
# -----------------------------------------------------------------------------
if nav_mode == "🛍️ Online Cable Store":
    # Hero Promo Banner
    st.markdown("""
    <div class="hero-banner">
        <div>
            <h3 style="margin:0; font-weight:800;">🔥 Factory Direct Wholesale Pricing</h3>
            <p style="margin:0; font-size:0.9rem; opacity:0.9;">100% Original Copper Wires — Certified to BS & IEC Standards</p>
        </div>
        <div style="font-weight:700; font-size:0.9rem; background:rgba(255,255,255,0.2); padding:6px 12px; border-radius:6px;">
            🚚 Fast Delivery Across Pakistan
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search Bar
    search_query = st.text_input("🔍 Search Cables (e.g. 1.5mm, 7/.029, Single Core, CAT6, XLPO)...", "")
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Specification / Subcategory"].str.contains(search_query, case=False, na=False) |
            filtered_df["Product Category"].str.contains(search_query, case=False, na=False)
        ]

    st.subheader(f"Cable Catalog ({len(filtered_df)} Products Available)")

    # 3-Column Product Grid
    cols_per_row = 3
    for i in range(0, len(filtered_df), cols_per_row):
        row_items = filtered_df.iloc[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, (_, item) in enumerate(row_items.iterrows()):
            with cols[idx]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                st.markdown(f'<span class="category-badge">{item["Product Category"]}</span>', unsafe_allow_html=True)
                st.markdown(f"### {item['Specification / Subcategory']}")
                st.caption(f"**Unit:** {item['Standard Unit']}")
                
                lowest_price = item['Lowest Price (PKR)']
                lowest_info = item['Lowest Price Vendor & Rate']
                
                st.markdown(f"""
                <div style="margin-top:10px;">
                    <span class="price-lowest">Rs. {lowest_price:,.0f}</span>
                    <span class="price-original">Rs. {lowest_price * 1.12:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="best-option-box">⭐ Best Deal: <b>{lowest_info}</b></div>', unsafe_allow_html=True)
                
                # Brand selection dropdown
                avail_brands = {}
                for b in ["Million Classic", "GM Cables", "Fast Cables", "Newage Cables"]:
                    val = item[f"{b} (PKR)"]
                    if pd.notna(val) and val > 0:
                        avail_brands[f"{b} — Rs. {val:,.0f}"] = (b, val)
                
                if avail_brands:
                    selected_brand_key = st.selectbox(
                        "Manufacturer Brand:", 
                        list(avail_brands.keys()), 
                        key=f"select_{item['Specification / Subcategory']}_{i}_{idx}"
                    )
                    b_name, b_price = avail_brands[selected_brand_key]
                    
                    qty = st.number_input("Quantity:", min_value=1, value=1, key=f"qty_{item['Specification / Subcategory']}_{i}_{idx}")
                    
                    if st.button("🛒 Add to Cart", key=f"btn_{item['Specification / Subcategory']}_{i}_{idx}", use_container_width=True):
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
                        time.sleep(0.3)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MODE 2: MULTI-BRAND COMPARISON MATRIX
# -----------------------------------------------------------------------------
elif nav_mode == "📊 Multi-Brand Price Comparison":
    st.title("📊 Multi-Brand Price Comparison Matrix")
    st.caption("Live rate comparison across Pakistan's leading certified cable manufacturers")
    
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
# MODE 3: CART & CHECKOUT
# -----------------------------------------------------------------------------
elif nav_mode == "🛒 Cart & B2B Checkout":
    st.title("🛒 Shopping Cart & B2B Proforma Invoice")
    
    if not st.session_state.cart:
        st.info("Your shopping cart is empty. Return to the Online Store to add products.")
    else:
        cart_df = pd.DataFrame(st.session_state.cart)
        
        st.dataframe(cart_df[["Category", "Specification", "Unit", "Brand", "UnitPrice", "Quantity", "TotalPrice"]].style.format({
            "UnitPrice": "Rs. {:,.0f}",
            "TotalPrice": "Rs. {:,.0f}"
        }), use_container_width=True)
        
        subtotal = cart_df["TotalPrice"].sum()
        total_quantity = cart_df["Quantity"].sum()
        
        # Bulk Discount Logic
        discount_rate = 0.0
        if total_quantity >= 50:
            discount_rate = 0.07
        elif total_quantity >= 20:
            discount_rate = 0.05
        elif total_quantity >= 5:
            discount_rate = 0.035
            
        discount_amount = subtotal * discount_rate
        net_total = subtotal - discount_amount
        
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### Subtotal: **Rs. {subtotal:,.0f}**")
            if discount_rate > 0:
                st.markdown(f"### Volume Discount ({discount_rate*100:.1f}%): **- Rs. {discount_amount:,.0f}**")
            st.markdown(f"# Net Payable: **Rs. {net_total:,.0f}**")
            
        with col2:
            st.markdown("### 🏢 Business Order Details")
            comp_name = st.text_input("Company / Project Name")
            contact_person = st.text_input("Contact Person & Phone")
            
            if st.button("📄 Generate B2B Proforma Quote", use_container_width=True):
                if comp_name and contact_person:
                    st.success("Invoice generated successfully!")
                    st.balloons()
                    
                    quote_io = io.StringIO()
                    cart_df.to_csv(quote_io, index=False)
                    st.download_button(
                        label="📥 Download Proforma Invoice (CSV)",
                        data=quote_io.getvalue(),
                        file_name=f"Rehman_Cable_Quote_{comp_name.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Please enter Company Name and Contact details.")

        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = []
            st.rerun()

# -----------------------------------------------------------------------------
# MODE 4: ADMIN PRICE PORTAL
# -----------------------------------------------------------------------------
elif nav_mode == "⚙️ Admin Price Portal":
    st.title("⚙️ Admin Price Management")
    st.caption("Upload updated price lists directly to sync the entire store.")
    
    uploaded_file = st.file_uploader("Upload Price Comparison Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            new_df = pd.read_excel(uploaded_file, skiprows=3)
            st.write("Uploaded Sheet Preview:")
            st.dataframe(new_df.head(10))
            
            if st.button("🚀 Publish Prices to Store"):
                st.session_state.catalog_df = load_default_data()
                st.success("Store prices updated successfully!")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing file: {e}")

# Footer
st.divider()
st.caption("© 2026 Rehman Cables eStore | Authorized Electrical Distribution Partner | All rights reserved.")