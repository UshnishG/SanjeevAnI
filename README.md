# Hospital Management System

A comprehensive web-based Hospital Management System built with Flask that streamlines hospital operations, enhances patient care, and optimizes medical record management.

DEPLOYED LINK : https://sanjeevani.up.railway.app

## 🏥 Overview

This Hospital Management System (HMS) provides an integrated platform for hospital administrators, doctors, and patients to manage healthcare operations efficiently. The system features role-based access control, medical record management, appointment scheduling, diagnosis tracking, and an AI-powered medical chatbot.

## ✨ Features

### For Administrators
- Manage doctors and medical staff
- Add and manage patients
- Monitor hospital operations
- View and manage appointments across the hospital
- Generate reports and analytics

### For Doctors
- View assigned patients
- Record diagnoses and treatments
- Manage medical records
- Schedule and track appointments
- View patient history and medical data
- Calendar view for appointments

### For Patients
- Book appointments with specialists
- View personal medical records
- Access diagnosis history
- Communicate with healthcare providers
- AI-assisted medical information

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **AI Chatbot**: Google's Gemini AI API
- **Authentication**: Werkzeug Security
- **Data Visualization**: (Optional feature to be implemented)

## 🚀 Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   GEMINI_API_KEY=your_gemini_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

5. Initialize the database:
   ```bash
   python app.py  # The database will be created on first run
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Access the application at: http://127.0.0.1:5000

## 📊 Database Schema

The system uses the following database structure:

- **Admin**: System administrators
- **Doctor**: Medical professionals
- **Patient**: Patient information and records
- **Diagnosis**: Patient diagnoses
- **MedicalRecord**: Patient medical history
- **Appointment**: Scheduled appointments
- **DoctorPatient**: Relationship between doctors and patients

## 👥 Default Users

The system is pre-populated with the following users:

### Administrators
- Username: admin_aayush, Password: admin@123
- Username: admin_ushnish, Password: admin#456
- Username: admin_utsav, Password: admin!789

### Doctors
- Username: dr_rajesh, Password: doc@123 (Cardiology)
- Username: dr_priya, Password: pedia#456 (Pediatrics)
- Username: dr_amit, Password: ortho789 (Orthopedics)
- Username: dr_ananya, Password: neuro101 (Neurology)

### Patients
- Email: rahul.v@example.com, Password: patient@123
- Email: neha.g@example.com, Password: neha#456

## 🤖 AI Medical Chatbot

The system includes an AI-powered medical assistant built with Google's Gemini AI. The chatbot can:

- Provide general medical information
- Offer personalized responses based on patient records (for logged-in patients)
- Direct users to appropriate medical resources
- Handle basic medical queries

Note: The chatbot always recommends consulting with a healthcare professional for specific medical advice.

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👨‍💻 Developers

- Ushnish Ghosal - System Architecture & Backend Development
- Aayush Mishra - Frontend Development
- Utsav Opal - Database Management & Security

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For any questions or support, please contact the team at:
- Email: hospital.management.system@example.com

---

© 2025 Hospital Management System. All Rights Reserved.
