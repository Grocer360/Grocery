import os
import cv2
from datetime import datetime
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import util
import uuid
import psycopg2
class Logout:
    def logout(self):
        if self.most_recent_capture_arr is None:
            print("No image captured for logout")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            print("No faces detected in the captured frame")
            util.msg_box("Error", "No faces detected!")
            return

        # Save the captured image temporarily for face recognition
        img_path = os.path.join(self.db_dir, f"temp_logout_{uuid.uuid4().hex}.jpg")
        cv2.imwrite(img_path, self.most_recent_capture_arr)

        try:
            recognized_name = util.recognize(self.most_recent_capture_arr, self.db_dir)
            print(f"Recognized name: {recognized_name}")

            if recognized_name == 'unknown_person':
                util.msg_box("Error", "Face not recognized. Please try again.")
            elif recognized_name == 'no_persons_found':
                util.msg_box("Error", "No persons found. Please try again.")
            else:
                # Calculate working hours
                time_stamp_in = self.get_login_time(recognized_name)  # Retrieve login time from database
                print(f"Login time for {recognized_name}: {time_stamp_in}")
                time_stamp_out = datetime.now()  # Current time is logout time
                print(f"Logout time for {recognized_name}: {time_stamp_out}")

                if time_stamp_in:
                    working_hours = self.calculate_working_hours(time_stamp_in, time_stamp_out)
                else:
                    print(f"Failed to retrieve login time for {recognized_name}")
                    working_hours = "N/A"

                # Update database
                success = self.update_logout_status(recognized_name, time_stamp_out, working_hours)

                if success:
                    util.msg_box("Goodbye!", f"Goodbye, {recognized_name}")
                    self.log_access("Logout", recognized_name)
                else:
                    util.msg_box("Error", "Failed to update logout status. Please try again.")
        finally:
            # Clean up temporary file
            if os.path.exists(img_path):
                os.remove(img_path)
    def get_login_time(self, username):
        try:
            conn = psycopg2.connect(**self.conn_details)
            cursor = conn.cursor()
            cursor.execute("SELECT time_stamp_in FROM Users WHERE user_name = %s", (username,))
            time_stamp_in = cursor.fetchone()
            cursor.close()
            conn.close()
            if time_stamp_in:
                return time_stamp_in[0]
            return None
        except Exception as e:
            print(f"Error retrieving login time for {username}: {e}")
            return None
        
    def update_logout_status(self, username, time_stamp_out, working_hours):
        try:
            with psycopg2.connect(**self.conn_details) as conn:
                with conn.cursor() as cursor:
                    # Print the details being updated for debugging
                    print(f"Updating logout status for {username}")
                    print(f"Set logged_in to False, time_stamp_out to {time_stamp_out}, working_hours to {working_hours}")

                    cursor.execute("""
                        UPDATE Users 
                        SET logged_in = %s, time_stamp_out = %s, working_hours = %s 
                        WHERE user_name = %s
                    """, (False, time_stamp_out, working_hours, username))
                    
                    # Check how many rows were affected by the update
                    rows_updated = cursor.rowcount
                    print(f"Rows updated: {rows_updated}")

                    # Commit the transaction
                    conn.commit()

                    if rows_updated > 0:
                        print(f"Logout details updated for {username}")
                        return True
                    else:
                        print(f"No records updated. User {username} may not exist or is already logged out.")
                        return False
        except psycopg2.DatabaseError as db_error:
            print(f"Database error updating logout status for {username}: {db_error}")
        except psycopg2.OperationalError as op_error:
            print(f"Operational error updating logout status for {username}: {op_error}")
        except Exception as e:
            print(f"Unexpected error updating logout status for {username}: {e}")
        return False