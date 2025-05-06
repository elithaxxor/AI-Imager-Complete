# mommies toy - Super Easy Picture Analyzer 🖼️

Hello friend! This is a special computer program that looks at all your pictures and tells you what's in them using a super smart robot brain! It's like having a friend who can see all your photos and tell you stories about what's in them!

@copyleft -- don't do stupid shit with my work.

## What This Program Does (The Really Fun Stuff!)

This magical program can:
- Look at thousands of your pictures all at once! (up to 5,000 pictures in 200 folders)
- Tell you what's in each picture using robot eyes 👁️👁️
- Make up stories about your pictures
- Remember everything it sees in a special treasure box (that's the database!)
- Find pictures later when you're looking for something special
- Make pretty reports you can save and share with friends

## How The Magic Works Behind The Curtain

Our program has different magical parts that work together:

1. **The Looking Part**: This part looks at your pictures using special robot eyes from a company called OpenAI. Their robot brain is called GPT-4o and it's super duper smart!

2. **The Remembering Part**: After looking at your pictures, the program puts all the information in a special treasure box called PostgreSQL. This means it won't forget anything it sees!

3. **The Pretty Website Part**: You can use the program through a special colorful website made with something called Streamlit. It has buttons and pictures and is very easy to use!

4. **The Detective Part**: When you want to find a specific picture, this part helps you search through all the pictures the program has seen before.

5. **The Collector Part**: This part pulls out all the secret information hidden inside your pictures - like what camera took them, where the picture was taken, and other cool secret codes!

## How to Make It Work on Your Computer

### Things You Need First:
- A computer with Python (that's a special computer language)
- A special key from OpenAI (like a magic password)
- A PostgreSQL database (the treasure box)

### Step-by-Step Instructions (Like Building a Lego Set):

1. **Get the program files** - You need to download all the program files and put them in a special folder on your computer.

2. **Install the magical ingredients** - Open a command window (ask a grown-up to help) and type:
   ```
   pip install -r package_requirements.txt
   ```
   This gets all the special magical ingredients the program needs!

3. **Set up your magic passwords** - Create a file called `.env` and put these magic words inside:
   ```
   OPENAI_API_KEY=your_super_secret_openai_key
   DATABASE_URL=postgresql://username:password@localhost:5432/mommies_toy_db
   ```
   (Replace the secret parts with your actual secrets!)

4. **Start the program** - Type this magic spell:
   ```
   streamlit run app.py
   ```
   And POOF! The program starts running!

## How to Use the Magical Program (Super Easy Steps!)

### Looking at Pictures:

1. When the program starts, you'll see a page with "mommies toy" at the top.
2. Look at the gray bar on the left side of the screen.
3. Type the path to where your pictures are stored (like `C:\My Pictures` on Windows or `/home/username/Pictures` on Mac/Linux).
4. Pick a folder from the dropdown menu that appears.
5. Click the big "Process Folder" button.
6. Wait while the robot brain looks at all your pictures (this might take a little while - maybe go get a snack!).
7. When it's done, you'll see a list of all your pictures and what the robot thought they were!

### Finding Pictures You've Already Looked At:

1. Click the "Analysis History" button at the top.
2. You'll see all the folders you've looked at before.
3. Click on any folder to see the pictures inside.
4. Click on any picture to see what the robot thought about it.

### Searching for Special Pictures:

1. Click the "Search Database" button at the top.
2. Type what you're looking for (like "cat" or "beach" or "Canon camera").
3. The program will find all pictures that match what you typed!
4. Click on any picture to see more details.

### Making Pretty Reports:

1. After you've looked at pictures or searched, look for the "Export Results" section.
2. Pick what kind of report you want:
   - CSV (a simple file you can open in Excel)
   - Excel (a colorful spreadsheet)
   - PDF Simple (a neat report)
   - PDF Detailed (a fancy report with pictures included)
3. Write a description if you want.
4. Click "Export Results" button.
5. Click "Download File" to save it to your computer.

## Special Image Detective Information (Metadata)

The program is also a secret detective! It can find hidden information in your pictures that you might not even know is there:

- What camera took the picture
- When the picture was taken
- Where the picture was taken (if your camera knows)
- How big the picture is
- Special camera settings used
- What kind of file the picture is

All this secret information is saved in the treasure box (database) along with what the robot brain saw in the picture. You can search for pictures using this secret information too!

## How Much It Costs to Run This Magic

If you want to look at 5,000 pictures:
- The robot brain costs about $300-350 to rent
- The people who made this program charged about $400
- Total cost: around $700-750

## Special Notes for Grown-Ups

This program uses advanced artificial intelligence to analyze images through the OpenAI API, specifically leveraging the GPT-4o model's vision capabilities. The application is built with Python 3.11 and uses several libraries:

- Streamlit for the web interface
- SQLAlchemy with PostgreSQL for the database
- Pandas for data handling and exports
- Pillow and exifread for image processing and metadata extraction
- ReportLab and FPDF for PDF generation

The application securely stores all analysis results and extracted metadata in a PostgreSQL database, allowing for persistent storage and efficient querying. The search functionality allows for searching across object names, descriptions, and metadata fields including camera information and file properties.

@copyleft -- don't do stupid shit with my work.