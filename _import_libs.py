import subprocess

try:
    from decouple import config
except ImportError:
    try:
        subprocess.check_call(['pip', 'install', 'python-decouple'])
        from decouple import config  # Verify if the installation was successful
    except subprocess.CalledProcessError as e:
        # Handle the error, e.g., show a message to the user
        print(e)
        

try:
    import requests
except ImportError:
    try:
        subprocess.check_call(['pip', 'install', 'requests'])
        import requests  # Verify if the installation was successful
    except subprocess.CalledProcessError as e:
        # Handle the error, e.g., show a message to the user
        print(e)