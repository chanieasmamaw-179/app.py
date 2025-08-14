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
    return "Bethe-EL Cultural Training Institute Email Server is running! Use POST /register for workshop registrations."

@app.route('/form.js')
def serve_javascript():
    """Serve the JavaScript file for form handling"""
    javascript_content = """
document.addEventListener('DOMContentLoaded', function() {
    // Get the current domain for API calls
    const API_BASE_URL = window.location.hostname === 'localhost' ? 
        'http://localhost:5000' : 
        'https://your-flask-app-name.onrender.com';  // Replace with your actual Flask app URL

    // Handle workshop registration forms, contact forms, and general inquiry forms
    const forms = document.querySelectorAll('form[id*="registration"], form[id*="Registration"], form[id*="contact"], form[id*="Contact"], form[id*="workshop"], form[id*="Workshop"], form[id*="inquiry"], form[id*="Inquiry"]');

    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); // Prevent default form submission

            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]') || 
                            form.querySelector('#submitBtn') || 
                            form.querySelector('button');
            const messageDiv = form.querySelector('#message') || 
                             document.getElementById('message') || 
                             form.querySelector('.message') ||
                             form.querySelector('.form-message');

            // Disable submit button and show loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.textContent || submitBtn.value;
                submitBtn.textContent = 'Submitting...';
                submitBtn.setAttribute('data-original-text', originalText);
            }

            // Hide previous messages
            if (messageDiv) {
                messageDiv.style.display = 'none';
            }

            // Collect form data - flexible field detection for cultural institute forms
            const formData = {
                name: form.querySelector('#name, [name="name"], input[placeholder*="name" i], input[placeholder*="Name"]')?.value?.trim() || '',
                
                email: form.querySelector('#email, [name="email"], input[type="email"], input[placeholder*="email" i]')?.value?.trim() || '',
                
                phone: form.querySelector('#phone, [name="phone"], input[type="tel"], input[placeholder*="phone" i]')?.value?.trim() || '',
                
                workshop: form.querySelector('#workshop, [name="workshop"], select[name*="workshop"], #program, [name="program"]')?.value || '',
                
                experience_level: form.querySelector('#experience, [name="experience"], select[name*="experience"], #level, [name="level"]')?.value || '',
                
                message: form.querySelector('#message-text, #message, [name="message"], textarea, input[name*="comment"]')?.value?.trim() || '',
                
                preferred_schedule: form.querySelector('#schedule, [name="schedule"], select[name*="schedule"], select[name*="time"]')?.value || '',
                
                participant_type: form.querySelector('#participant-type, [name="participant_type"], #role, [name="role"]')?.value || 'individual',
                
                cultural_background: form.querySelector('#background, [name="background"], [name="cultural_background"]')?.value?.trim() || '',
                
                special_requirements: form.querySelector('#requirements, [name="requirements"], [name="special_needs"]')?.value?.trim() || '',
                
                how_heard: form.querySelector('#how_heard, [name="how_heard"], select[name*="source"]')?.value || '',
                
                form_type: determineFormType(form)
            };

            console.log('Submitting form data:', formData);

            try {
                // Use the API base URL for the request
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    // Success
                    if (messageDiv) {
                        messageDiv.className = 'message success form-success';
                        messageDiv.innerHTML = `<div class="success-icon">✓</div><div class="success-text">${result.message}</div>`;
                        messageDiv.style.display = 'block';
                    }

                    // Reset form
                    form.reset();

                    // Show registration ID if provided
                    if (result.registration_id) {
                        setTimeout(() => {
                            if (messageDiv) {
                                messageDiv.innerHTML += '<br><div class="registration-id"><strong>Registration ID: ' + result.registration_id + '</strong></div>';
                            }
                        }, 1000);
                    }

                    // Auto-scroll to message if it's not visible
                    if (messageDiv) {
                        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }

                } else {
                    // Error from server
                    if (messageDiv) {
                        messageDiv.className = 'message error form-error';
                        messageDiv.innerHTML = `<div class="error-icon">⚠</div><div class="error-text">${result.message || 'Registration failed. Please try again.'}</div>`;
                        messageDiv.style.display = 'block';
                    }
                }

            } catch (error) {
                // Network or other error
                console.error('Registration Error:', error);
                if (messageDiv) {
                    messageDiv.className = 'message error form-error';
                    messageDiv.innerHTML = '<div class="error-icon">⚠</div><div class="error-text">Registration service temporarily unavailable. Please try again later.</div>';
                    messageDiv.style.display = 'block';
                }
            } finally {
                // Re-enable submit button
                if (submitBtn) {
                    submitBtn.disabled = false;
                    const originalText = submitBtn.getAttribute('data-original-text') || 'Submit';
                    submitBtn.textContent = originalText;
                }
            }
        });
    });

    // Helper function to determine form type
    function determineFormType(form) {
        const formId = form.id.toLowerCase();
        const formClass = form.className.toLowerCase();
        
        if (formId.includes('workshop') || formClass.includes('workshop')) {
            return 'workshop_registration';
        }
        if (formId.includes('contact') || formClass.includes('contact')) {
            return 'contact_inquiry';
        }
        if (formId.includes('general') || formClass.includes('general')) {
            return 'general_inquiry';
        }
        // Default based on presence of workshop field
        const hasWorkshop = form.querySelector('#workshop, [name="workshop"], select[name*="workshop"]');
        return hasWorkshop ? 'workshop_registration' : 'general_inquiry';
    }
});

// Enhanced validation functions
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('message') || 
                      document.querySelector('.message') || 
                      document.querySelector('.form-message');
    if (messageDiv) {
        messageDiv.className = 'message form-message ' + type;
        messageDiv.innerHTML = `<div class="${type}-text">${message}</div>`;
        messageDiv.style.display = 'block';

        // Auto-hide success messages after 8 seconds
        if (type === 'success') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 8000);
        }
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    // Allow various international phone formats
    const phoneRegex = /^[\\+]?[1-9]?[0-9]{7,15}$/;
    return phoneRegex.test(phone.replace(/[\\s\\-\\(\\)]/g, ''));
}

function validateForm(form) {
    const name = form.querySelector('#name, [name="name"]')?.value?.trim();
    const email = form.querySelector('#email, [name="email"]')?.value?.trim();
    const phone = form.querySelector('#phone, [name="phone"]')?.value?.trim();

    if (!name) {
        showMessage('Please enter your full name', 'error');
        return false;
    }

    if (!email) {
        showMessage('Please enter your email address', 'error');
        return false;
    }

    if (!validateEmail(email)) {
        showMessage('Please enter a valid email address', 'error');
        return false;
    }

    if (phone && !validatePhone(phone)) {
        showMessage('Please enter a valid phone number', 'error');
        return false;
    }

    return true;
}

// Enhanced form validation with real-time feedback
document.addEventListener('DOMContentLoaded', function() {
    // Email validation
    const emailInputs = document.querySelectorAll('#email, [name="email"], input[type="email"]');
    emailInputs.forEach(emailInput => {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            if (email && !validateEmail(email)) {
                showMessage('Please enter a valid email address', 'error');
                this.classList.add('invalid');
            } else {
                this.classList.remove('invalid');
            }
        });
    });

    // Phone validation
    const phoneInputs = document.querySelectorAll('#phone, [name="phone"], input[type="tel"]');
    phoneInputs.forEach(phoneInput => {
        phoneInput.addEventListener('blur', function() {
            const phone = this.value.trim();
            if (phone && !validatePhone(phone)) {
                showMessage('Please enter a valid phone number', 'error');
                this.classList.add('invalid');
            } else {
                this.classList.remove('invalid');
            }
        });
    });

    // Name validation
    const nameInputs = document.querySelectorAll('#name, [name="name"]');
    nameInputs.forEach(nameInput => {
        nameInput.addEventListener('blur', function() {
            const name = this.value.trim();
            if (name && name.length < 2) {
                showMessage('Please enter your full name', 'error');
                this.classList.add('invalid');
            } else {
                this.classList.remove('invalid');
            }
        });
    });
});

// Add CSS for better form styling
const style = document.createElement('style');
style.textContent = `
    .message {
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        display: none;
        font-family: Arial, sans-serif;
    }
    .message.success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .message.error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .success-icon, .error-icon {
        display: inline-block;
        margin-right: 8px;
        font-weight: bold;
    }
    .registration-id {
        margin-top: 10px;
        font-size: 14px;
        color: #0c5460;
    }
    input.invalid, select.invalid, textarea.invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
    button:disabled, input[type="submit"]:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;
document.head.appendChild(style);
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
        # Test SMTP connection
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("SMTP connection successful!")

            # Send test email
            msg = EmailMessage()
            msg['Subject'] = 'Test Email - Bethe-EL Cultural Institute'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = ', '.join(TO_EMAILS)
            msg.set_content('This is a test email to verify the email configuration is working for Bethe-EL Cultural Training Institute.')

            smtp.send_message(msg)
            return jsonify({'status': 'success', 'message': 'Test email sent successfully!'})

    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Email test failed: {str(e)}'}), 500

@app.route('/register', methods=['POST'])
def register():
    """Unified registration endpoint for Bethe-EL Cultural Training Institute"""
    logger.info("Registration request received")

    # Check if email password is configured
    if not EMAIL_PASSWORD:
        logger.error("EMAIL_PASSWORD not configured")
        return jsonify({'status': 'fail', 'message': 'Email configuration error'}), 500

    data = request.json
    logger.info(f"Received data: {data}")

    if not data:
        logger.error("No data provided in request")
        return jsonify({'status': 'fail', 'message': 'No data provided'}), 400

    # Extract form data with enhanced field mapping for cultural institute
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    workshop = data.get('workshop', '').strip()
    experience_level = data.get('experience_level', '').strip()
    message = data.get('message', '').strip()
    preferred_schedule = data.get('preferred_schedule', '').strip()
    participant_type = data.get('participant_type', 'individual').strip()
    cultural_background = data.get('cultural_background', '').strip()
    special_requirements = data.get('special_requirements', '').strip()
    how_heard = data.get('how_heard', '').strip()
    form_type = data.get('form_type', 'general_inquiry').strip()

    logger.info(f"Parsed data - Name: {name}, Email: {email}, Workshop: {workshop}, Type: {form_type}")

    # Validate required fields
    if not name or not email:
        logger.error("Missing required fields")
        return jsonify({'status': 'fail', 'message': 'Missing required fields: name and email'}), 400

    # Email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'status': 'fail', 'message': 'Please enter a valid email address'}), 400

    try:
        # Create admin notification email
        admin_msg = EmailMessage()

        # Workshop names mapping for Ethiopian cultural programs
        workshop_names = {
            'basket-weaving': 'Traditional Ethiopian Basket Weaving',
            'coffee-ceremony': 'Ethiopian Coffee Ceremony Workshop',
            'textile-arts': 'Traditional Ethiopian Textile Arts',
            'pottery': 'Ethiopian Pottery & Clay Arts',
            'culinary': 'Ethiopian Culinary Heritage',
            'immersion': 'Cultural Immersion Program',
            'language': 'Amharic Language Classes',
            'music-dance': 'Traditional Music & Dance',
            'art-painting': 'Ethiopian Art & Painting',
            'jewelry-making': 'Traditional Jewelry Making'
        }

        if form_type == 'workshop_registration' and workshop:
            # Workshop registration email
            workshop_display = workshop_names.get(workshop, workshop.replace('-', ' ').title())
            admin_msg['Subject'] = f'New Workshop Registration - {workshop_display}'

            admin_content = "=== NEW WORKSHOP REGISTRATION ===\n\n"
            admin_content += f"Workshop: {workshop_display}\n"
            admin_content += f"Participant Name: {name}\n"
            admin_content += f"Email Address: {email}\n"
            
            if phone:
                admin_content += f"Phone Number: {phone}\n"
            
            admin_content += f"Participant Type: {participant_type.replace('_', ' ').title()}\n"
            
            if experience_level:
                admin_content += f"Experience Level: {experience_level.replace('_', ' ').title()}\n"
            
            if preferred_schedule:
                admin_content += f"Preferred Schedule: {preferred_schedule.replace('_', ' ').title()}\n"
            
            if cultural_background:
                admin_content += f"Cultural Background: {cultural_background}\n"
            
            if special_requirements:
                admin_content += f"Special Requirements: {special_requirements}\n"
            
            if how_heard:
                admin_content += f"How They Heard About Us: {how_heard.replace('_', ' ').title()}\n"

            if message:
                admin_content += f"\nAdditional Message:\n{message}\n"

            admin_content += "\n" + "=" * 50 + "\n"
            admin_content += f"Registration submitted: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            # Generate registration ID for workshops
            reg_id = f"BEL-{datetime.datetime.now().strftime('%Y%m%d')}-{hash(email) % 10000:04d}"

        else:
            # General inquiry or contact form
            admin_msg['Subject'] = 'New Inquiry - Bethe-EL Cultural Training Institute'
            
            admin_content = "=== NEW GENERAL INQUIRY ===\n\n"
            admin_content += f"Name: {name}\n"
            admin_content += f"Email: {email}\n"
            
            if phone:
                admin_content += f"Phone: {phone}\n"
            
            if participant_type != 'individual':
                admin_content += f"Inquiry Type: {participant_type.replace('_', ' ').title()}\n"
            
            if cultural_background:
                admin_content += f"Cultural Background: {cultural_background}\n"
            
            if how_heard:
                admin_content += f"How They Heard About Us: {how_heard.replace('_', ' ').title()}\n"

            if message:
                admin_content += f"\nMessage:\n{message}\n"
            
            admin_content += f"\nSubmitted: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            reg_id = None

        admin_msg['From'] = EMAIL_ADDRESS
        admin_msg['To'] = ', '.join(TO_EMAILS)
        admin_msg.set_content(admin_content)

        # Send admin notification
        logger.info("Attempting to connect to SMTP server...")
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            logger.info("SMTP connection established")
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("SMTP login successful")

            smtp.send_message(admin_msg)
            logger.info("Admin notification email sent successfully!")

            # Send user confirmation
            user_msg = EmailMessage()
            user_msg['From'] = EMAIL_ADDRESS
            user_msg['To'] = email

            if form_type == 'workshop_registration' and workshop:
                # Workshop registration confirmation
                user_msg['Subject'] = 'Workshop Registration Confirmation - Bethe-EL Cultural Training Institute'
                
                user_content = f"Dear {name},\n\n"
                user_content += "ሰላም (Selam)! Peace and blessings!\n\n"
                user_content += "Thank you for your interest in our Ethiopian Cultural Heritage Programs at Bethe-EL Cultural Training Institute!\n\n"
                user_content += "We have received your workshop registration with the following details:\n\n"
                user_content += f"• Workshop: {workshop_display}\n"
                user_content += f"• Participant: {name}\n"
                user_content += f"• Email: {email}\n"
                
                if phone:
                    user_content += f"• Phone: {phone}\n"
                    
                user_content += f"• Registration ID: {reg_id}\n\n"
                
                user_content += "NEXT STEPS:\n"
                user_content += "• Our cultural heritage experts will review your registration\n"
                user_content += "• We will contact you within 2-3 business days to discuss:\n"
                user_content += "  - Workshop schedule and availability\n"
                user_content += "  - Materials and preparation needed\n"
                user_content += "  - Location details and cultural guidelines\n\n"
                
                user_content += "WORKSHOP LOCATION:\n"
                user_content += "Cultural District, Heritage Center Building\n"
                user_content += "Jerusalem, Israel\n\n"
                
                user_content += "CONTACT INFORMATION:\n"
                user_content += "Phone: +972-52-609-1347\n"
                user_content += "Email: info@beiteltaba.org\n"
                user_content += "Office Hours: Sunday-Thursday 9AM-6PM, Friday 9AM-2PM\n\n"
                
                user_content += "We look forward to sharing the rich traditions of Ethiopian heritage with you!\n\n"
                user_content += "With warm regards,\n"
                user_content += "Bethe-EL Cultural Training Institute Team\n"
                user_content += "Preserving Ethiopian-Israeli Heritage Through Art & Craft"

            else:
                # General inquiry confirmation
                user_msg['Subject'] = 'Thank You for Your Inquiry - Bethe-EL Cultural Training Institute'
                
                user_content = f"Dear {name},\n\n"
                user_content += "ሰላም (Selam)! Peace and blessings!\n\n"
                user_content += "Thank you for reaching out to Bethe-EL Cultural Training Institute.\n\n"
                user_content += "We have received your inquiry and our team will respond within 1-2 business days.\n\n"
                user_content += "In the meantime, we invite you to learn more about our cultural heritage programs:\n"
                user_content += "• Traditional Ethiopian Basket Weaving\n"
                user_content += "• Sacred Coffee Ceremony Workshops\n"
                user_content += "• Textile Arts and Natural Dyeing\n"
                user_content += "• Ethiopian Pottery and Clay Arts\n"
                user_content += "• Culinary Heritage Classes\n"
                user_content += "• Cultural Immersion Programs\n\n"
                user_content += "CONTACT INFORMATION:\n"
                user_content += "Phone: +972-52-609-1347\n"
                user_content += "Email: info@beiteltaba.org\n"
                user_content += "Address: Cultural District, Heritage Center Building, Jerusalem, Israel\n\n"
                user_content += "With warm regards,\n"
                user_content += "Bethe-EL Cultural Training Institute Team"

            user_msg.set_content(user_content)
            smtp.send_message(user_msg)
            logger.info("User confirmation email sent successfully!")

            if reg_id:
                return jsonify({
                    'status': 'success',
                    'message': 'Workshop registration submitted successfully! Please check your email for confirmation and next steps.',
                    'registration_id': reg_id
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'Thank you for your inquiry! We will respond within 1-2 business days.'
                }), 200

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        return jsonify(
            {'status': 'fail', 'message': 'Email authentication failed. Please check email credentials.'}), 500
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Email delivery failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return jsonify({'status': 'fail', 'message': 'Registration failed. Please try again later.'}), 500

@app.route('/send-email', methods=['POST'])
def send_email_redirect():
    """Legacy endpoint - redirects to unified register endpoint for backward compatibility"""
    logger.info("Legacy /send-email endpoint called - redirecting to /register")
    return register()

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
