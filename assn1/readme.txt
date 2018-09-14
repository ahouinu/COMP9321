// README.txt
Student ID: z5176343
Name: Tianpeng Chen
Installation Guide
- 1. Open this project in PyCharm.
- 2. In Preferences - Project Interpreter, click on the gear, click 'Add Locate', select /venv as the project interpreter.
- 3. Run main.py (server will be running on 127.0.0.1:5000 by default.
- 4. Read Document.html for API details (valid input, output, etc.)
- PS: If coffee type is not in the price_dict, server may occur 500 Internal Server Error as create_order() can't find
    price for this drink. (Note: coffee type is case-sensitive)