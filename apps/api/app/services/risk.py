from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Pond, RiskAssessment, RecommendedAction

def clamp(x): return max(0.0, min(1.0, float(x)))

def assess_pond(db: Session, pond: Pond) -> RiskAssessment:
    missing = sum(v is None for v in [pond.latitude, pond.longitude, pond.dam_height_m, pond.crest_length_m, pond.total_storage_thousand_m3])
    hazard = 0.45
    vulnerability = clamp(((pond.dam_height_m or 5) / 15) * 0.6 + (0.2 if pond.duplicate_candidate else 0))
    exposure = clamp((pond.total_storage_thousand_m3 or 50) / 500)
    anomaly = 0.0
    uncertainty = clamp(missing / 5 + (0.25 if pond.coordinate_quality in ["unknown", "estimated"] else 0))
    score = clamp(settings.hazard_weight*hazard + settings.vulnerability_weight*vulnerability + settings.exposure_weight*exposure + settings.anomaly_weight*anomaly + settings.uncertainty_weight*uncertainty)
    level = "high" if score >= .65 else "medium" if score >= .4 else "low"
    ra = RiskAssessment(pond_id=pond.pond_id, hazard_score=hazard, vulnerability_score=vulnerability, exposure_score=exposure, anomaly_score=anomaly, uncertainty_score=uncertainty, screening_score=score, risk_level=level, model_version=settings.risk_model_version, evidence={"formula":"weighted_sum", "not_probability": True, "missing_fields": missing})
    db.add(ra); db.flush()
    action = "field_inspection" if level == "high" else "remote_review" if level == "medium" else "monitor"
    db.add(RecommendedAction(pond_id=pond.pond_id, risk_assessment_id=ra.risk_assessment_id, action=action, reason=f"{level} screening score with uncertainty {uncertainty:.2f}", priority={"high":1,"medium":2,"low":3}[level]))
    db.commit(); db.refresh(ra)
    return ra
