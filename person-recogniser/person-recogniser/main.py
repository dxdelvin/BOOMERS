import cv2
import time

cap = cv2.VideoCapture(0)
human_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

timer_start = None
timer_end = None

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if the frame is empty
    if not ret:
        print("No frame available. Exiting...")
        break

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    humans = human_cascade.detectMultiScale(gray, 1.9, 1)

    # Display the resulting frame
    for (x, y, w, h) in humans:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
        if timer_start is None:
            timer_start = time.time()  # Start the timer when a person appears
        else:
            timer_end = None  # Reset the end time if a person appears again
    else:
        if timer_start is not None:
            if timer_end is None:
                timer_end = time.time()  # Set the end time if no person is detected
            elapsed_time = timer_start - timer_end
            print("Elapsed Time:", round(elapsed_time, 2), "seconds")
            if elapsed_time >= 20:  # 5 minutes in seconds
                print("Alert")
                break
            timer_start = None  # Reset the timer

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
