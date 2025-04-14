import streamlit as st
import base64
import os

def main():
    st.set_page_config(
        page_title="mommies toy - Download Code",
        page_icon="📦",
        layout="centered"
    )

    st.title("mommies toy - Download Code")
    st.write("Download the complete source code as a ZIP file.")

    # Path to the ZIP file
    zip_file_path = "mommies_toy_code.zip"

    # Check if the zip file exists
    if os.path.exists(zip_file_path):
        # Read the file as bytes
        with open(zip_file_path, "rb") as file:
            zip_data = file.read()
        
        # Create a download button
        st.download_button(
            label="📦 Download Complete Code Package",
            data=zip_data,
            file_name="mommies_toy_code.zip",
            mime="application/zip",
            help="Click to download all source code files as a zip archive"
        )
        
        # Display file size
        file_size_kb = os.path.getsize(zip_file_path) / 1024
        file_size_mb = file_size_kb / 1024
        
        if file_size_mb < 1:
            st.info(f"Download size: {file_size_kb:.1f} KB")
        else:
            st.info(f"Download size: {file_size_mb:.2f} MB")
        
        # File contents details
        st.subheader("Package Contents")
        st.markdown("""
        This package includes:
        
        - **app.py**: Main application file
        - **database.py**: Database models and operations
        - **image_processor.py**: OpenAI image analysis logic
        - **utils.py**: Utility functions including metadata extraction
        - **history_page.py**: History browser functionality
        - **search_page.py**: Search functionality
        - **export_utils.py**: Export functions (CSV, Excel, PDF)
        - **custom_styles.css**: Custom styling
        - **.streamlit/config.toml**: Streamlit configuration
        - **README.md**: User documentation
        - **explain_code.md**: Technical documentation
        - **package_requirements.txt**: Required Python packages
        - **pyproject.toml**: Python project configuration
        """)
        
        # Installation instructions
        st.subheader("Installation Instructions")
        st.markdown("""
        1. Extract the ZIP file to a folder on your computer
        2. Install Python 3.11 or newer if you don't have it
        3. Open a terminal/command prompt in the extracted folder
        4. Install the required packages:
           ```
           pip install -r package_requirements.txt
           ```
        5. Create a `.env` file with your OpenAI API key and database URL:
           ```
           OPENAI_API_KEY=your_openai_api_key
           DATABASE_URL=postgresql://username:password@localhost:5432/mommies_toy_db
           ```
        6. Run the application:
           ```
           streamlit run app.py
           ```
        """)

    else:
        st.error(f"ZIP file not found at {zip_file_path}. Please create the ZIP package first.")

    # Footer
    st.markdown("---")
    st.markdown("@copyleft -- don't do stupid shit with my work.")

# Check if running directly
if __name__ == "__main__":
    main()