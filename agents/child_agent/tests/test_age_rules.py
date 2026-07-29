from app.services.age_adaptation_service import classify_age_group, get_adaptive_recommendations

def test_classify_age_group():
    # Early Childhood
    assert classify_age_group(0) == "EARLY_CHILDHOOD"
    assert classify_age_group(5) == "EARLY_CHILDHOOD"
    
    # Primary School
    assert classify_age_group(6) == "PRIMARY_SCHOOL"
    assert classify_age_group(10) == "PRIMARY_SCHOOL"
    
    # Middle School
    assert classify_age_group(11) == "MIDDLE_SCHOOL"
    assert classify_age_group(13) == "MIDDLE_SCHOOL"
    
    # High School
    assert classify_age_group(14) == "HIGH_SCHOOL"
    assert classify_age_group(17) == "HIGH_SCHOOL"
    
    # College
    assert classify_age_group(18) == "COLLEGE"
    assert classify_age_group(25) == "COLLEGE"

def test_get_adaptive_recommendations():
    # Early Childhood rules
    rec_early = get_adaptive_recommendations(3, "Early Childhood Education")
    assert rec_early["age_group"] == "EARLY_CHILDHOOD"
    assert "Play-based" in rec_early["recommended_study_duration"]
    assert rec_early["financial_independence_level"] == "None"
    
    # Primary School rules
    rec_primary = get_adaptive_recommendations(8, "Primary School")
    assert rec_primary["age_group"] == "PRIMARY_SCHOOL"
    assert rec_primary["parent_supervision_level"] == "Moderate to High (Guided supervision)"
    assert "pocket-money" in rec_primary["financial_independence_level"]
    
    # College rules
    rec_college = get_adaptive_recommendations(20, "University")
    assert rec_college["age_group"] == "COLLEGE"
    assert rec_college["parent_supervision_level"] == "Low (Independent adult)"
    assert rec_college["financial_independence_level"] == "High (Personal banking, budgeting, independent expense tracking)"
