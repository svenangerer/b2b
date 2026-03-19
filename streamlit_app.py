import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import io

def process_pdf(input_bytes, threshold=100, zoom=3.0):
    # Open the uploaded PDF from memory
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
        
        data[:,:,0][dark_mask] = 0
        data[:,:,1][dark_mask] = 0
        data[:,:,2][dark_mask] = 255
        
        processed_img = Image.fromarray(data)
        
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PDF', resolution=72.0 * zoom)
        img_pdf_bytes = img_byte_arr.getvalue()
        
        img_doc = fitz.open("pdf", img_pdf_bytes)
        out_doc.insert_pdf(img_doc)
        
    # Return the new PDF as bytes
    out_bytes = out_doc.tobytes()
    doc.close()
    out_doc.close()
    return out_bytes

# --- Web App UI ---
st.set_page_config(page_title="Out of Black Ink!", page_icon="🖨️")

st.title("🖨️ The 'Out of Black Ink' Fixer")
st.write("Upload a PDF to turn all black text and dark pixels into blue, so you can print using your color cartridge!")

# File uploader
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    if st.button("Convert to Blue"):
        with st.spinner("Processing document... this might take a few seconds."):
            # Process the file
            processed_pdf_bytes = process_pdf(uploaded_file.read())
            
            st.success("Done! Your document is ready.")
            
            # Download button
            st.download_button(
                label="⬇️ Download Blue PDF",
                data=processed_pdf_bytes,
                file_name="blue_document.pdf",
                mime="application/pdf"
            )