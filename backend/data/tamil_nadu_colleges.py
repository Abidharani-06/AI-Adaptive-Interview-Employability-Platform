"""
Comprehensive Registry of Tamil Nadu Colleges & Universities
============================================================
Contains major recognized engineering institutions, state universities,
national institutes, autonomous colleges, and deemed universities across Tamil Nadu.
"""

from typing import List, Dict, Any

TAMIL_NADU_COLLEGES: List[Dict[str, str]] = [
    {"name": "Indian Institute of Technology Madras (IIT Madras)", "district": "Chennai", "type": "National"},
    {"name": "National Institute of Technology Tiruchirappalli (NIT Trichy)", "district": "Tiruchirappalli", "type": "National"},
    {"name": "Indian Institute of Information Technology, Design and Manufacturing (IIITDM Kancheepuram)", "district": "Kanchipuram", "type": "National"},
    {"name": "College of Engineering, Guindy (CEG - Anna University)", "district": "Chennai", "type": "State University Campus"},
    {"name": "Madras Institute of Technology (MIT - Anna University)", "district": "Chennai", "type": "State University Campus"},
    {"name": "Alagappa College of Technology (ACT - Anna University)", "district": "Chennai", "type": "State University Campus"},
    {"name": "School of Architecture and Planning (SAP - Anna University)", "district": "Chennai", "type": "State University Campus"},
    {"name": "PSG College of Technology", "district": "Coimbatore", "type": "Autonomous / Government-Aided"},
    {"name": "Coimbatore Institute of Technology (CIT)", "district": "Coimbatore", "type": "Autonomous / Government-Aided"},
    {"name": "Government College of Technology (GCT)", "district": "Coimbatore", "type": "Government"},
    {"name": "Thiagarajar College of Engineering (TCE)", "district": "Madurai", "type": "Autonomous / Government-Aided"},
    {"name": "SSN College of Engineering (Sri Sivasubramaniya Nadar)", "district": "Chennai", "type": "Autonomous"},
    {"name": "Chennai Institute of Technology (CIT Chennai)", "district": "Chennai", "type": "Autonomous"},
    {"name": "SASTRA Deemed University", "district": "Thanjavur", "type": "Deemed University"},
    {"name": "Vellore Institute of Technology (VIT Vellore)", "district": "Vellore", "type": "Deemed University"},
    {"name": "Vellore Institute of Technology (VIT Chennai)", "district": "Chennai", "type": "Deemed University"},
    {"name": "SRM Institute of Science and Technology (Kattankulathur)", "district": "Chengalpattu", "type": "Deemed University"},
    {"name": "SRM Institute of Science and Technology (Ramapuram)", "district": "Chennai", "type": "Deemed University"},
    {"name": "Amrita Vishwa Vidyapeetham", "district": "Coimbatore", "type": "Deemed University"},
    {"name": "Kumaraguru College of Technology (KCT)", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Kongu Engineering College", "district": "Erode", "type": "Autonomous"},
    {"name": "Bannari Amman Institute of Technology", "district": "Erode", "type": "Autonomous"},
    {"name": "Government College of Engineering, Salem", "district": "Salem", "type": "Government"},
    {"name": "Government College of Engineering, Tirunelveli", "district": "Tirunelveli", "type": "Government"},
    {"name": "Government College of Engineering, Bargur", "district": "Krishnagiri", "type": "Government"},
    {"name": "Government College of Engineering, Thanjavur", "district": "Thanjavur", "type": "Government"},
    {"name": "Government College of Engineering, Bodinayakkanur", "district": "Theni", "type": "Government"},
    {"name": "Rajalakshmi Engineering College (REC)", "district": "Chennai", "type": "Autonomous"},
    {"name": "Sri Venkateswara College of Engineering (SVCE)", "district": "Sriperumbudur", "type": "Autonomous"},
    {"name": "St. Joseph's College of Engineering", "district": "Chennai", "type": "Autonomous"},
    {"name": "Mepco Schlenk Engineering College", "district": "Virudhunagar", "type": "Autonomous"},
    {"name": "National Engineering College", "district": "Thoothukudi", "type": "Autonomous"},
    {"name": "Sona College of Technology", "district": "Salem", "type": "Autonomous"},
    {"name": "Sri Krishna College of Engineering and Technology (SKCET)", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Sri Krishna College of Technology (SKCT)", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Sri Ramakrishna Engineering College (SREC)", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Dr. Mahalingam College of Engineering and Technology", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "R.M.K. Engineering College", "district": "Thiruvallur", "type": "Autonomous"},
    {"name": "R.M.D. Engineering College", "district": "Thiruvallur", "type": "Autonomous"},
    {"name": "Easwari Engineering College", "district": "Chennai", "type": "Autonomous"},
    {"name": "Meenakshi Sundararajan Engineering College", "district": "Chennai", "type": "Affiliated"},
    {"name": "Loyola-ICAM College of Engineering and Technology (LICET)", "district": "Chennai", "type": "Affiliated"},
    {"name": "Panimalar Engineering College", "district": "Chennai", "type": "Autonomous"},
    {"name": "Saveetha Engineering College", "district": "Chennai", "type": "Autonomous"},
    {"name": "Vel Tech Rangarajan Dr. Sagunthala R&D Institute", "district": "Chennai", "type": "Deemed University"},
    {"name": "B.S. Abdur Rahman Crescent Institute of Science and Technology", "district": "Chennai", "type": "Deemed University"},
    {"name": "Hindustan Institute of Technology and Science", "district": "Chennai", "type": "Deemed University"},
    {"name": "Karunya Institute of Technology and Sciences", "district": "Coimbatore", "type": "Deemed University"},
    {"name": "PSNA College of Engineering and Technology", "district": "Dindigul", "type": "Autonomous"},
    {"name": "Sethu Institute of Technology", "district": "Virudhunagar", "type": "Autonomous"},
    {"name": "Kamaraj College of Engineering and Technology", "district": "Virudhunagar", "type": "Autonomous"},
    {"name": "Francis Xavier Engineering College", "district": "Tirunelveli", "type": "Autonomous"},
    {"name": "Saranathan College of Engineering", "district": "Tiruchirappalli", "type": "Affiliated"},
    {"name": "K. Ramakrishnan College of Engineering", "district": "Tiruchirappalli", "type": "Autonomous"},
    {"name": "K. Ramakrishnan College of Technology", "district": "Tiruchirappalli", "type": "Autonomous"},
    {"name": "M. Kumarasamy College of Engineering", "district": "Karur", "type": "Autonomous"},
    {"name": "K.S. Rangasamy College of Technology", "district": "Namakkal", "type": "Autonomous"},
    {"name": "Paavai Engineering College", "district": "Namakkal", "type": "Autonomous"},
    {"name": "Muthayammal Engineering College", "district": "Namakkal", "type": "Autonomous"},
    {"name": "Vivekanandha College of Engineering for Women", "district": "Namakkal", "type": "Autonomous"},
    {"name": "Adhiyamaan College of Engineering", "district": "Krishnagiri", "type": "Autonomous"},
    {"name": "Velammal Engineering College", "district": "Chennai", "type": "Autonomous"},
    {"name": "Velammal College of Engineering and Technology", "district": "Madurai", "type": "Autonomous"},
    {"name": "Hindusthan College of Engineering and Technology", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Karpagam College of Engineering", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "SNS College of Technology", "district": "Coimbatore", "type": "Autonomous"},
    {"name": "Sree Sastha Institute of Engineering and Technology", "district": "Thiruvallur", "type": "Affiliated"},
    {"name": "Annamalai University (Faculty of Engineering & Technology)", "district": "Cuddalore", "type": "State University"},
    {"name": "Bharathiar University", "district": "Coimbatore", "type": "State University"},
    {"name": "Madurai Kamaraj University", "district": "Madurai", "type": "State University"},
    {"name": "Bharathidasan University", "district": "Tiruchirappalli", "type": "State University"},
    {"name": "Manonmaniam Sundaranar University", "district": "Tirunelveli", "type": "State University"},
    {"name": "Alagappa University", "district": "Karaikudi", "type": "State University"},
    {"name": "Periyar University", "district": "Salem", "type": "State University"},
    {"name": "Tamil Nadu Agricultural University (TNAU)", "district": "Coimbatore", "type": "State University"},
    {"name": "Other (Specify institution manually)", "district": "Other", "type": "Custom"}
]


def get_colleges_list() -> List[str]:
    """Returns sorted list of college names with 'Other' at the end."""
    names = [c["name"] for c in TAMIL_NADU_COLLEGES if c["name"] != "Other (Specify institution manually)"]
    names.sort()
    names.append("Other (Specify institution manually)")
    return names
