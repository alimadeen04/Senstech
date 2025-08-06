# personalization.py

def get_personalized_thresholds(age, gender, weight):
    """
    Returns low and high threshold values based on age, gender, and weight.
    """
    if age < 13:
        return (0.5, 1.0)
    elif age >= 65:
        return (0.6, 1.2)
    elif gender.lower() == 'male':
        if weight > 90:
            return (0.8, 1.4)
        elif weight < 60:
            return (0.6, 1.2)
        else:
            return (0.7, 1.3)
    else:  # female or other
        if weight > 75:
            return (0.7, 1.2)
        elif weight < 50:
            return (0.5, 1.0)
        else:
            return (0.6, 1.1)

def get_status(creatinine_value, age, gender, weight):
    """
    Returns 'Low', 'Normal', or 'High' based on personalized thresholds.
    """
    low, high = get_personalized_thresholds(age, gender, weight)
    if creatinine_value < low:
        return "Low"
    elif creatinine_value > high:
        return "High"
    else:
        return "Normal"

def get_breakdown(status, age, gender, weight):
    """
    Returns a personalized explanation string based on the status and personal factors.
    """
    if status == "High":
        if gender.lower() == "male":
            return "Your creatinine level is elevated. In males with higher muscle mass, this may be normal, but kidney function should still be monitored."
        else:
            return "High creatinine may signal decreased kidney filtration. Please consult a healthcare provider."
    elif status == "Low":
        if age > 65:
            return "Low creatinine is common in older adults but may also indicate low muscle mass or liver conditions."
        else:
            return "Low creatinine may reflect low muscle mass or dietary factors. Consider a medical evaluation."
    else:
        return "Your creatinine level is normal for your profile. Keep monitoring and maintaining your health."
