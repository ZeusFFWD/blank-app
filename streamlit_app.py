import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(page_title="Archery Sight Master", layout="centered")

st.title("🎯 Archery Sight Adjuster")

# --- 1. SETTINGS ---
with st.sidebar:
    st.header("Setup")
    dist_m = st.number_input("Distance to Target (m)", value=25)
    sight_rad = st.number_input("Sight Extension (mm)", value=880)  # Set to your 880mm
    target_size_cm = st.selectbox("Face Size (cm)", [40, 60, 80, 122], index=0)
    st.divider()
    st.info("Follow the Error: If you hit high/right, move the sight pin up/right.")

# --- 2. UPLOAD ---
uploaded_file = st.file_uploader("Upload Target Photo", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # Open image
    img_orig = Image.open(uploaded_file).convert("RGB")
    width, height = img_orig.size
    
    st.subheader("1. Align the Crosshairs")
    
    # Gold Center (Blue)
    st.write("🔵 **Center the Blue Crosshair on the GOLD**")
    gx = st.slider("Gold Horizontal", 0, 100, 50, key="gx_slider")
    gy = st.slider("Gold Vertical", 0, 100, 50, key="gy_slider")
    
    # Group Center (Red)
    st.write("🔴 **Center the Red Crosshair on your GROUP**")
    rx = st.slider("Group Horizontal", 0, 100, 55, key="rx_slider")
    ry = st.slider("Group Vertical", 0, 100, 45, key="ry_slider")

    # Drawing the feedback
    draw = ImageDraw.Draw(img_orig)
    
    def draw_cross(draw_obj, x_pct, y_pct, color):
        x = (x_pct / 100) * width
        y = (y_pct / 100) * height
        draw_obj.line([(x-60, y), (x+60, y)], fill="black", width=12)
        draw_obj.line([(x, y-60), (x, y+60)], fill="black", width=12)
        draw_obj.line([(x-50, y), (x+50, y)], fill=color, width=8)
        draw_obj.line([(x, y-50), (x, y+50)], fill=color, width=8)

    draw_cross(draw, gx, gy, "blue")
    draw_cross(draw, rx, ry, "red")

    # Use 'stretch' as requested for container width
    st.image(img_orig, width='stretch')

    # --- 3. CALCULATION (Correctly Indented) ---
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
        
        # Directions and Arrows
        dir_x = "RIGHT" if adj_x > 0 else "LEFT"
        arrow_x = "➡️" if adj_x > 0 else "⬅️"
        
        dir_y = "DOWN" if adj_y > 0 else "UP"
        arrow_y = "⬇️" if adj_y > 0 else "⬆️"
        
        st.divider()
        st.subheader("🛠️ Range Instructions")

        # Avalon Tec X Logic: 1 Click = 0.08mm | 10 Clicks = 1 Full Turn
        def get_turns_and_clicks(mm_val):
            total_clicks = round(abs(mm_val) / 0.08)
            full_turns = total_clicks // 10
            remaining_clicks = total_clicks % 10
            return int(full_turns), int(remaining_clicks)

        tx, cx = get_turns_and_clicks(adj_x)
        ty, cy = get_turns_and_clicks(adj_y)

        col1, col2 = st.columns(2)
        with col1:
            st.warning("**WINDAGE**")
            st.markdown(f"## {arrow_x} {dir_x}")
            st.markdown(f"### {tx} Turns")
            st.markdown(f"### {cx} Clicks")

        with col2:
            st.error("**ELEVATION**")
            st.markdown(f"## {arrow_y} {dir_y}")
            st.markdown(f"### {ty} Turns")
            st.markdown(f"### {cy} Clicks")

        st.info("💡 Move your pin toward the arrow. One 'Click' is 1/10th of a full turn.")
