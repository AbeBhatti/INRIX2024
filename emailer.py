import smtplib, ssl

def send_sms(sender_email, sender_password, recipient_phone_number, carrier_gateway, body):
    """
    Sends an SMS using SMTP. 
    :param sender_email: Email address of the sender.
    :param sender_password: Password or app-specific password for the sender email.
    :param recipient_phone_number: Phone number of the recipient.
    :param carrier_gateway: SMS gateway of the recipient's carrier (e.g., 'tmomail.net' for T-Mobile).
    :param body: Body of the SMS (message content).
    """
    try:
        # Combine recipient's phone number with the carrier's SMS gateway
        recipient_email = f"{recipient_phone_number}@{carrier_gateway}"

        # Connect to the SMTP server (Gmail in this case)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)  # Log in to the sender's email account
            server.sendmail(sender_email, recipient_email, body)  # Send the SMS
            print(f"Message sent successfully to {recipient_email}.")

    except Exception as e:
        print(f"Failed to send SMS: {e}")

def main():
    # Example input for vehicle details (make, model, color)
    make = input("Enter the vehicle make: ")
    model = input("Enter the vehicle model: ")
    color = input("Enter the vehicle color: ")

    # Example recipient phone number and carrier (e.g., AT&T)
    recipient_phone_number = "4083324884"  # Replace with actual recipient phone number
    carrier_gateway = "txt.att.net"  # Replace with the carrier's SMS gateway (e.g., T-Mobile, Verizon, etc.)

    # Construct the message content (SMS body)
    body = f"Vehicle Alert: {color} {make} {model} detected. Please investigate."

    # Sender email credentials (use an app-specific password for Gmail)
    sender_email = "vidittheboat@gmail.com"
    sender_password = "tupg ruzi zpri acpu"  # Use your Gmail app-specific password here

    # Send the SMS
    send_sms(sender_email, sender_password, recipient_phone_number, carrier_gateway, body)

if __name__ == "__main__":
    main()
