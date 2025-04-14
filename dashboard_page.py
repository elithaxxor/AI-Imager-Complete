import streamlit as st
import os
import pandas as pd
from database import get_all_favorites, get_favorite_by_id, update_favorite_details
from database import update_favorite_order, remove_from_favorites
import database as db
from export_utils import export_to_csv, export_to_excel, export_to_pdf_simple, export_to_pdf_detailed

def show_dashboard_page():
    """
    Display the customizable dashboard with pinned favorite images
    """
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h2>Image Dashboard</h2>
            <p>Your customizable collection of favorited images</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we need to show detail view
    if 'view_favorite_id' in st.session_state:
        show_favorite_details(st.session_state.view_favorite_id)
        return
    
    # Check if we need to show edit view
    if 'edit_favorite_id' in st.session_state:
        show_edit_favorite_dialog(st.session_state.edit_favorite_id)
        return
        
    # Get all favorites from database
    favorites = get_all_favorites()
    
    # Add a button to manually add favorites
    if st.button("Add New Favorite"):
        show_add_favorite_dialog()
        return
    
    if not favorites:
        st.info("Your dashboard is empty. Add images to your dashboard from the History or Search pages.")
        return
    
    # Display layout options
    layout_type = st.radio(
        "Select Layout",
        ["Grid", "List", "Detailed"],
        horizontal=True,
        help="Choose how to display your favorited images"
    )
    
    # Display based on selected layout
    if layout_type == "Grid":
        display_grid_layout(favorites)
    elif layout_type == "List":
        display_list_layout(favorites)
    elif layout_type == "Detailed":
        display_details_layout(favorites)
    
    # Export dashboard data option
    with st.expander("Dashboard Management"):
        export_dashboard_data(favorites)
        
        if st.button("Reorder Favorites"):
            show_reorder_dialog(favorites)
            return

def display_grid_layout(favorites):
    """
    Display favorites in a grid layout
    """
    # Calculate number of columns (responsive approach)
    if len(favorites) <= 3:
        num_cols = len(favorites)
    else:
        num_cols = 3
    
    # Create columns
    cols = st.columns(num_cols)
    
    # Display favorites
    for i, favorite in enumerate(favorites):
        col_index = i % num_cols
        with cols[col_index]:
            st.markdown(f"<h4>{favorite.custom_label or favorite.image.object_name}</h4>", unsafe_allow_html=True)
            
            # Check if file exists
            if os.path.exists(favorite.image.file_path):
                st.image(favorite.image.file_path, use_column_width=True)
            else:
                st.warning("Image file not found")
            
            # Add buttons for details and editing
            if st.button("View Details", key=f"details_{favorite.id}"):
                st.session_state.view_favorite_id = favorite.id
                st.rerun()
            
            if st.button("Edit", key=f"edit_{favorite.id}"):
                st.session_state.edit_favorite_id = favorite.id
                st.rerun()

def display_list_layout(favorites):
    """
    Display favorites in a list layout
    """
    for favorite in favorites:
        with st.container():
            st.markdown("---")
            cols = st.columns([1, 3])
            
            with cols[0]:
                # Check if file exists
                if os.path.exists(favorite.image.file_path):
                    st.image(favorite.image.file_path, use_column_width=True)
                else:
                    st.warning("Image file not found")
            
            with cols[1]:
                st.markdown(f"<h4>{favorite.custom_label or favorite.image.object_name}</h4>", unsafe_allow_html=True)
                st.markdown(f"**Object Type:** {favorite.image.object_name}")
                st.markdown(f"**Confidence:** {favorite.image.confidence:.2f}")
                
                if favorite.note:
                    st.markdown(f"**Note:** {favorite.note}")
                
                # Add buttons for details and editing
                button_cols = st.columns(3)
                with button_cols[0]:
                    if st.button("View Details", key=f"list_details_{favorite.id}"):
                        st.session_state.view_favorite_id = favorite.id
                        st.rerun()
                
                with button_cols[1]:
                    if st.button("Edit", key=f"list_edit_{favorite.id}"):
                        st.session_state.edit_favorite_id = favorite.id
                        st.rerun()
                
                with button_cols[2]:
                    if st.button("Remove", key=f"list_remove_{favorite.id}"):
                        remove_from_favorites(favorite.id)
                        st.success("Removed from dashboard")
                        st.rerun()

