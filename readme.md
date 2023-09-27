# LuminaScholar - Academic Journal Management Web Application

LuminaScholar is an online platform designed to streamline the process of submitting, reviewing, and managing scholarly manuscripts for academic journals and conferences.   
Its core functionality includes manuscript submission, peer review management, and editorial workflow coordination. Authors can submit their manuscripts through the platform, where editors manage the review process by assigning reviewers and overseeing the peer review cycle. Reviewers access and evaluate submitted manuscripts, providing feedback and recommendations. The system facilitates communication between authors, reviewers, and editors, enabling collaborative decision-making on manuscript acceptance or revisions. 

## Getting Started

To run the project locally, follow these steps:

1. Navigate to a folder of your choice or create a new one in the file explorer where you want to clone the Git         repository.

2. Right-click and open the terminal while being in that folder.

3. Clone the Git repository:
   `git clone <repository-link>`

4. Navigate to the project root folder(LuminaScholar): `cd LuminaScholar`

5. Install the virtual environment package: `py -m pip install --user virtualenv`

6. Create a new virtual environment: `py -m venv env`

7. Activate the virtual environment:
- If using Git Bash:
  `
  source ./env/Scripts/activate
  `
- If using Command Prompt or PowerShell:
  `
  .\env\Scripts\activate
  `

8. Install all the required packages for the project: `pip install -r requirements.txt`

9. Create a PostgreSQL database in pgAdmin named conferva_db and set a password for it (e.g., 123).

10. Create a file named '.env' in the project root folder(LuminaScholar) and copy the contents from the '.env-sample' file into it. Fill in the values for the following fields:
 ```
 SECRET_KEY=django-insecure-svk*_lwz42j8)no8gub7i7a(&^s%4v=vc_v*ia8d%2zdl@24&8
 DEBUG=True

 # Database configuration
 DB_NAME=luminaScholar_db
 DB_USER=postgres
 DB_PASSWORD=123
 DB_HOST=localhost

 # Email configuration
 EMAIL_HOST=smtp.gmail.com
 EMAIL_PORT=587
 EMAIL_HOST_USER=abc@gmail.com
 EMAIL_HOST_PASSWORD=
 ```

11. Run the migrations to set up the database:
 - `python manage.py makemigrations`
 - `python manage.py migrate`
 
12. Create a superuser for accessing the admin panel:
 `python manage.py createsuperuser`

13. Start the development server:
 `python manage.py runserver`

14. To access the admin portal, open a different web browser or the same browser in private mode and type in the url: `localhost:8000/admin` in the web browser search bar.  
  Log in by using the username and password you set while creating the superuser.
  After being logged in, in the Accounts section go to the User model and create a new User object by setting a unique username and a password and then mark the 'is_admin' True. 

## Additional Commands

- To stop the development server press Ctrl+C

- To deactivate the virtual environment:
`deactivate`

- To create a new Django app:
`python manage.py startapp <app-name>`

- Useful Git commands for version control:
    - `git status`
    - `git add -A`
    - `git commit -m "Commit message"`
    - `git push origin main`

- To create a new Django project:
`django-admin startproject myproject`

- To start shell:
`python manage.py shell`

- To stop shell press Ctrl+Z

- Create requirements.txt automatically: `pip freeze > requirements.txt`

- List all packages installed in virtual environment: `pip list`

- If the changes made to the models are not getting reflected in the database after running makemigrations and migrate command even the changes are there in the migration file(s) then revert the models to how they were before the changes and delete any migration file(s) that do exist for now.
Next generate the migration file(s) by running makemigrations command and then run the following two commands:

  - `python manage.py migrate <app-name> zero --fake`
  - `python manage.py migrate <app-name> --fake`

  The first one will mark all migrations as unapplied for the app. The second one will mark all the migrations as applied. Now add the changes you wanted to make back to the models and run makemigrations and migrate command again.



