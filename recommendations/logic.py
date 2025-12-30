def get_recommendations(assessment):
    """
    Simple rule-based recommendation engine.
    """
    score = assessment.score
    recommendations = {
        'careers': [],
        'skills': [],
        'jobs': []
    }
    
    if score > 80:
        recommendations['careers'] = ['Data Analyst', 'Software Developer']
        recommendations['skills'] = ['Python', 'SQL', 'Data Visualization']
    elif score > 50:
        recommendations['careers'] = ['Digital Marketer', 'Sales Executive']
        recommendations['skills'] = ['Communication', 'Social Media Marketing', 'Excel']
    else:
        recommendations['careers'] = ['Customer Support', 'Data Entry']
        recommendations['skills'] = ['Typing', 'Basic Computer Skills', 'English']
        
    return recommendations
