import streamlit as st
import os
import pandas as pd
import database as db
from PIL import Image as PILImage
import base64
from io import BytesIO
import export_utils

def show_dashboard_page():
    """
    Display the customizable dashboard with pinned favorite images
    """
    st.title("📌 Custom Dashboard")
    st.write("Pin your favorite analysis results and customize your dashboard view")
    
    # Get all favorites
    favorites = db.get_all_favorites()
    
    if not favorites:
        st.info("Your dashboard is empty. Add favorites from the analysis results to build your dashboard.")
        st.markdown("""
        ### How to use the dashboard:
        1. Browse image analysis results in the History or Search pages
        2. Click on an image to view its details
        3. Click "Add to Favorites" to pin it to your dashboard
        4. Customize labels, notes and order on the dashboard
        """)
        return
    
    # Dashboard layout
    dashboard_layout = st.radio(
        "Dashboard Layout",
        options=["Grid View", "List View", "Details View"],
        horizontal=True,
        index=0
    )
    
    # Add buttons for managing dashboard
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        add_new = st.button("Add New Favorite", use_container_width=True)
    with col2:
        reorder = st.button("Reorder Favorites", use_container_width=True)
    with col3:
        export_dashboard = st.button("Export Dashboard", use_container_width=True)
    
    if add_new:
        show_add_favorite_dialog()
        return
    
    if reorder:
        show_reorder_dialog(favorites)
        return
    
    if export_dashboard:
        export_dashboard_data(favorites)
        return
    
    # Display favorites based on selected layout
    if dashboard_layout == "Grid View":
        display_grid_layout(favorites)
    elif dashboard_layout == "List View":
        display_list_layout(favorites)
    else:  # Details View
        display_details_layout(favorites)

def display_grid_layout(favorites):
    """
    Display favorites in a grid layout
    """
    # Calculate number of columns based on number of favorites
    num_items = len(favorites)
    if num_items <= 3:
        num_cols = num_items
    else:
        num_cols = 3
    
    # Create columns
    cols = st.columns(num_cols)
    
    # Display favorites in grid
    for i, favorite in enumerate(favorites):
        image = favorite.image
        col_idx = i % num_cols
        
        with cols[col_idx]:
            # Display card
            st.subheader(favorite.custom_label or image.object_name or "Untitled")
            
            # Display image if it exists
            if os.path.exists(image.file_path):
                try:
                    img = PILImage.open(image.file_path)
                    st.image(img, use_column_width=True)
                except Exception as e:
                    st.error(f"Could not load image: {e}")
            else:
                st.warning("Image file not found")
            
            # Display basic info
            st.caption(f"Confidence: {image.confidence:.2f}")
            
            # Actions
            if st.button(f"View Details", key=f"view_{favorite.id}"):
                st.session_state.selected_favorite_id = favorite.id
                show_favorite_details(favorite.id)
                st.rerun()
            
            # Remove from favorites
            if st.button(f"Remove", key=f"remove_{favorite.id}"):
                db.remove_from_favorites(favorite.id)
                st.success("Removed from favorites")
                st.rerun()

def display_list_layout(favorites):
    """
    Display favorites in a list layout
    """
    for i, favorite in enumerate(favorites):
        image = favorite.image
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            # Display image
            with col1:
                if os.path.exists(image.file_path):
                    try:
                        img = PILImage.open(image.file_path)
                        st.image(img, use_column_width=True)
                    except Exception as e:
                        st.error(f"Could not load image: {e}")
                else:
                    st.warning("Image file not found")
            
            # Display info
            with col2:
                st.subheader(favorite.custom_label or image.object_name or "Untitled")
                st.write(image.description[:150] + "..." if len(image.description) > 150 else image.description)
                if favorite.note:
                    st.info(favorite.note)
                
                metadata = ""
                if image.camera_make:
                    metadata += f"Camera: {image.camera_make} {image.camera_model or ''}"
                if image.width and image.height:
                    metadata += f" | Dimensions: {image.width}x{image.height}"
                
                st.caption(metadata if metadata else "No metadata available")
            
            # Actions
            with col3:
                st.caption(f"Confidence: {image.confidence:.2f}")
                
                if st.button(f"View Details", key=f"view_{favorite.id}"):
                    st.session_state.selected_favorite_id = favorite.id
                    show_favorite_details(favorite.id)
                    st.rerun()
                
                if st.button(f"Edit", key=f"edit_{favorite.id}"):
                    st.session_state.edit_favorite_id = favorite.id
                    show_edit_favorite_dialog(favorite.id)
                    st.rerun()
                
                if st.button(f"Remove", key=f"remove_{favorite.id}"):
                    db.remove_from_favorites(favorite.id)
                    st.success("Removed from favorites")
                    st.rerun()
            
            st.divider()

