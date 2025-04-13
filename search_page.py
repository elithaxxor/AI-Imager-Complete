import streamlit as st
import os
import pandas as pd
import database as db

def show_search_page():
    """
    Display a search interface for finding images by object name or description
    """
    st.title("Search Image Database")
    st.write("Search for images by object name or description")
    
    # Search box
    search_query = st.text_input("Search for objects or descriptions", 
                               help="Enter keywords to search across all analyzed images")
    
    if search_query:
        # Perform search
        search_results = db.search_images(search_query)
        
        if search_results:
            st.success(f"Found {len(search_results)} results matching '{search_query}'")
            
            # Create a dataframe for display
            results_data = []
            for img in search_results:
                results_data.append({
                    "id": img.id,
                    "folder": os.path.basename(os.path.dirname(img.file_path)),
                    "file_name": img.file_name,
                    "file_path": img.file_path,
                    "object_name": img.object_name,
                    "confidence": img.confidence,
                    "description": img.description[:100] + "..." if len(img.description) > 100 else img.description
                })
            
            results_df = pd.DataFrame(results_data)
            
            # Format for display
            display_df = results_df.copy()
            display_df["View Details"] = display_df.apply(
                lambda row: f'<a href="#" id="search_{row["id"]}">View</a>', 
                axis=1
            )
            
            # Display the table with HTML
            st.write(
                display_df[["folder", "file_name", "object_name", "description", "View Details"]]
                .rename(columns={
                    "folder": "Folder", 
                    "file_name": "File Name", 
                    "object_name": "Object",
                    "description": "Description"
                })
                .to_html(escape=False, index=False), 
                unsafe_allow_html=True
            )
            
            # JavaScript to handle clicks
            st.markdown("""
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const links = document.querySelectorAll('a[id^="search_"]');
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
            clicked_image_id = st.text_input("", key="search_clicked_id", label_visibility="collapsed")
            
            # If an image is selected, show its details
            if clicked_image_id and clicked_image_id.isdigit():
                image_id = int(clicked_image_id)
                show_search_result_details(image_id)
        else:
            st.info(f"No results found for '{search_query}'")
    else:
        # Show some statistics about the database
        db_session = db.SessionLocal()
        folders_count = db_session.query(db.Folder).count()
        images_count = db_session.query(db.Image).count()
        db_session.close()
        
        st.info(f"Database contains {images_count} analyzed images across {folders_count} folders")
        
        # Advanced search options (placeholders for future development)
        with st.expander("Advanced Search Options"):
            st.write("Future versions will include:")
            st.write("- Filtering by confidence level")
            st.write("- Filtering by date processed")
            st.write("- Searching by image similarity")
            st.write("- Exporting search results")

def show_search_result_details(image_id):
    """
    Display details for a specific image from search results
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
        folder_name = os.path.basename(os.path.dirname(image.file_path))
        st.markdown(f"**Folder:** {folder_name}")
        st.markdown(f"**File:** {image.file_name}")
        st.markdown(f"**Object Identified:** {image.object_name}")
        st.markdown(f"**Confidence:** {image.confidence:.2f}")
        st.markdown("### Description")
        st.markdown(image.description)
        st.markdown(f"**Processed at:** {image.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Export options
    with st.expander("Export Options"):
        export_format = st.selectbox("Export Format", ["CSV", "JSON"], key="search_export_format")
        
        if st.button("Export This Result", key="search_export_button"):
            # Code for exporting the result
            pass