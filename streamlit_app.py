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

# --- 2. UPLOAD & ORIENTATION ---
uploaded_file = st.file_uploader("Upload Target Photo", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img_orig = Image.open(uploaded_file)
    img_orig = ImageOps.exif_transpose(img_orig).convert("RGB")
    width, height = img_orig.size
    
    st.subheader("1. Align the Crosshairs")

    # Creating a layout: [Left Slider] [Image] [Right Slider]
    col_left, col_img, col_right = st.columns([1, 4, 1])

    with col_left:
        st.write("🔵")
        # Inverting slider so 100 is at the top (more natural for archery)
        gy_raw = st.select_slider("Gold Y", options=list(range(100, -1, -1)), value=50, key="gy")
        st.caption("Gold Up/Down")

    with col_img:
        # We define positions here so they update live
        gx = st.slider("Gold Horizontal", 0, 100, 50, key="gx")
        rx = st.slider("Group Horizontal", 0, 100, 55, key="rx")
        
        # Draw on a copy of the image
        img_draw = img_orig.copy()
        draw = ImageDraw.Draw(img_draw)
        
        def draw_cross(draw_obj, x_pct, y_pct, color):
            x, y = (x_pct / 100) * width, (y_pct / 100) * height
            draw_obj.line([(x-60, y), (x+60, y)], fill="black", width=12)
            draw_obj.line([(x, y-60), (x, y+60)], fill="black", width=12)
            draw_obj.line([(x-50, y), (x+50, y)], fill=color, width=8)
            draw_obj.line([(x, y-50), (x, y+50)], fill=color, width=8)

        draw_cross(draw, gx, gy_raw, "blue")
        draw_cross(draw, rx, 45, "red") # Placeholder for Red Y while setting up logic
        
        # We need the actual Red Y from the right column, so we define it before drawing
        # But since Streamlit runs top-down, we'll use session_state or a simple order tweak
        
    with col_right:
        st.write("🔴")
        ry_raw = st.select_slider("Group Y", options=list(range(100, -1, -1)), value=45, key="ry")
        st.caption("Group Up/Down")

    # Re-draw with the correct RY now that we have it
    draw_cross(draw, rx, ry_raw, "red")
    col_img.image(img_draw, width='stretch')

    # --- 3. CALCULATION ---
    if st.button("Calculate Adjustment", type="primary"):
        pix_per_cm = width / target_size_cm
        dx_pix = ((rx/100)*width) - ((gx/100)*width)
        # Using the raw values directly
        dy_pix = ((gy_raw/100)*height) - ((ry_raw/100)*height) 
        
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
