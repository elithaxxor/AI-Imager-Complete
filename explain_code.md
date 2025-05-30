# How This Program Works (Code Explanation)

## Overall Program Structure

The program is divided into several Python files, each responsible for a different part of the application:

1. **app.py**: The main application file that sets up the Streamlit interface and handles the main page flow.

2. **database.py**: Manages the PostgreSQL database connection and defines the data models.

3. **image_processor.py**: Contains logic for processing images with OpenAI's GPT-4o vision model.

4. **utils.py**: Contains utility functions for working with images, including metadata extraction.

5. **history_page.py**: Manages the history view where users can browse previously analyzed images.

6. **search_page.py**: Handles the search functionality to find specific images in the database.

7. **export_utils.py**: Provides functions to export results in various formats (CSV, Excel, PDF).

## Key Components Explained

### Database Structure (database.py)

The database has two main tables:

1. **Folders**: Stores information about folders that have been processed
   - id: Unique identifier
   - name: Folder name
   - path: Full path to folder
   - processed_at: When the folder was processed

2. **Images**: Stores analysis results and metadata for each image
   - id: Unique identifier
   - folder_id: Reference to parent folder
   - file_name: Name of the image file
   - file_path: Full path to the image
   - object_name: Main object identified in the image
   - description: Detailed description generated by AI
   - confidence: Confidence score of the analysis
   - processed_at: When the image was analyzed
   - metadata_json: Complete metadata as JSON string
   - Individual metadata fields (width, height, camera_make, etc.)

The database logic uses SQLAlchemy ORM (Object-Relational Mapping) to interact with PostgreSQL.

### Image Processing (image_processor.py)

The image processing flow:
1. An image is loaded and encoded to base64 format
2. The base64 image is sent to OpenAI's API with a prompt asking to identify objects
3. The response is parsed to extract the object name, description, and confidence
4. Image metadata is extracted using the utils.py functions
5. All results are returned and stored in the database

```python
def process_single_image(image_path):
    # Encode image to base64
    base64_image = encode_image_to_base64(image_path)
    
    # Analyze with OpenAI
    result = analyze_image_with_openai(base64_image)
    
    # Extract metadata
    metadata = extract_image_metadata(image_path)
    
    # Add metadata to result
    result['metadata'] = metadata
    
    return result
```

### Metadata Extraction (utils.py)

The metadata extraction uses several libraries:
- PIL (Pillow) for image dimensions and basic properties
- exifread for detailed EXIF metadata
- pillow_heif for HEIC/HEIF format support

It extracts information like:
- Image dimensions (width, height)
- Camera information (make, model)
- Camera settings (aperture, exposure time, ISO)
- GPS coordinates
- Date taken
- File properties (size, type)

```python
def extract_image_metadata(file_path):
    # Create basic metadata dictionary
    metadata = {...}
    
    # Extract file info
    metadata['file_size'] = get_file_size(file_path)
    metadata['file_type'] = ext.lower().replace('.', '')
    
    # Extract dimensions
    width, height = get_image_dimensions(file_path)
    metadata['width'] = width
    metadata['height'] = height
    
    # Extract EXIF data
    with open(file_path, 'rb') as f:
        exif_tags = exifread.process_file(f, details=False)
        # ... extract various EXIF fields
    
    return metadata
```

### User Interface (app.py)

The Streamlit interface is organized into several pages:
1. **Process Images**: The main page where users can select folders and process images
2. **Analysis History**: View previously processed folders and images
3. **Search Database**: Search for images by content or metadata

The UI is built using Streamlit's declarative components like:
- st.title() - For page titles
- st.sidebar - For folder selection controls
- st.columns() - For layout of image previews and details
- st.dataframe() - For tabular display of results
- st.download_button() - For exporting results

### Export Functionality (export_utils.py)

The application can export results in multiple formats:
1. **CSV**: Simple tabular data
2. **Excel**: Formatted spreadsheet
3. **PDF Simple**: Basic PDF with tables
4. **PDF Detailed**: Advanced PDF with images and formatted descriptions

The export process:
1. Convert analysis results to a pandas DataFrame
2. Depending on the format, use different libraries to create the export file
3. Save the file to disk with a timestamped name
4. Provide a download link to the user

## How Data Flows Through The Application

1. User selects a folder containing images
2. For each image in the folder:
   - The image is processed using OpenAI API
   - Metadata is extracted
   - Results are stored in the database
3. Results are displayed to the user
4. The user can:
   - Browse detailed results
   - Export results in various formats
   - Visit the history page to see previous analyses
   - Search for specific images by content or metadata

## Performance Considerations

- The application processes images sequentially, displaying a progress bar
- Database queries use efficient indexes on frequently searched fields
- Large PDF exports with images can be memory-intensive
- OpenAI API calls are the main performance bottleneck and cost driver

## Security Considerations

- API keys are stored in environment variables
- Database connection details are secured
- User inputs are validated before processing
- File paths are checked for existence and proper format
- No user authentication is implemented in the current version