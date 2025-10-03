from flask import Flask, request, jsonify, Response
import smtplib
from flask_cors import CORS
from flask import send_from_directory
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import logging
import datetime

app = Flask(__name__)

# Configure CORS to allow requests from your website
CORS(app, origins=["https://www-bethe-el-com.onrender.com", "http://localhost:3000"])

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure your email settings
EMAIL_ADDRESS = 'chanieasmamaw@yahoo.com'
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAILS = ['chanieasmamaw@yahoo.com', 'elsa32@walla.com']

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()})

@app.route('/')
def home():
    return "Flask Email Server is running! Use POST /register for registrations."

@app.route('/form.js')
def serve_javascript():
    """Serve the JavaScript file for form handling"""
    javascript_content = """ 
    // (your JavaScript unchanged – omitted here for brevity)
    """
    response = Response(javascript_content, mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/test-email', methods=['GET'])
def test_email():
    """Test endpoint to check email configuration"""
    if not EMAIL_PASSWORD:
        return jsonify({'status': 'fail', 'message': 'EMAIL_PASSWORD not configured'}), 500

    try:
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465, timeout=15) as smtp:  # timeout added
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("SMTP connection successful!")

            msg = EmailMessage()
            msg['Subject'] = 'Test Email - Flask App'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = ', '.join(TO_EMAILS)
            msg.set_content('This is a test email to verify the email configuration is working.')

            smtp.send_message(msg)
            return jsonify({'status': 'success', 'message': 'Test email sent successfully!'})

    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Email test failed: {str(e)}'}), 500

@app.route('/register', methods=['POST'])
def register():
    """Unified registration endpoint"""
    logger.info("Registration request received")

    if not EMAIL_PASSWORD:
        logger.error("EMAIL_PASSWORD not configured")
        return jsonify({'status': 'fail', 'message': 'Email configuration error'}), 500

    data = request.json
    logger.info(f"Received data: {data}")

    if not data:
        return jsonify({'status': 'fail', 'message': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'participant').strip()
    program = data.get('program', '').strip()
    registration_interest = (data.get('registration_interest', '') or data.get('message', '')).strip()

    logger.info(f"Parsed data - Name: {name}, Email: {email}, Role: {role}, Program: {program}")

    if not name or not email:
        return jsonify({'status': 'fail', 'message': 'Missing required fields: name and email'}), 400

    try:
        is_program_registration = bool(program)
        admin_msg = EmailMessage()

        if is_program_registration:
            admin_msg['Subject'] = 'New Program Registration - Ethiopian Cultural Heritage'
            program_names = {
                'basket-weaving': 'Traditional Basket Weaving',
                'coffee-ceremony': 'Ethiopian Coffee Ceremony',
                'textile-arts': 'Traditional Textile Arts',
                'pottery': 'Pottery & Clay Arts',
                'culinary': 'Culinary Heritage',
                'immersion': 'Cultural Immersion Program'
            }
            program_display = program_names.get(program, program)

            admin_content = f"""=== NEW PROGRAM REGISTRATION ===

Full Name: {name}
Email Address: {email}
Role: {role.title()}
Interested Program: {program_display}

"""
            if registration_interest:
                admin_content += f"Additional Information:\n{registration_interest}\n\n"
            admin_content += "=" * 40 + f"\nRegistration submitted at: {datetime.datetime.now()}\n"

        else:
            if role.lower() == 'organization':
                admin_msg['Subject'] = 'New Interest Registration - Art Exhibition Website (Organization)'
                admin_content = f"Organization Registration\n\nName: {name}\nEmail: {email}\nRole: {role}"
            elif role.lower() == 'artist':
                admin_msg['Subject'] = 'New Interest Registration - Art Exhibition Website (Artist)'
                admin_content = f"Artist Registration\nName: {name}\nEmail: {email}\nRole: {role}"
            else:
                admin_msg['Subject'] = 'New Interest Registration - Art Exhibition Website'
                admin_content = f"General Registration\nName: {name}\nEmail: {email}\nRole: {role}"

            if registration_interest:
                admin_content += f"\nAdditional Info: {registration_interest}"
            admin_content += f"\n\nSubmitted at: {datetime.datetime.now()}"

        admin_msg['From'] = EMAIL_ADDRESS
        admin_msg['To'] = ', '.join(TO_EMAILS)
        admin_msg.set_content(admin_content)

        logger.info("Attempting to connect to SMTP server...")
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465, timeout=15) as smtp:  # timeout added
            logger.info("SMTP connection established")
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("SMTP login successful")

            smtp.send_message(admin_msg)
            logger.info("Admin notification sent")

            if is_program_registration:
                user_msg = EmailMessage()
                user_msg['Subject'] = 'Registration Confirmation - Ethiopian Cultural Heritage Programs'
                user_msg['From'] = EMAIL_ADDRESS
                user_msg['To'] = email

                reg_id = f"ECH-{datetime.datetime.now().strftime('%Y%m%d')}-{hash(email) % 10000:04d}"

                user_content = f"""Dear {name},

Thank you for your interest in our Ethiopian Cultural Heritage Programs!

We received your registration with these details:

• Name: {name}
• Email: {email}
• Role: {role.title()}
• Program: {program_display}
"""
                if registration_interest:
                    user_content += f"• Message: {registration_interest}\n"
                user_content += f"• Registration ID: {reg_id}\n\n"
                user_content += "We will contact you within 2-3 business days.\n\nBest regards,\nEthiopian Cultural Heritage Team"

                user_msg.set_content(user_content)

                try:
                    smtp.send_message(user_msg)
                    logger.info("User confirmation email sent")
                except Exception as e:
                    logger.error(f"Failed to send user confirmation: {str(e)}")

                return jsonify({
                    'status': 'success',
                    'message': 'Registration submitted successfully! Please check your email for confirmation.',
                    'registration_id': reg_id
                }), 200

        return jsonify({'status': 'success', 'message': 'Registration sent successfully!'}), 200

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        return jsonify({'status': 'fail', 'message': 'Email authentication failed. Check credentials.'}), 500
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Email delivery failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'status': 'fail', 'message': 'Registration failed. Try again later.'}), 500

@app.route('/send-email', methods=['POST'])
def send_email_redirect():
    logger.info("Legacy /send-email endpoint called - redirecting to /register")
    return register()

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
