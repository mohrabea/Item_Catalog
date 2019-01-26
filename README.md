
# Item Catalog Project

### About Item Catalog
#### Project Overview

You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

#### Why this project?

Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.

#### What Will I Learn?

* Develop a RESTful web application using the Python framework Flask.
* Implementing third-party OAuth authentication.
* Implementing CRUD (create, read, update and delete) operations.

#### In This Repo

This project has one main Python module `application.py` which runs the Flask application. A SQL database is created using the `database_setup.py` module and you can populate the database with test data using `database_seeder.py` . The Flask application uses stored HTML templates in the `tempaltes` folder to build the front-end of the application. CSS are stored in the `static` directory.


#### Skills used
* Python
* HTML
* CSS
* Flask Framework
* Jinja2
* SQLAchemy
* OAuth2 authentication(with google+)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. See deployment for notes on how to deploy the project on a live system.

### PreRequisites:

* Operating system (Linux / Windows)
* [Python 3.x](https://www.python.org/)
* [VirtualBox](https://www.virtualbox.org/)
* [Vagrant](https://www.vagrantup.com/)

### How to Run

1. Install Vagrant and VirtualBox.
2. Clone the fullstack-nanodegree-vm.
3. Launch the Vagrant VM (vagrant up).
4. Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
5. un your application within the VM (python /vagrant/catalog/application.py)
6. Access and test your application by visiting http://localhost:8000 locally.


### JSON Endpoints

The following are open to the public:
* **Catalog JSON:** `http://localhost:8000/catalog.json` -Displays the whole catalog. Categories and all items.
* **Categories JSON:** `http://localhost:8000/catalog.json/categories.json` -Displays items for a specific category.
* **Category Items JSON:** `http://localhost:8000/catalog.json/categories.jso/items.json` Displays a specific category item.


### Authors

* **Mohammed Rabea** - *Email: moh.rabea@gmail.com* 





