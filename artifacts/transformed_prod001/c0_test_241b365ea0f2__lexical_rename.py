import pandas as pd
import datetime
import subprocess
import pyautogui
import time
import keyboard

# Assuming df is already defined and contains the necessary data
df_new_renamed = pd.DataFrame()

while True:
    # Check the current system time
    timestr = datetime.datetime.now().strftime("%H:%M")
    # Check if the current time is mentioned in the DataFrame
    if timestr in df['Time'].astype(str).values:
        df_new_renamed = df[df['Time'].astype(str).str.contains(timestr)]

        # Open the Zoom app
        zoom_app_location = "***Put the location of the Zoom app here***"
        subprocess.Popen(zoom_app_location)
        time.sleep(9)

        # Click the join button
        try:
            join_btn = pyautogui.locateCenterOnScreen('join_button.png')
            pyautogui.moveTo(join_btn)
            pyautogui.click()
            time.sleep(5)

            # Write the meeting ID from the dataframe onto the Zoom App
            meeting_id = str(df_new_renamed.iloc[0, 1])
            keyboard.write(meeting_id)
            pyautogui.press('enter')
            time.sleep(6)

            # Read the Meeting Passcode from the dataframe and enter into the zoom app
            meeting_passcode = str(df_new_renamed.iloc[0, 2])
            keyboard.write(meeting_passcode)
            pyautogui.press('enter')
            time.sleep(6)

        except pyautogui.ImageNotFoundException:
            print(f"Could not find the join button or the elements to input the meeting details.")
            subprocess.Popen.kill()

        except IndexError:
            print("Meeting details not found in the DataFrame.")
            subprocess.Popen.kill()

        except Exception as e:
            print(f"An error occurred: {e}")
            subprocess.Popen.kill()

    time.sleep(60)  # Wait for 1 minute before checking the time again
