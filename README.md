# Covid-Bunker
    COVID BUNKER
    By: Phillip Applegate, Isaac Lehman, Eric Martin, and Nathaniel Shi

    Your one stop shop for all things Covid.

    Options to run server:
    1.
        set FLASK_APP=server.py       (set the current server file to run)
        python -m flask run           (run the server)
    2.
        python server.py              (runs in debug mode)

    Some pip stuff:
        pip install --upgrade google-auth
        pip install --upgrade requests
        
    NOTE:
        Make sure you run on local host and not the local ip address.
        Example: http://localhost:5000

    At the login page you can login as either 
        a) a google account using the google id 
        b) a pre-existing user id

        To test admin functionality, login with user id 1
        To test normal user functionality, login with user id abc123

    NOTE: Google Pay and Purchase History are incomplete