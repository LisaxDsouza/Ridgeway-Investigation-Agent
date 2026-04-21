import groq
from sqlalchemy.orm import Session
from ..config import settings
from ..models import Incident, Briefing
from datetime import datetime, timedelta

client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

class BriefingService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_morning_brief(self, site_id: str):
        # 1. Fetch all Incidents from the last night
        start = datetime.utcnow().replace(hour=22, minute=0) - timedelta(days=1)
        incidents = self.db.query(Incident).filter(
            Incident.site_id == site_id,
            Incident.created_at >= start
        ).all()
        
        if not incidents:
            return None

        # 2. Synthesize using Groq
        context = "\n".join([f"- Incident: {i.hypothesis}\n  Confidence: {i.confidence_level}\n  Action: {i.recommended_action}" for i in incidents])
        
        prompt = f"""
        Synthesize the following forensic incidents from the overnight shift at {site_id} into a 5-question morning brief.
        
        INCIDENTS:
        {context}
        
        STRUCTURE:
        Q1: What actually happened last night? (Brief overall summary)
        Q2: What was harmless? (Identify false positives/operational noise)
        Q3: What deserves escalation? (Identify high-confidence security events)
        Q4: What did the drone check? (Summarize visual verifications)
        Q5: What still needs follow-up? (List unresolved tasks)
        
        Keep it professional, high-agency, and concise.
        """
        try:
            response = await client.chat.completions.create(
                model=settings.safe_groq_model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
        except groq.RateLimitError:
            try:
                fallback_model = "llama-3.1-8b-instant"
                if settings.safe_groq_model == fallback_model: raise
                response = await client.chat.completions.create(
                    model=fallback_model,
                    messages=[{"role": "user", "content": prompt + "\n(Note: This is a fallback generation due to load.)"}]
                )
                content = response.choices[0].message.content
            except Exception:
                content = "ERROR: System capacity reached. Unable to generate brief at this time."
        except Exception as e:
            content = f"ERROR during briefing generation: {str(e)}"
        
        # 3. Persist
        briefing = Briefing(
            site_id=site_id,
            briefing_date=datetime.utcnow().date(),
            q1_summary=content, # For MVP, store whole blob or split
            export_text=content
        )
        self.db.add(briefing)
        self.db.commit()
        return briefing
