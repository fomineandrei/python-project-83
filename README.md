[![Actions Status](https://github.com/fomineandrei/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/fomineandrei/python-project-83/actions)
[![Maintainability](https://qlty.sh/badges/98ca09e8-84bf-4f9f-bf50-759b678811af/maintainability.svg)](https://qlty.sh/gh/fomineandrei/projects/python-project-83)


# Page Analyzer app
### This app analyzes the main headers of website home pages.

## Install:

### This app works with PostgreSQL databases with version at least 4.18
### You must have empty database
### 1. Clone this app with command: git clone git@github.com:fomineandrei/python-project-83.git
### 2. Create .env file in root directory. In this file must be two environments:
###    SECRET_KEY='your_secret_key'
###    DATABASE_URL='postgresql://{db_user}:{db_password}@localhost:5432/{db_name}'
### 3. Make global environment with command: 
###    export DATABASE_URL='postgresql://{db_user}:{db_password}@localhost:5432/{db_name}'
### 4. Install dependencies and database init with command: make build


## Test:

### 1. This app has built-in tests. You can run tests with command: make local-test

### 2. You can see app with browser:
###    Start dev server: make dev
###    Open your browser and enter this url: http://localhost:5000

## Run app:

### Run app with command: make start
### The app will be available from your computer at http://localhost:8000
