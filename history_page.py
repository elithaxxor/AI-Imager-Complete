import streamlit as st
import os
import pandas as pd
from datetime import datetime
import database as db

def show_history_page():
    """
    Display the history of processed folders and allow browsing previous analysis results
    """
    st.title("Analysis History")
    st.write("Browse previously analyzed folders and view their results")
    
    # Get all folders from the database
    folders = db.get_all_folders()
    
    if not folders:
        st.info("No analysis history found. Process some image folders to see results here.")
        return
    
    # Create a dataframe for display
    folders_data = []
    for folder in folders:
        # Count images in folder
        image_count = len(db.get_images_by_folder_id(folder.id))
        
        folders_data.append({
            "id": folder.id,
            "name": folder.name,
            "path": folder.path,
            "processed_at": folder.processed_at,
            "image_count": image_count
        })
    
    folders_df = pd.DataFrame(folders_data)
    
    # Display as a table
    st.subheader("Processed Folders")
    
    # Format the dataframe for display
    display_df = folders_df.copy()
    display_df["processed_at"] = display_df["processed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    display_df["View Results"] = display_df.apply(
        lambda row: f'<a href="#" id="folder_{row["id"]}">View</a>', 
        axis=1
    )
    
    # Display the table with HTML
    st.write(
        display_df[["name", "image_count", "processed_at", "View Results"]]
        .rename(columns={
            "name": "Folder Name", 
            "image_count": "Images", 
            "processed_at": "Processed At"
        })
        .to_html(escape=False, index=False), 
        unsafe_allow_html=True
    )
    
    # JavaScript to handle clicks
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const links = document.querySelectorAll('a[id^="folder_"]');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const folderId = this.id.split('_')[1];
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: folderId
                }, '*');
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Use st.text_input as a hack to receive the clicked value
    clicked_folder_id = st.text_input("", key="clicked_folder_id", label_visibility="collapsed")
    
    # If a folder is selected, show its images
    if clicked_folder_id and clicked_folder_id.isdigit():
        folder_id = int(clicked_folder_id)
        show_folder_images(folder_id)

def show_folder_images(folder_id):
    """
    Display all images from a specific folder
    """
    # Get the folder
    db_session = db.SessionLocal()
    folder = db_session.query(db.Folder).filter(db.Folder.id == folder_id).first()
    
    if not folder:
        st.error("Folder not found")
        return
    
    st.subheader(f"Images in folder: {folder.name}")
    
    # Get all images for this folder
    images = db.get_images_by_folder_id(folder_id)
    
    if not images:
        st.info("No images found in this folder")
        return
    
    # Create a dataframe for display
    images_data = []
    for img in images:
        images_data.append({
            "id": img.id,
            "file_name": img.file_name,
            "file_path": img.file_path,
            "object_name": img.object_name,
            "confidence": img.confidence,
            "processed_at": img.processed_at
        })
    
    images_df = pd.DataFrame(images_data)
    
    # Format for display
    display_df = images_df.copy()
    display_df["processed_at"] = display_df["processed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    display_df["View Details"] = display_df.apply(
        lambda row: f'<a href="#" id="image_{row["id"]}">View</a>', 
        axis=1
    )
    
    # Display the table with HTML
    st.write(
        display_df[["file_name", "object_name", "confidence", "View Details"]]
        .rename(columns={
            "file_name": "File Name", 
            "object_name": "Object", 
            "confidence": "Confidence"
        })
        .to_html(escape=False, index=False), 
        unsafe_allow_html=True
    )
    
    # JavaScript to handle clicks
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const links = document.querySelectorAll('a[id^="image_"]');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const imageId = this.id.split('_')[1];
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: imageId
                }, '*');
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Use st.text_input as a hack to receive the clicked value
    clicked_image_id = st.text_input("", key="clicked_image_id", label_visibility="collapsed")
    
    # If an image is selected, show its details
    if clicked_image_id and clicked_image_id.isdigit():
        image_id = int(clicked_image_id)
        show_image_details(image_id)

def show_image_details(image_id):
    """
    Display details for a specific image
    """
    # Get the image
    db_session = db.SessionLocal()
    image = db_session.query(db.Image).filter(db.Image.id == image_id).first()
    
    if not image:
        st.error("Image not found")
        return
    
    st.subheader("Image Analysis Details")
    
    # Display image and details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Image")
        if os.path.exists(image.file_path):
            st.image(image.file_path, use_column_width=True)
        else:
            st.error("Image file not found at the stored path")
    
    with col2:
        st.subheader("Analysis Results")
        st.markdown(f"**File:** {image.file_name}")
        st.markdown(f"**Object Identified:** {image.object_name}")
        st.markdown(f"**Confidence:** {image.confidence:.2f}")
        st.markdown("### Description")
        st.markdown(image.description)
        st.markdown(f"**Processed at:** {image.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Export options
    st.subheader("Export This Analysis")
    
    export_format = st.selectbox("Export Format", ["CSV", "JSON"], key="single_export_format")
    
    if st.button("Export This Result"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_data = {
            "file_name": image.file_name,
            "file_path": image.file_path,
            "object_name": image.object_name,
            "description": image.description,
            "confidence": image.confidence,
            "processed_at": image.processed_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if export_format == "CSV":
            export_filename = f"image_analysis_{image.file_name}_{timestamp}.csv"
            pd.DataFrame([export_data]).to_csv(export_filename, index=False)
            st.success(f"Results exported to {export_filename}")
        else:
            export_filename = f"image_analysis_{image.file_name}_{timestamp}.json"
            pd.DataFrame([export_data]).to_json(export_filename, orient="records")
            st.success(f"Results exported to {export_filename}")