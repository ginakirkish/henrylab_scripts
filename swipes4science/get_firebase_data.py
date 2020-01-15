import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("/data/henry6/gina/scripts/swipes4science/sienaxlesions_firebase.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://sienaxlesions.firebaseio.com'})

# Get a database reference to our posts
ref = db.reference('project/sienaxlesions/database/sienaxlesions/data')

# Read the data at the posts reference (this is a blocking operation)
print(ref.get())



"""

# Import database module.
from firebase_admin import db

# Get a database reference to our posts
ref = db.reference('server/saving-data/fireblog/posts')

# Read the data at the posts reference (this is a blocking operation)
print(ref.get())



from firebase_admin import firebase
firebase = firebase.FirebaseApplication('https://sienaxlesions.firebaseio.com', None)
result = firebase.get('/Data', None)
print(results)"""
