# authentication

## Description

This project is a simple authentication system that allows users to sign up, log in, and log out. It uses a PostgreSQL database to store user information and sessions. The project is built using Python and Flask.

## Installation

1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add the following environment variables:
   - `DATABASE_URL`: The URL of the PostgreSQL database
    - `SECRET_KEY`: A secret key for the Flask app
4. Run the app using `flask run`

## Usage

- To sign up, go to `/signup` and enter your details
- To log in, go to `/login` and enter your details
- To log out, go to `/logout`
- To rest password go to `/reset-password` and enter your email
- To verify email go to `/verify-email` and enter your email
- To verify phone number go to `/verify-phone` and enter your phone number


## License

This project is open source and available under the [MIT License](LICENSE).
```

### Output[]: # Path: requirements.txt
```txt 
bcrypt==3.2.0
Flask==2.0.1
Flask-Mail==0.9.1
Flask-Session==0.4.0
psycopg2-binary==2.9.1
```

### Output[]: # Path: .env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/database
SECRET_KEY=secret
```

### Output[]: # Path: LICENSE
```txt
MIT License

Copyright (c) 2021

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
