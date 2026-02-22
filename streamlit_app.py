import streamlit as st
from PIL import Image, ImageDraw, ImageOps

st.set_page_config(page_title="Archery Sight Master", layout="centered")

st.title("🎯 Archery Sight Adjuster")

# --- 1. SETTINGS ---
with st.sidebar:
    st.header("Setup")
    dist_m = st.number_input("Distance to Target (m)", value=25)
    sight_rad = st.number_input("Sight Extension (mm)", value=880)
    target_size_cm = st.selectbox("Face Size (cm)", [40, 60, 80, 122], index=0)

# --- 2. UPLOAD & FIX ROTATION ---
uploaded_file = st.file_uploader("Upload Target Photo", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # Open image
    img_orig = Image.open(uploaded_file)
    
    # FIX: This line reads the EXIF data and rotates the image to be upright
    img_orig = ImageOps.exif_transpose(img_orig).convert("RGB")
    
    width, height = img_orig.size
    
    st.subheader("1. Align the Crosshairs")
    
    col_sliders_a, col_sliders_b = st.columns(2)
    with col_sliders_a:
        st.write("🔵 **GOLD**")
        gx = st.slider("Gold Horizontal", 0, 100, 50, key="gx")
        gy = st.slider("Gold Vertical", 0, 100, 50, key="gy")
    with col_sliders_b:
        st.write("🔴 **GROUP**")
        rx = st.slider("Group Horizontal", 0, 100, 55, key="rx")
        ry = st.slider("Group Vertical", 0, 100, 45, key="ry")

    # Drawing
    draw = ImageDraw.Draw(img_orig)
    def draw_cross(draw_obj, x_pct, y_pct, color):
        x, y = (x_pct / 100) * width, (y_pct / 100) * height
        draw_obj.line([(x-60, y), (x+60, y)], fill="black", width=12)
        draw_obj.line([(x, y-60), (x, y+60)], fill="black", width=12)
        draw_obj.line([(x-50, y), (x+50, y)], fill=color, width=8)
        draw_obj.line([(x, y-50), (x, y+50)], fill=color, width=8)

    draw_cross(draw, gx, gy, "blue")
    draw_cross(draw, rx, ry, "red")

    st.image(img_orig, width='stretch')

    # --- 3. CALCULATION ---
    if st.button("Calculate Adjustment", type="primary"):
        # Scale logic
        pix_per_cm = width / target_size_cm
        dx_pix = ((rx/100)*width) - ((gx/100)*width)
        dy_pix = ((gy/100)*height) - ((ry/100)*height) 
        
        err_x_mm = (dx_pix / pix_per_cm) * 10
        err_y_mm = (dy_pix / pix_per_cm) * 10
        
        dist_mm = dist_m * 1000
        adj_x = (err_x_mm * sight_rad) / dist_mm
        adj_y = (err_y_mm * sight_rad) / dist_mm
        
        dir_x = "RIGHT" if adj_x > 0 else "LEFT"
        arrow_x = "➡️" if adj_x > 0 else "⬅️"
        dir_y = "DOWN" if adj_y > 0 else "UP"
        arrow_y = "⬇️" if adj_y > 0 else "⬆️"
        
        st.divider()
        st.subheader("🛠️ Range Instructions")

        def get_turns_and_clicks(mm_val):
            total_clicks = round(abs(mm_val) / 0.08)
            return int(total_clicks // 10), int(total_clicks % 10)

        tx, cx = get_turns_and_clicks(adj_x)
        ty, cy = get_turns_and_clicks(adj_y)

        res_a, res_b = st.columns(2)
        with res_a:
            st.warning("**WINDAGE**")
            st.markdown(f"## {arrow_x} {dir_x}\n**{tx} Turns**\n**{cx} Clicks**")
        with res_b:
            st.error("**ELEVATION**")
            st.markdown(f"## {arrow_y} {dir_y}\n**{ty} Turns**\n**{cy} Clicks**")