def display_details_layout(favorites):
    """
    Display favorites with expanded details
    """
    for favorite in favorites:
        image = favorite.image
        
        with st.expander(favorite.custom_label or image.object_name or "Untitled", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Display image
                if os.path.exists(image.file_path):
                    try:
                        img = PILImage.open(image.file_path)
                        st.image(img, use_column_width=True)
                    except Exception as e:
                        st.error(f"Could not load image: {e}")
                else:
                    st.warning("Image file not found")
            
            with col2:
                # Display info
                st.write("### Description")
                st.write(image.description)
                
                if favorite.note:
                    st.write("### Note")
                    st.info(favorite.note)
                
                st.write("### Details")
                st.write(f"**Object:** {image.object_name}")
                st.write(f"**Confidence:** {image.confidence:.2f}")
                st.write(f"**File:** {image.file_name}")
                
                # Display metadata if available
                if image.metadata_json:
                    st.write("### Metadata")
                    metadata_table = {
                        "Property": [],
                        "Value": []
                    }
                    
                    if image.width and image.height:
                        metadata_table["Property"].append("Dimensions")
                        metadata_table["Value"].append(f"{image.width}x{image.height}")
                    
                    if image.camera_make:
                        metadata_table["Property"].append("Camera Make")
                        metadata_table["Value"].append(image.camera_make)
                    
                    if image.camera_model:
                        metadata_table["Property"].append("Camera Model")
                        metadata_table["Value"].append(image.camera_model)
                    
                    if image.date_taken:
                        metadata_table["Property"].append("Date Taken")
                        metadata_table["Value"].append(image.date_taken)
                    
                    if image.focal_length:
                        metadata_table["Property"].append("Focal Length")
                        metadata_table["Value"].append(f"{image.focal_length}mm")
                    
                    if image.aperture:
                        metadata_table["Property"].append("Aperture")
                        metadata_table["Value"].append(f"f/{image.aperture}")
                    
                    if image.iso_speed:
                        metadata_table["Property"].append("ISO")
                        metadata_table["Value"].append(image.iso_speed)
                    
                    if image.file_size:
                        metadata_table["Property"].append("File Size")
                        metadata_table["Value"].append(f"{image.file_size/1024:.1f} KB")
                    
                    if image.file_type:
                        metadata_table["Property"].append("File Type")
                        metadata_table["Value"].append(image.file_type)
                    
                    if metadata_table["Property"]:
                        st.table(pd.DataFrame(metadata_table))
            
            # Actions
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button(f"View Full Details", key=f"view_{favorite.id}"):
                    st.session_state.selected_favorite_id = favorite.id
                    show_favorite_details(favorite.id)
                    st.rerun()
            
            with col2:
                if st.button(f"Edit", key=f"edit_{favorite.id}"):
                    st.session_state.edit_favorite_id = favorite.id
                    show_edit_favorite_dialog(favorite.id)
                    st.rerun()
            
            with col3:
                if st.button(f"Remove", key=f"remove_{favorite.id}"):
                    db.remove_from_favorites(favorite.id)
                    st.success("Removed from favorites")
                    st.rerun()

def show_favorite_details(favorite_id):
    """
    Show detailed view of a favorite image
    """
    favorite = db.get_favorite_by_id(favorite_id)
    if not favorite:
        st.error("Favorite not found")
        return
    
    image = favorite.image
    
    st.title(favorite.custom_label or image.object_name or "Untitled")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_favorite_id = None
        st.rerun()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display image
        if os.path.exists(image.file_path):
            try:
                img = PILImage.open(image.file_path)
                st.image(img, use_column_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        else:
            st.warning("Image file not found")
    
    with col2:
        # Display note if available
        if favorite.note:
            st.info(favorite.note)
        
        # Display description
        st.subheader("Description")
        st.write(image.description)
        
        # Display object and confidence
        st.subheader("Analysis Results")
        st.write(f"**Object:** {image.object_name}")
        st.write(f"**Confidence:** {image.confidence:.2f}")
        
        # Display file info
        st.subheader("File Information")
        st.write(f"**File Name:** {image.file_name}")
        st.write(f"**Full Path:** {image.file_path}")
        st.write(f"**Folder:** {image.folder.name}")
        
        # Display pinned status
        st.subheader("Dashboard Status")
        st.write(f"**Custom Label:** {favorite.custom_label or 'None'}")
        st.write(f"**Display Order:** {favorite.display_order}")
        st.write(f"**Added on:** {favorite.added_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display metadata if available
    if image.metadata_json:
        st.subheader("Image Metadata")
        metadata_table = {
            "Property": [],
            "Value": []
        }
        
        if image.width and image.height:
            metadata_table["Property"].append("Dimensions")
            metadata_table["Value"].append(f"{image.width}x{image.height}")
        
        if image.camera_make:
            metadata_table["Property"].append("Camera Make")
            metadata_table["Value"].append(image.camera_make)
        
        if image.camera_model:
            metadata_table["Property"].append("Camera Model")
            metadata_table["Value"].append(image.camera_model)
        
        if image.date_taken:
            metadata_table["Property"].append("Date Taken")
            metadata_table["Value"].append(image.date_taken)
        
        if image.focal_length:
            metadata_table["Property"].append("Focal Length")
            metadata_table["Value"].append(f"{image.focal_length}mm")
        
        if image.exposure_time:
            metadata_table["Property"].append("Exposure Time")
            metadata_table["Value"].append(image.exposure_time)
        
        if image.aperture:
            metadata_table["Property"].append("Aperture")
            metadata_table["Value"].append(f"f/{image.aperture}")
        
        if image.iso_speed:
            metadata_table["Property"].append("ISO")
            metadata_table["Value"].append(image.iso_speed)
        
        if image.gps_latitude and image.gps_longitude:
            metadata_table["Property"].append("GPS Location")
            metadata_table["Value"].append(f"{image.gps_latitude}, {image.gps_longitude}")
        
        if image.file_size:
            metadata_table["Property"].append("File Size")
            metadata_table["Value"].append(f"{image.file_size/1024:.1f} KB")
        
        if image.file_type:
            metadata_table["Property"].append("File Type")
            metadata_table["Value"].append(image.file_type)
        
        if metadata_table["Property"]:
            st.table(pd.DataFrame(metadata_table))
    
    # Actions
    st.subheader("Actions")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Edit Favorite Details"):
            st.session_state.edit_favorite_id = favorite.id
            show_edit_favorite_dialog(favorite.id)
            st.rerun()
    
    with col2:
        if st.button("Export Details"):
            show_export_options([image])
    
    with col3:
        if st.button("Remove from Favorites"):
            db.remove_from_favorites(favorite.id)
            st.session_state.selected_favorite_id = None
            st.success("Removed from favorites")
            st.rerun()

def show_edit_favorite_dialog(favorite_id):
    """
    Show dialog to edit favorite details
    """
    favorite = db.get_favorite_by_id(favorite_id)
    if not favorite:
        st.error("Favorite not found")
        return
    
    image = favorite.image
    
    st.title("Edit Favorite")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.edit_favorite_id = None
        st.rerun()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display image
        if os.path.exists(image.file_path):
            try:
                img = PILImage.open(image.file_path)
                st.image(img, use_column_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        else:
            st.warning("Image file not found")
        
        st.write(f"**Object:** {image.object_name}")
        st.write(f"**File:** {image.file_name}")
    
    with col2:
        # Edit form
        with st.form("edit_favorite_form"):
            # Custom label
            custom_label = st.text_input(
                "Custom Label", 
                value=favorite.custom_label or image.object_name or ""
            )
            
            # Note
            note = st.text_area(
                "Note", 
                value=favorite.note or "",
                placeholder="Add a note about why this image is important"
            )
            
            # Display order
            display_order = st.number_input(
                "Display Order", 
                value=favorite.display_order,
                min_value=0,
                help="Lower numbers appear first in the dashboard"
            )
            
            # Submit button
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                # Update favorite
                updated = db.update_favorite_details(favorite.id, custom_label, note)
                db.update_favorite_order(favorite.id, display_order)
                
                if updated:
                    st.success("Favorite updated successfully")
                    st.session_state.edit_favorite_id = None
                    st.rerun()
                else:
                    st.error("Failed to update favorite")

def show_add_favorite_dialog():
    """
    Show dialog to add a new favorite
    """
    st.title("Add to Favorites")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.rerun()
    
    # Get all images not already favorited
    db_session = db.get_db()
    subquery = db_session.query(db.FavoriteImage.image_id)
    unfavorited_images = db_session.query(db.Image).filter(
        ~db.Image.id.in_(subquery)
    ).order_by(db.Image.processed_at.desc()).all()
    
    if not unfavorited_images:
        st.info("All images have already been added to favorites")
        return
    
    # Filter options
    folder_filter = st.selectbox(
        "Filter by Folder",
        options=[("All Folders", None)] + [(f.name, f.id) for f in db.get_all_folders()],
        format_func=lambda x: x[0]
    )
    
    # Filter images by folder if selected
    if folder_filter[1] is not None:
        filtered_images = [img for img in unfavorited_images if img.folder_id == folder_filter[1]]
    else:
        filtered_images = unfavorited_images
    
    if not filtered_images:
        st.info("No unfavorited images in this folder")
        return
    
    # Display images in a grid
    num_cols = 3
    cols = st.columns(num_cols)
    
    for i, image in enumerate(filtered_images):
        col_idx = i % num_cols
        
        with cols[col_idx]:
            # Display card
            st.subheader(image.object_name or "Untitled")
            
            # Display image if it exists
            if os.path.exists(image.file_path):
                try:
                    img = PILImage.open(image.file_path)
                    st.image(img, use_column_width=True)
                except Exception as e:
                    st.error(f"Could not load image: {e}")
            else:
                st.warning("Image file not found")
            
            # Display basic info
            st.caption(f"Confidence: {image.confidence:.2f}")
            
            # Add to favorites button
            if st.button(f"Add to Dashboard", key=f"add_{image.id}"):
                show_create_favorite_form(image.id)
                st.rerun()

def show_create_favorite_form(image_id):
    """
    Show form to create a new favorite
    """
    image = db.get_db().query(db.Image).filter(db.Image.id == image_id).first()
    if not image:
        st.error("Image not found")
        return
    
    st.title("Add to Dashboard")
    
    # Back button
    if st.button("← Back to Image Selection"):
        st.rerun()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display image
        if os.path.exists(image.file_path):
            try:
                img = PILImage.open(image.file_path)
                st.image(img, use_column_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        else:
            st.warning("Image file not found")
        
        st.write(f"**Object:** {image.object_name}")
        st.write(f"**File:** {image.file_name}")
    
    with col2:
        # Edit form
        with st.form("create_favorite_form"):
            # Custom label
            custom_label = st.text_input(
                "Custom Label", 
                value=image.object_name or ""
            )
            
            # Note
            note = st.text_area(
                "Note", 
                value="",
                placeholder="Add a note about why this image is important"
            )
            
            # Display order
            display_order = st.number_input(
                "Display Order", 
                value=0,
                min_value=0,
                help="Lower numbers appear first in the dashboard"
            )
            
            # Submit button
            submitted = st.form_submit_button("Add to Dashboard")
            
            if submitted:
                # Create favorite
                try:
                    favorite = db.add_to_favorites(image.id, custom_label, note, display_order)
                    if favorite:
                        st.success("Added to dashboard successfully")
                        st.rerun()
                    else:
                        st.error("Failed to add to dashboard")
                except Exception as e:
                    st.error(f"Error adding to dashboard: {e}")

def show_reorder_dialog(favorites):
    """
    Show dialog to reorder favorites
    """
    st.title("Reorder Dashboard Items")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.rerun()
    
    st.write("Drag and drop to reorder your dashboard items. Lower numbers appear first.")
    
    # Create a form for reordering
    with st.form("reorder_form"):
        order_changes = {}
        
        for i, favorite in enumerate(favorites):
            image = favorite.image
            
            col1, col2, col3 = st.columns([2, 4, 1])
            
            with col1:
                # Display image thumbnail
                if os.path.exists(image.file_path):
                    try:
                        img = PILImage.open(image.file_path)
                        st.image(img, width=100)
                    except Exception as e:
                        st.error(f"Could not load image: {e}")
                else:
                    st.warning("Image file not found")
            
            with col2:
                st.write(f"**{favorite.custom_label or image.object_name or 'Untitled'}**")
                if favorite.note:
                    st.caption(favorite.note[:50] + "..." if len(favorite.note) > 50 else favorite.note)
            
            with col3:
                # Order input
                new_order = st.number_input(
                    f"Order",
                    value=favorite.display_order,
                    min_value=0,
                    key=f"order_{favorite.id}"
                )
                order_changes[favorite.id] = new_order
        
        # Submit button
        submitted = st.form_submit_button("Save Order")
        
        if submitted:
            # Update order
            for fav_id, order in order_changes.items():
                db.update_favorite_order(fav_id, order)
            
            st.success("Dashboard order updated")
            st.rerun()

def export_dashboard_data(favorites):
    """
    Export dashboard data to various formats
    """
    st.title("Export Dashboard")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.rerun()
    
    # Prepare export data
    export_data = []
    
    for favorite in favorites:
        image = favorite.image
        
        # Create row
        row = {
            "Label": favorite.custom_label or image.object_name or "Untitled",
            "Object": image.object_name,
            "Description": image.description,
            "Note": favorite.note or "",
            "Confidence": image.confidence,
            "File Name": image.file_name,
            "File Path": image.file_path,
            "Folder": image.folder.name,
            "Width": image.width,
            "Height": image.height,
            "Camera Make": image.camera_make,
            "Camera Model": image.camera_model,
            "Date Taken": image.date_taken,
            "File Size": image.file_size,
            "File Type": image.file_type,
            "Display Order": favorite.display_order,
            "Added On": favorite.added_at
        }
        
        export_data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(export_data)
    
    # Select export format
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel", "PDF Simple", "PDF Detailed"]
    )
    
    # Include images option (for PDF)
    include_images = False
    if export_format in ["PDF Detailed"]:
        include_images = st.checkbox("Include Images", value=True)
    
    # Export button
    if st.button("Export"):
        if export_format == "CSV":
            export_filename = export_utils.export_to_csv(df, "dashboard")
            st.success(f"Dashboard exported to CSV: {export_filename}")
        
        elif export_format == "Excel":
            export_filename = export_utils.export_to_excel(df, "dashboard")
            st.success(f"Dashboard exported to Excel: {export_filename}")
        
        elif export_format == "PDF Simple":
            export_filename = export_utils.export_to_pdf_simple(df, "dashboard")
            st.success(f"Dashboard exported to PDF: {export_filename}")
        
        elif export_format == "PDF Detailed":
            # Get image paths for detailed PDF
            image_paths = []
            if include_images:
                image_paths = [img.image.file_path for img in favorites if os.path.exists(img.image.file_path)]
            
            export_filename = export_utils.export_to_pdf_detailed(df, "dashboard", include_images)
            st.success(f"Dashboard exported to detailed PDF: {export_filename}")
        
        # Download the exported file
        if export_filename and os.path.exists(export_filename):
            with open(export_filename, "rb") as file:
                file_ext = os.path.splitext(export_filename)[1]
                
                if file_ext == ".csv":
                    mime = "text/csv"
                elif file_ext == ".xlsx":
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif file_ext == ".pdf":
                    mime = "application/pdf"
                else:
                    mime = "application/octet-stream"
                
                st.download_button(
                    label=f"Download {export_format} File",
                    data=file,
                    file_name=os.path.basename(export_filename),
                    mime=mime
                )

def show_export_options(images):
    """
    Show options for exporting data for a single image
    """
    # Prepare data
    export_data = []
    
    for image in images:
        # Create row
        row = {
            "Object": image.object_name,
            "Description": image.description,
            "Confidence": image.confidence,
            "File Name": image.file_name,
            "File Path": image.file_path,
            "Folder": image.folder.name,
            "Width": image.width,
            "Height": image.height,
            "Camera Make": image.camera_make,
            "Camera Model": image.camera_model,
            "Date Taken": image.date_taken,
            "File Size": image.file_size,
            "File Type": image.file_type
        }
        
        export_data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(export_data)
    
    # Select export format
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel", "PDF Simple", "PDF Detailed"]
    )
    
    # Include images option (for PDF)
    include_images = False
    if export_format in ["PDF Detailed"]:
        include_images = st.checkbox("Include Images", value=True)
    
    # Export button
    if st.button("Export"):
        if export_format == "CSV":
            export_filename = export_utils.export_to_csv(df, "image_details")
            st.success(f"Details exported to CSV: {export_filename}")
        
        elif export_format == "Excel":
            export_filename = export_utils.export_to_excel(df, "image_details")
            st.success(f"Details exported to Excel: {export_filename}")
        
        elif export_format == "PDF Simple":
            export_filename = export_utils.export_to_pdf_simple(df, "image_details")
            st.success(f"Details exported to PDF: {export_filename}")
        
        elif export_format == "PDF Detailed":
            # Get image paths for detailed PDF
            image_paths = []
            if include_images:
                image_paths = [img.file_path for img in images if os.path.exists(img.file_path)]
            
            export_filename = export_utils.export_to_pdf_detailed(df, "image_details", include_images)
            st.success(f"Details exported to detailed PDF: {export_filename}")
        
        # Download the exported file
        if export_filename and os.path.exists(export_filename):
            with open(export_filename, "rb") as file:
                file_ext = os.path.splitext(export_filename)[1]
                
                if file_ext == ".csv":
                    mime = "text/csv"
                elif file_ext == ".xlsx":
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif file_ext == ".pdf":
                    mime = "application/pdf"
                else:
                    mime = "application/octet-stream"
                
                st.download_button(
                    label=f"Download {export_format} File",
                    data=file,
                    file_name=os.path.basename(export_filename),
                    mime=mime
                )

# Main section for direct testing
if __name__ == "__main__":
    show_dashboard_page()