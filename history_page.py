import streamlit as st
import os
import pandas as pd
from database import get_all_folders, get_images_by_folder_id
from export_utils import export_to_csv, export_to_excel, export_to_pdf_simple, export_to_pdf_detailed

def show_history_page():
    """
    Display the history of processed folders and allow browsing previous analysis results
    """
    st.header("Analysis History")
    st.write("Browse previously analyzed image folders")
    
    # Get all folders from the database
    folders = get_all_folders()
    
    if not folders:
        st.info("No analyzed folders found in the database. Process some images first.")
        return
    
    # Convert to DataFrame for better display
    folder_data = [{
        "id": folder.id,
        "name": folder.name, 
        "path": folder.path, 
        "processed_at": folder.processed_at,
        "image_count": len(folder.images)
    } for folder in folders]
    
    folder_df = pd.DataFrame(folder_data)
    
    # Sort by most recent first
    folder_df = folder_df.sort_values(by="processed_at", ascending=False)
    
    # Display as a table
    st.dataframe(
        folder_df[["name", "processed_at", "image_count"]],
        column_config={
            "name": "Folder Name",
            "processed_at": st.column_config.DatetimeColumn("Processed Date", format="MMM DD, YYYY, hh:mm A"),
            "image_count": st.column_config.NumberColumn("Images")
        },
        hide_index=True
    )
    
    # Let user select a folder to view details
    selected_folder_id = st.selectbox(
        "Select a folder to view images",
        options=folder_df["id"].tolist(),
        format_func=lambda x: folder_df[folder_df["id"] == x]["name"].iloc[0]
    )
    
    if selected_folder_id:
        show_folder_images(selected_folder_id)
    
def show_folder_images(folder_id):
    """
    Display all images from a specific folder
    """
    # Get all images for the folder
    images = get_images_by_folder_id(folder_id)
    
    if not images:
        st.warning("No images found for this folder")
        return
    
    # Convert to DataFrame for better display
    image_data = [{
        "id": img.id,
        "file_name": img.file_name, 
        "object_name": img.object_name, 
        "confidence": img.confidence,
        "processed_at": img.processed_at
    } for img in images]
    
    image_df = pd.DataFrame(image_data)
    
    # Sort alphabetically by filename
    image_df = image_df.sort_values(by="file_name")
    
    # Display as a table
    st.dataframe(
        image_df[["file_name", "object_name", "confidence", "processed_at"]],
        column_config={
            "file_name": "Image Name",
            "object_name": "Object Identified",
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
            "processed_at": st.column_config.DatetimeColumn("Processed Date", format="MMM DD, YYYY, hh:mm A")
        },
        hide_index=True
    )
    
    # Add export options
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Export Format", 
                                    ["CSV", "Excel", "PDF (Simple)", "PDF (Detailed)"],
                                    key="history_export_format")
    
    with col2:
        if export_format.startswith("PDF"):
            include_images = st.checkbox("Include Images in PDF", value=True, 
                                        help="Include image previews in the PDF export (may increase file size)",
                                        key="history_include_images")
    
    if st.button("Export Results", key="history_export_button"):
        # Construct a proper dataframe for export with all fields
        export_data = []
        for img in images:
            export_data.append({
                "file_name": img.file_name,
                "file_path": img.file_path,
                "object_name": img.object_name,
                "description": img.description,
                "confidence": img.confidence,
                "processed_at": img.processed_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        export_df = pd.DataFrame(export_data)
        folder_name = images[0].folder.name if images and images[0].folder else "folder"
        
        if export_format == "CSV":
            export_filename = export_to_csv(export_df, folder_name)
            st.success(f"Results exported to {export_filename}")
            
        elif export_format == "Excel":
            export_filename = export_to_excel(export_df, folder_name)
            st.success(f"Results exported to {export_filename}")
            
        elif export_format == "PDF (Simple)":
            with st.spinner("Generating PDF..."):
                export_filename = export_to_pdf_simple(export_df, folder_name)
            st.success(f"Results exported to {export_filename}")
            
        elif export_format == "PDF (Detailed)":
            with st.spinner("Generating detailed PDF report with images..."):
                include_imgs = include_images if 'include_images' in locals() else True
                export_filename = export_to_pdf_detailed(export_df, folder_name, include_imgs)
            st.success(f"Results exported to {export_filename}")
        
        # Provide download link
        with open(export_filename, "rb") as file:
            btn = st.download_button(
                label="Download File",
                data=file,
                file_name=os.path.basename(export_filename),
                mime="application/octet-stream",
                key="history_download_button"
            )

    # Let user select an image to view details
    st.subheader("View Image Details")
    selected_image_id = st.selectbox(
        "Select an image to view details",
        options=image_df["id"].tolist(),
        format_func=lambda x: image_df[image_df["id"] == x]["file_name"].iloc[0]
    )
    
    if selected_image_id:
        show_image_details(selected_image_id)

def show_image_details(image_id):
    """
    Display details for a specific image
    """
    # Find the image in the database
    from database import get_db, Image
    
    db = next(get_db())
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        st.error("Image not found")
        return
    
    # Display image details
    col1, col2 = st.columns([1, 2])
    
    # Check if file exists first
    if os.path.exists(image.file_path):
        with col1:
            st.subheader("Image")
            st.image(image.file_path, use_column_width=True)
    else:
        with col1:
            st.subheader("Image")
            st.warning("Image file not found at path: " + image.file_path)
    
    with col2:
        st.subheader("Analysis Results")
        st.markdown(f"**File:** {image.file_name}")
        st.markdown(f"**Object Identified:** {image.object_name}")
        st.markdown(f"**Confidence:** {image.confidence:.2f}")
        st.markdown("### Description")
        st.markdown(image.description)
        
        # Additional metadata
        st.markdown("### Metadata")
        st.markdown(f"**Processed Date:** {image.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Full Path:** {image.file_path}")