def display_details_layout(favorites):
    """
    Display favorites with expanded details
    """
    for favorite in favorites:
        with st.expander(favorite.custom_label or favorite.image.object_name, expanded=True):
            cols = st.columns([1, 2])
            
            with cols[0]:
                # Check if file exists
                if os.path.exists(favorite.image.file_path):
                    st.image(favorite.image.file_path, use_column_width=True)
                else:
                    st.warning("Image file not found")
            
            with cols[1]:
                st.markdown(f"**Object Type:** {favorite.image.object_name}")
                st.markdown(f"**Confidence:** {favorite.image.confidence:.2f}")
                st.markdown(f"**Description:**")
                st.markdown(favorite.image.description)
                
                if favorite.note:
                    st.markdown(f"**Note:** {favorite.note}")
                
                # Display file info
                st.markdown(f"**File:** {favorite.image.file_name}")
                st.markdown(f"**Folder:** {favorite.image.folder.name if favorite.image.folder else 'Unknown'}")
                
                # Add buttons for editing
                button_cols = st.columns(2)
                with button_cols[0]:
                    if st.button("Edit", key=f"detail_edit_{favorite.id}"):
                        st.session_state.edit_favorite_id = favorite.id
                        st.rerun()
                
                with button_cols[1]:
                    if st.button("Remove", key=f"detail_remove_{favorite.id}"):
                        remove_from_favorites(favorite.id)
                        st.success("Removed from dashboard")
                        st.rerun()
                
                # Export single image
                if st.button("Export", key=f"detail_export_{favorite.id}"):
                    show_export_options([favorite.image])

