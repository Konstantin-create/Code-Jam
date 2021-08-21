import validators


# Short name
def short_name(name):
    if len(str(name)) >= 11:
        return str(name)[:11] + '...'
    return str(name)


# Validator db posts
def validate_db_posts(title, short_description, files):
    print(files.read())
    if title == "" or short_description == "":
        return False


# Validator url
def validate_url(url):
    if not validators.url(url):
        return False
    return True
