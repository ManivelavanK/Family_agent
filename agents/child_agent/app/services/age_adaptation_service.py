def classify_age_group(age: int) -> str:
    if age < 6:
        return "EARLY_CHILDHOOD"
    elif 6 <= age <= 10:
        return "PRIMARY_SCHOOL"
    elif 11 <= age <= 13:
        return "MIDDLE_SCHOOL"
    elif 14 <= age <= 17:
        return "HIGH_SCHOOL"
    else:
        return "COLLEGE"

def get_adaptive_recommendations(age: int, education_stage: str) -> dict:
    # Classify age group first
    age_group = classify_age_group(age)
    
    # Recommendations mappings
    if age_group == "EARLY_CHILDHOOD":
        return {
            "age_group": age_group,
            "education_stage": "Early Childhood Education",
            "recommended_study_duration": "0-1 hour (Play-based learning)",
            "recommended_sleep_duration": "10-13 hours",
            "recommended_screen_time_limit": "Max 1 hour (High-quality programming)",
            "activity_recommendation": "Sensory play, drawing, story reading, outdoor running",
            "parent_supervision_level": "High (Constant supervision required)",
            "financial_independence_level": "None",
            "safety_monitoring_level": "High (Full supervision)"
        }
    elif age_group == "PRIMARY_SCHOOL":
        return {
            "age_group": age_group,
            "education_stage": "Primary / Elementary School",
            "recommended_study_duration": "1-2 hours (Homework & reading)",
            "recommended_sleep_duration": "9-11 hours",
            "recommended_screen_time_limit": "1-1.5 hours",
            "activity_recommendation": "Structured sports, arts, board games, basic puzzle-solving",
            "parent_supervision_level": "Moderate to High (Guided supervision)",
            "financial_independence_level": "Low (Basic pocket-money tracking, learning to save)",
            "safety_monitoring_level": "High (Supervised outdoor play & online activity)"
        }
    elif age_group == "MIDDLE_SCHOOL":
        return {
            "age_group": age_group,
            "education_stage": "Middle School / Junior High",
            "recommended_study_duration": "2-3 hours (Independent study & projects)",
            "recommended_sleep_duration": "9-10 hours",
            "recommended_screen_time_limit": "1.5-2 hours",
            "activity_recommendation": "Team sports, science clubs, music instruments, introductory coding",
            "parent_supervision_level": "Moderate (Encourage autonomy with check-ins)",
            "financial_independence_level": "Low to Moderate (Pocket-money tracking, budget-awareness basics)",
            "safety_monitoring_level": "Moderate (Digital wellness tracking & safety boundaries)"
        }
    elif age_group == "HIGH_SCHOOL":
        return {
            "age_group": age_group,
            "education_stage": "High School",
            "recommended_study_duration": "3-4 hours (Exam prep, career/interest exploration)",
            "recommended_sleep_duration": "8-10 hours",
            "recommended_screen_time_limit": "2-3 hours",
            "activity_recommendation": "Debate, community service, competitive sports, advanced creative projects",
            "parent_supervision_level": "Low to Moderate (Independence with coaching/guidance)",
            "financial_independence_level": "Moderate (Budgeting, part-time job management, savings goals)",
            "safety_monitoring_level": "Moderate (Check-ins, curfew alignment, online privacy awareness)"
        }
    else:  # COLLEGE
        return {
            "age_group": age_group,
            "education_stage": "College / Higher Education",
            "recommended_study_duration": "4+ hours (Self-directed learning, lectures, assignments)",
            "recommended_sleep_duration": "7-9 hours",
            "recommended_screen_time_limit": "Self-regulated (Educational & productive focus)",
            "activity_recommendation": "Internships, networking, career prep, campus clubs, gym/fitness",
            "parent_supervision_level": "Low (Independent adult)",
            "financial_independence_level": "High (Personal banking, budgeting, independent expense tracking)",
            "safety_monitoring_level": "Low (Strong safety check-ins and emergency contact alignment)"
        }
