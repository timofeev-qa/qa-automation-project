# QA Automation Project (Users & Tasks)

## Overview

This project simulates a simple system with users and tasks.

The main goal was not to build a real API, but to practice:
- test design
- working with data
- validating business rules
- writing meaningful tests instead of just checking endpoints

---

## Structure

The project is split into 3 layers:

- client — builds data and calls service functions  
- service — contains validation and business rules  
- db (SQLite) — stores data and runs SQL queries  

Flow:  
client → service → db

---

## What is covered

Main scenarios:

- create / get user  
- update user  
- delete user  
- create task (only for active user)  
- task status logic (including "done" restrictions)  
- token-based access (valid / invalid / missing)

Additional:

- duplicate email (handled by DB constraint)  
- empty results  
- basic negative cases  

- task limit: max 3 active tasks per user
    - preventing creation of 4th active task
    - preventing update from inactive → active when limit reached
    - allowing update of existing active tasks without breaking limit
    - freeing slot after task completion
    - inactive tasks do not affect active limit

---

## Notes

- business logic is placed in service layer  
- client layer is kept simple  
- database constraints are used where needed  
- random data is used to avoid collisions in tests  

---

## Stack

- Python  
- pytest  
- sqlite3  

---

## Run

```bash
pytest -v