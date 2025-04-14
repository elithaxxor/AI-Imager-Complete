import streamlit as st
import os
import pandas as pd
from database import search_images, get_db, Image
from export_utils import export_to_csv, export_to_excel, export_to_pdf_simple, export_to_pdf_detailed

def show_search_page():
    """
    Display a search interface to find images by description or object name
    """
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h2>Image Search</h2>
            <p>Search for images by object name, description, or camera details</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search interface - made more mobile friendly
    query = st.text_input("Search for images", 
                          placeholder="Enter search terms...",
                          help="Search is case insensitive and will match partial words")

    # Execute search when a query is entered
    if query:
        results = search_images(query)

        if not results:
            st.info(f"No results found for '{query}'")
            return

        # Convert to DataFrame for better display
        result_data = [{
            "id": img.id,
            "file_name": img.file_name, 
            "folder_name": img.folder.name if img.folder else "Unknown",
            "object_name": img.object_name, 
            "confidence": img.confidence,
            "camera_info": f"{img.camera_make} {img.camera_model}".strip() if hasattr(img, 'camera_make') and img.camera_make else "",
            "file_type": img.file_type.upper() if hasattr(img, 'file_type') and img.file_type else "",
            "description_snippet": img.description[:100] + "..." if len(img.description) > 100 else img.description
        } for img in results]

        result_df = pd.DataFrame(result_data)

        # Display results count
        st.subheader(f"Found {len(results)} results")

        # Display as a table
        st.dataframe(
            result_df[["file_name", "folder_name", "object_name", "confidence", "camera_info", "file_type", "description_snippet"]],
            column_config={
                "file_name": "Image Name",
                "folder_name": "Folder",
                "object_name": "Object Identified",
                "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
                "camera_info": "Camera",
                "file_type": "Format",
                "description_snippet": "Description Preview"
            },
            hide_index=True
        )

        # Add export options
        st.subheader("Export Search Results")

        st.markdown('<div class="export-options">', unsafe_allow_html=True)
        export_format = st.selectbox("Export Format", 
                                    ["CSV", "Excel", "PDF (Simple)", "PDF (Detailed)"],
                                    key="search_export_format")

        if export_format.startswith("PDF"):
            include_images = st.checkbox("Include Images in PDF", value=True, 
                                        help="Include image previews in the PDF export (may increase file size)",
                                        key="search_include_images")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add text area for folder description
        folder_description = st.text_area(
            "Folder Description (will be included in exports)",
            value=f"Collection of images related to '{query}'",
            height=100,
            key="search_folder_description"
        )

        if st.button("Export Results", key="search_export_button"):
            # Construct a proper dataframe for export with all fields
            export_data = []
            for img in results:
                export_data.append({
                    "file_name": img.file_name,
                    "file_path": img.file_path,
                    "folder_name": img.folder.name if img.folder else "Unknown",
                    "object_name": img.object_name,
                    "description": img.description,
                    "confidence": img.confidence,
                    "processed_at": img.processed_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "folder_description": folder_description,
                    "item_description": f"Found in search for '{query}'"
                })

            export_df = pd.DataFrame(export_data)

            if export_format == "CSV":
                export_filename = export_to_csv(export_df, f"search_results_{query}")
                st.success(f"Results exported to {export_filename}")

            elif export_format == "Excel":
                export_filename = export_to_excel(export_df, f"search_results_{query}")
                st.success(f"Results exported to {export_filename}")

            elif export_format == "PDF (Simple)":
                with st.spinner("Generating PDF..."):
                    export_filename = export_to_pdf_simple(export_df, f"search_results_{query}")
                st.success(f"Results exported to {export_filename}")

            elif export_format == "PDF (Detailed)":
                with st.spinner("Generating detailed PDF report with images..."):
                    include_imgs = include_images if 'include_images' in locals() else True
                    export_filename = export_to_pdf_detailed(export_df, f"search_results_{query}", include_imgs)
                st.success(f"Results exported to {export_filename}")

            # Provide download link
            with open(export_filename, "rb") as file:
                btn = st.download_button(
                    label="Download File",
                    data=file,
                    file_name=os.path.basename(export_filename),
                    mime="application/octet-stream",
                    key="search_download_button"
                )

        # Let user select an image to view details
        st.subheader("View Image Details")
        selected_image_id = st.selectbox(
            "Select an image to view details",
            options=result_df["id"].tolist(),
            format_func=lambda x: f"{result_df[result_df['id'] == x]['file_name'].iloc[0]} ({result_df[result_df['id'] == x]['folder_name'].iloc[0]})"
        )

        if selected_image_id:
            show_search_result_details(selected_image_id)
    else:
        st.info("Enter a search term to find images")

def show_search_result_details(image_id):
    """
    Display details for a specific image from search results
    """
    # Find the image in the database
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
        st.markdown(f"**Folder:** {image.folder.name if image.folder else 'Unknown'}")
        st.markdown(f"**Object Identified:** {image.object_name}")
        st.markdown(f"**Confidence:** {image.confidence:.2f}")
        st.markdown("### Description")
        st.markdown(image.description)

        # Highlight search terms in description
        if 'query' in locals() and query:
            highlighted_desc = image.description
            for term in query.split():
                if len(term) > 2:  # Only highlight terms with more than 2 characters
                    highlighted_desc = highlighted_desc.replace(
                        term, f"<mark>{term}</mark>"
                    )
            st.markdown(highlighted_desc, unsafe_allow_html=True)
        else:
            st.markdown(image.description)

        # Additional metadata
        st.markdown("### File Metadata")
        st.markdown(f"**Processed Date:** {image.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**Full Path:** {image.file_path}")

        # Display image metadata if available
        if hasattr(image, 'metadata_json') and image.metadata_json:
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
                    if hasattr(image, field):
                        metadata[field] = getattr(image, field)

                metadata_text = format_metadata_for_display(metadata)
                st.markdown(metadata_text)
            except Exception as e:
                st.error(f"Error displaying metadata: {str(e)}")