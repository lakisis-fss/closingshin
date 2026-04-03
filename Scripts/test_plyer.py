from plyer import notification
import sys

print("Python version:", sys.version)
try:
    print("Importing plyer...")
    from plyer import notification
    print("Plyer imported successfully.")
    
    print("Sending notification...")
    notification.notify(
        title='Test Notification',
        message='This is a test notification from Python.',
        app_name='TestApp',
        timeout=5
    )
    print("Notification sent.")
except Exception as e:
    print(f"Error occurred: {e}")
