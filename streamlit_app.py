import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import io
import os

def process_pdf(input_bytes, target_rgb, threshold=100, zoom=3.0):
    """
    Converts dark pixels in a PDF to a user-specified RGB color.
    """
    doc = fitz.open("pdf", input_bytes)
    out_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        data = np.array(img)
        
        r, g, b = data[:,:,0], data[:,:,1], data[:,:,2]
        dark_mask = (r < threshold) & (g < threshold) & (b < threshold)
        
        # Replace dark pixels with the chosen RGB color
        data[:,:,0][dark_mask] = target_rgb[0]  # Red
        data[:,:,1][dark_mask] = target_rgb[1]  # Green
        data[:,:,2][dark_mask] = target_rgb[2]  # Blue
        
        processed_img = Image.fromarray(data)
        
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PDF', resolution=72.0 * zoom)
        img_pdf_bytes = img_byte_arr.getvalue()
        
        img_doc = fitz.open("pdf", img_pdf_bytes)
        out_doc.insert_pdf(img_doc)
        
    out_bytes = out_doc.tobytes()
    doc.close()
    out_doc.close()
    return out_bytes

def hex_to_rgb(hex_color):
    """Converts a hex color string (e.g., '#0000FF') to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# --- Web App UI ---
st.set_page_config(page_title="Out of Black Ink!", page_icon="🖨️")

st.title("🖨️ The 'Out of Black Ink' Fixer")
st.write("Upload a PDF to turn all black text into a color of your choice, so you can keep printing!")

# Color Picker (Defaults to Blue)
chosen_color_hex = st.color_picker("Pick a replacement color", "#0000FF")

# File uploader
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    if st.button("Convert Document"):
        with st.spinner("Processing document... this might take a few seconds."):
            
            # 1. Convert the chosen Hex color to RGB
            target_rgb = hex_to_rgb(chosen_color_hex)
            
            # 2. Process the file with the new color
            processed_pdf_bytes = process_pdf(uploaded_file.read(), target_rgb=target_rgb)
            
            # 3. Generate the new file name based on the original
            original_name = os.path.splitext(uploaded_file.name)[0]
            new_file_name = f"Converted_{original_name}.pdf"
            
            st.success("Done! Your document is ready.")
            
            # 4. Download button with dynamic file name
            st.download_button(
                label=f"⬇️ Download {new_file_name}",
                data=processed_pdf_bytes,
                file_name=new_file_name,
                mime="application/pdf"
            )