def show_favorite_details(favorite_id):
    """
    Show detailed view of a favorite image
    """
    favorite = get_favorite_by_id(favorite_id)
    
    if not favorite:
        st.error("Favorite not found")
        return
    
    st.subheader(favorite.custom_label or favorite.image.object_name)
    
    # Main content with image and details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Check if file exists
        if os.path.exists(favorite.image.file_path):
            st.image(favorite.image.file_path, use_column_width=True)
        else:
            st.warning("Image file not found")
    
    with col2:
        st.markdown(f"**Object Type:** {favorite.image.object_name}")
        st.markdown(f"**Confidence:** {favorite.image.confidence:.2f}")
        st.markdown(f"**Description:**")
        st.markdown(favorite.image.description)
        
        if favorite.note:
            st.markdown(f"**Note:** {favorite.note}")
        
        # Display file info
        st.markdown(f"**File:** {favorite.image.file_name}")
        st.markdown(f"**Folder:** {favorite.image.folder.name if favorite.image.folder else 'Unknown'}")
        st.markdown(f"**File Path:** {favorite.image.file_path}")
        st.markdown(f"**Added to Dashboard:** {favorite.added_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buttons
        button_cols = st.columns(3)
        with button_cols[0]:
            if st.button("Edit", key=f"detail_view_edit_{favorite.id}"):
                st.session_state.edit_favorite_id = favorite.id
                del st.session_state.view_favorite_id
                st.rerun()
        
        with button_cols[1]:
            if st.button("Remove", key=f"detail_view_remove_{favorite.id}"):
                remove_from_favorites(favorite.id)
                st.success("Removed from dashboard")
                if 'view_favorite_id' in st.session_state:
                    del st.session_state.view_favorite_id
                st.rerun()
        
        with button_cols[2]:
            if st.button("Export", key=f"detail_view_export_{favorite.id}"):
                show_export_options([favorite.image])
    
    # Display metadata if available
    if hasattr(favorite.image, 'metadata_json') and favorite.image.metadata_json:
        st.markdown("### Image Metadata")
        try:
            from utils import format_metadata_for_display
            import json
            
            # Create metadata dictionary from database fields
            metadata = {}
            for field in ['width', 'height', 'camera_make', 'camera_model', 
                        'focal_length', 'aperture', 'exposure_time', 'iso_speed',
                        'date_taken', 'gps_latitude', 'gps_longitude',
                        'file_size', 'file_type']:
                if hasattr(favorite.image, field):
                    metadata[field] = getattr(favorite.image, field)
            
            metadata_text = format_metadata_for_display(metadata)
            st.markdown(metadata_text)
        except Exception as e:
            st.error(f"Error displaying metadata: {str(e)}")
    
    # Button to go back
    if st.button("Back to Dashboard"):
        del st.session_state.view_favorite_id
        st.rerun()

def show_edit_favorite_dialog(favorite_id):
    """
    Show dialog to edit favorite details
    """
    favorite = get_favorite_by_id(favorite_id)
    
    if not favorite:
        st.error("Favorite not found")
        return
    
    st.subheader(f"Edit: {favorite.custom_label or favorite.image.object_name}")
    
    # Edit form
    with st.form("edit_favorite_form"):
        custom_label = st.text_input("Custom Label", 
                                    value=favorite.custom_label or favorite.image.object_name)
        
        note = st.text_area("Note", 
                           value=favorite.note or "",
                           placeholder="Add notes about why this image is important")
        
        display_order = st.number_input("Display Order", 
                                       value=favorite.display_order, 
                                       min_value=0,
                                       help="Lower numbers appear first in the dashboard")
        
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            try:
                update_favorite_details(
                    favorite_id=favorite.id,
                    custom_label=custom_label,
                    note=note
                )
                
                update_favorite_order(
                    favorite_id=favorite.id,
                    new_order=display_order
                )
                
                st.success("Updated successfully!")
                
                # Go back
                if 'edit_favorite_id' in st.session_state:
                    del st.session_state.edit_favorite_id
                st.rerun()
            except Exception as e:
                st.error(f"Error updating: {e}")
    
    # Cancel button
    if st.button("Cancel"):
        if 'edit_favorite_id' in st.session_state:
            del st.session_state.edit_favorite_id
        st.rerun()

def show_add_favorite_dialog():
    """
    Show dialog to add a new favorite
    """
    st.subheader("Add to Dashboard")
    
    # Get all images not in favorites
    db_session = next(db.get_db())
    all_images = db_session.query(db.Image).all()
    
    # Filter to images not in favorites
    non_favorite_images = []
    for image in all_images:
        is_favorite = db_session.query(db.FavoriteImage).filter(
            db.FavoriteImage.image_id == image.id
        ).first()
        
        if not is_favorite:
            non_favorite_images.append(image)
    
    if not non_favorite_images:
        st.info("All images are already in your dashboard")
        return
    
    # Convert to dataframe for selection
    image_data = [{
        "id": img.id,
        "file_name": img.file_name,
        "object_name": img.object_name,
        "folder": img.folder.name if img.folder else "Unknown",
    } for img in non_favorite_images]
    
    image_df = pd.DataFrame(image_data)
    
    # Display as a table for selection
    st.dataframe(
        image_df[["file_name", "object_name", "folder"]],
        use_container_width=True,
        column_config={
            "file_name": "Image Name",
            "object_name": "Object Identified",
            "folder": "Folder"
        },
        hide_index=True
    )
    
    # Select image
    selected_image_id = st.selectbox(
        "Select an image to add",
        options=image_df["id"].tolist(),
        format_func=lambda x: f"{image_df[image_df['id'] == x]['file_name'].iloc[0]} ({image_df[image_df['id'] == x]['object_name'].iloc[0]})"
    )
    
    if selected_image_id:
        # Show add form for the selected image
        show_create_favorite_form(selected_image_id)

def show_create_favorite_form(image_id):
    """
    Show form to create a new favorite
    """
    # Get image details
    db_session = next(db.get_db())
    image = db_session.query(db.Image).filter(db.Image.id == image_id).first()
    
    if not image:
        st.error("Image not found")
        return
    
    # Display image preview
    if os.path.exists(image.file_path):
        st.image(image.file_path, width=300)
    
    # Add form
    with st.form("create_favorite_form"):
        custom_label = st.text_input("Custom Label", value=image.object_name)
        note = st.text_area("Note", placeholder="Add notes about why this image is important")
        display_order = st.number_input("Display Order", value=0, min_value=0, 
                                      help="Lower numbers appear first in the dashboard")
        
        submitted = st.form_submit_button("Add to Dashboard")
        
        if submitted:
            try:
                db.add_to_favorites(
                    image_id=image.id,
                    custom_label=custom_label,
                    note=note,
                    display_order=display_order
                )
                st.success("Added to dashboard successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding to dashboard: {e}")

def show_reorder_dialog(favorites):
    """
    Show dialog to reorder favorites
    """
    st.subheader("Reorder Dashboard Items")
    
    # Convert to dataframe for better display
    favorite_data = [{
        "id": fav.id,
        "label": fav.custom_label or fav.image.object_name,
        "current_order": fav.display_order
    } for fav in favorites]
    
    df = pd.DataFrame(favorite_data)
    df = df.sort_values("current_order")
    
    # Display current order
    st.dataframe(
        df[["label", "current_order"]],
        use_container_width=True,
        column_config={
            "label": "Item",
            "current_order": "Current Order"
        },
        hide_index=True
    )
    
    # Update orders one by one
    selected_favorite = st.selectbox(
        "Select item to update",
        options=df["id"].tolist(),
        format_func=lambda x: df[df["id"] == x]["label"].iloc[0]
    )
    
    if selected_favorite:
        current_order = df[df["id"] == selected_favorite]["current_order"].iloc[0]
        new_order = st.number_input("New display order", 
                                   value=current_order, 
                                   min_value=0)
        
        if st.button("Update Order"):
            try:
                update_favorite_order(selected_favorite, new_order)
                st.success("Order updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating order: {e}")
    
    # Batch update - reorder all sequentially
    if st.button("Reset All Orders (Sequential)"):
        try:
            for i, fav_id in enumerate(df["id"].tolist()):
                update_favorite_order(fav_id, i)
            st.success("All items reordered sequentially!")
            st.rerun()
        except Exception as e:
            st.error(f"Error reordering: {e}")

def export_dashboard_data(favorites):
    """
    Export dashboard data to various formats
    """
    st.subheader("Export Dashboard")
    
    # Create export data
    export_data = []
    for fav in favorites:
        export_data.append({
            "custom_label": fav.custom_label or fav.image.object_name,
            "object_name": fav.image.object_name,
            "description": fav.image.description,
            "confidence": fav.image.confidence,
            "file_name": fav.image.file_name,
            "file_path": fav.image.file_path,
            "folder": fav.image.folder.name if fav.image.folder else "Unknown",
            "note": fav.note or "",
            "added_at": fav.added_at.strftime("%Y-%m-%d %H:%M:%S"),
            "display_order": fav.display_order
        })
    
    export_df = pd.DataFrame(export_data)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Export Format", 
                                    ["CSV", "Excel", "PDF (Simple)", "PDF (Detailed)"], 
                                    key="dashboard_export_format")
    
    with col2:
        if export_format.startswith("PDF"):
            include_images = st.checkbox("Include Images in PDF", 
                                       value=True, 
                                       key="dashboard_include_images")
    
    if st.button("Export Dashboard", key="dashboard_export_button"):
        if export_format == "CSV":
            export_filename = export_to_csv(export_df, "dashboard_export")
            st.success(f"Dashboard exported to {export_filename}")
        
        elif export_format == "Excel":
            export_filename = export_to_excel(export_df, "dashboard_export")
            st.success(f"Dashboard exported to {export_filename}")
        
        elif export_format == "PDF (Simple)":
            with st.spinner("Generating PDF..."):
                export_filename = export_to_pdf_simple(export_df, "dashboard_export")
            st.success(f"Dashboard exported to {export_filename}")
        
        elif export_format == "PDF (Detailed)":
            with st.spinner("Generating detailed PDF report with images..."):
                include_imgs = include_images if 'include_images' in locals() else True
                export_filename = export_to_pdf_detailed(export_df, "dashboard_export", include_imgs)
            st.success(f"Dashboard exported to {export_filename}")
        
        # Provide download link
        with open(export_filename, "rb") as file:
            btn = st.download_button(
                label="Download File",
                data=file,
                file_name=os.path.basename(export_filename),
                mime="application/octet-stream",
                key="dashboard_download_button"
            )

