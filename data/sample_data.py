import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_students=100):
    """
    Generate sample data for the PPGE KPI Dashboard
    
    Parameters:
    - num_students: Number of student records to generate
    
    Returns:
    - DataFrame with sample data
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate student IDs
    student_ids = [f"S{i:04d}" for i in range(1, num_students + 1)]
    
    # Generate student names (simple pattern for demonstration)
    first_names = ["John", "Jane", "Carlos", "Maria", "Ahmed", "Sarah", "Michael", "Ana", 
                  "Luiz", "Amanda", "David", "Sofia", "Takashi", "Elena", "Wei", "Fatima"]
    last_names = ["Smith", "Silva", "Kim", "Patel", "Garcia", "Müller", "Wang", "Kowalski", 
                 "Tanaka", "Okafor", "Martinez", "Johnson", "Ali", "Ivanov", "Nguyen", "Santos"]
    
    student_names = [
        f"{np.random.choice(first_names)} {np.random.choice(last_names)}" 
        for _ in range(num_students)
    ]
    
    # Generate programs (Masters or Doctorate)
    programs = np.random.choice(["Masters", "Doctorate"], size=num_students, p=[0.6, 0.4])
    
    # Generate enrollment dates (within the last 5 years)
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2023, 8, 1)
    days_range = (end_date - start_date).days
    
    enrollment_dates = [
        start_date + timedelta(days=np.random.randint(0, days_range))
        for _ in range(num_students)
    ]
    
    # Generate defense dates (if applicable)
    # Masters typically take 2 years, Doctorate 4 years
    # Some students haven't defended yet
    defense_dates = []
    defense_statuses = []
    
    for i in range(num_students):
        if programs[i] == "Masters":
            avg_days = 365 * 2  # 2 years
            std_days = 180      # 6 months standard deviation
        else:  # Doctorate
            avg_days = 365 * 4  # 4 years
            std_days = 365      # 1 year standard deviation
        
        # Add random variation to the defense time
        defense_days = int(np.random.normal(avg_days, std_days))
        
        # Calculate defense date
        potential_defense_date = enrollment_dates[i] + timedelta(days=max(defense_days, 30))
        
        # Some students haven't defended yet (more recent enrollments are less likely to have defended)
        months_enrolled = (datetime.now() - enrollment_dates[i]).days / 30
        defense_probability = min(months_enrolled / avg_days * 30, 1.0)
        
        if np.random.random() < defense_probability and potential_defense_date <= datetime.now():
            defense_dates.append(potential_defense_date)
            
            # Most defenses are successful
            defense_statuses.append(np.random.choice(["Approved", "Failed"], p=[0.95, 0.05]))
        else:
            defense_dates.append(None)
            defense_statuses.append(None)
    
    # Generate advisor information
    advisor_ids = [f"A{i:03d}" for i in range(1, 16)]  # 15 advisors
    advisor_names = [
        "Dr. " + f"{np.random.choice(first_names)} {np.random.choice(last_names)}" 
        for _ in range(15)
    ]
    
    # Assign advisors to students
    student_advisor_ids = np.random.choice(advisor_ids, size=num_students)
    student_advisor_names = [advisor_names[advisor_ids.index(a_id)] for a_id in student_advisor_ids]
    
    # Generate departments
    departments = ["Computer Science", "Mathematics", "Physics", "Economics", 
                  "Linguistics", "Education", "Engineering", "Social Sciences"]
    
    student_departments = np.random.choice(departments, size=num_students)
    
    # Generate research areas
    research_areas = {
        "Computer Science": ["Machine Learning", "Computer Vision", "Algorithms", "Networks"],
        "Mathematics": ["Algebra", "Analysis", "Geometry", "Statistics"],
        "Physics": ["Quantum Mechanics", "Relativity", "Particle Physics", "Astrophysics"],
        "Economics": ["Microeconomics", "Macroeconomics", "Econometrics", "Development"],
        "Linguistics": ["Syntax", "Semantics", "Phonology", "Applied Linguistics"],
        "Education": ["Learning Theory", "Educational Technology", "Pedagogy", "Curriculum"],
        "Engineering": ["Civil", "Electrical", "Mechanical", "Chemical"],
        "Social Sciences": ["Sociology", "Anthropology", "Political Science", "Psychology"]
    }
    
    student_research_areas = [
        np.random.choice(research_areas[dept]) for dept in student_departments
    ]
    
    # Generate publication counts
    # More senior students and doctoral students tend to have more publications
    publication_counts = []
    
    for i in range(num_students):
        # Base count depends on program
        if programs[i] == "Masters":
            base_count = np.random.poisson(1)  # Masters students average 1 publication
        else:
            base_count = np.random.poisson(3)  # Doctoral students average 3 publications
        
        # Adjust based on time enrolled
        months_enrolled = (datetime.now() - enrollment_dates[i]).days / 30
        time_factor = min(months_enrolled / 36, 1.5)  # Cap at 1.5x for very senior students
        
        adjusted_count = int(base_count * time_factor)
        publication_counts.append(adjusted_count)
    
    # Create the DataFrame
    data = {
        "student_id": student_ids,
        "student_name": student_names,
        "program": programs,
        "enrollment_date": enrollment_dates,
        "defense_date": defense_dates,
        "defense_status": defense_statuses,
        "advisor_id": student_advisor_ids,
        "advisor_name": student_advisor_names,
        "department": student_departments,
        "research_area": student_research_areas,
        "publications": publication_counts
    }
    
    return pd.DataFrame(data)
