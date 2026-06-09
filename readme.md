# Online Bookstore Portal (TFB_APP)

Welcome to our project repository! Follow the instructions below to get the application up and running on your local machine.

---

## Local Installation & Setup

Always run these commands from the main `TFB_APP` root directory.

### 1a. Clone the Repository (First Method)
```bash
git clone https://github.com/Alex-Vrsecky/Book_Store_Implementation
cd TFB_APP
```
### 1b. Download the zipped folder (Second Method)
1. Unzip and choose a destination for the content to go to
2. Open Visual Studio Code
3. Ensure python is installed (version that works for me 3.12.5, but others could also work)
4. Open the terminal and ensure you are running commands from this point on in the main `TFB_APP` root directory

### 2. Set Up a Virtual Environment
Create and activate an isolated Python environment to keep the packages managed:

* **Windows (Command Prompt / PowerShell):**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
* **Mac / Linux:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 3. Install Dependencies
Install all required libraries mapped out in the setup file:
```bash
pip install -r requirements.txt
```

### 4. Seed the Database
Before running the server, make sure to generate and seed your local database file (`TFB.db`):
```bash
python server/database_seeder.py
```

---

## Running the Web Application

To ensure our custom architectural module layout (like `interface` and `server`) imports properly across folder boundaries, **always execute the program from the root level**:

```bash
python app.py
```
Once executed, open your web browser and navigate to: `http://127.0.5.1:5000/` or if that doesnt work, go to the link shown in the terminal

---

## Architectural Layout Cheat-Sheet

* `app.py` - Core Flask server initialization and central router control logic.
* `app_frame.py` - Global application HTML UI layouts wrapper used dynamically by view classes.
* `interface/` - Houses views, controllers (`controlviews.py`), and presentation logic.
* `server/` - Handles persistent data interactions (`database.py`, `models.py`) and initial mock seed arrays.