def show_export_options(images):
    """
    Show options for exporting data for a single image
    """
    st.subheader("Export Options")
    
    # Create dataframe for the image
    export_data = []
    for img in images:
        export_data.append({
            "object_name": img.object_name,
            "description": img.description,
            "confidence": img.confidence,
            "file_name": img.file_name,
            "file_path": img.file_path,
            "folder": img.folder.name if img.folder else "Unknown",
        })
    
    export_df = pd.DataFrame(export_data)
    
    # Export options
    export_format = st.selectbox("Export Format", 
                               ["CSV", "Excel", "PDF (Simple)", "PDF (Detailed)"],
                               key="single_export_format")
    
    # Include images option for detailed PDF
    include_images = False
    if export_format == "PDF (Detailed)":
        include_images = st.checkbox("Include Image", 
                                   value=True,
                                   key="single_include_image")
    
    if st.button("Generate Export", key="single_generate_export"):
        img_id = images[0].id if images else "unknown"
        
        if export_format == "CSV":
            export_filename = export_to_csv(export_df, f"image_{img_id}")
            st.success(f"Exported to CSV: {export_filename}")
        
        elif export_format == "Excel":
            export_filename = export_to_excel(export_df, f"image_{img_id}")
            st.success(f"Exported to Excel: {export_filename}")
        
        elif export_format == "PDF (Simple)":
            export_filename = export_to_pdf_simple(export_df, f"image_{img_id}")
            st.success(f"Exported to PDF: {export_filename}")
        
        elif export_format == "PDF (Detailed)":
            export_filename = export_to_pdf_detailed(export_df, f"image_{img_id}", include_images)
            st.success(f"Exported to detailed PDF: {export_filename}")
        
        # Download link
        with open(export_filename, "rb") as file:
            st.download_button(
                label="Download Export",
                data=file,
                file_name=os.path.basename(export_filename),
                mime="application/octet-stream",
                key="single_download_export"
            )

# Main dashboard layout and logic
if __name__ == "__main__":
    show_dashboard_page()