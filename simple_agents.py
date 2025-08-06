import json 
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from openai import AzureOpenAI

class AgentType(Enum): 
    GOAL = "goal"
    PREREQUISITE = "prerequisite"
    CURRICULUM = "curriculum"
    SCHEDULE = "schedule"

@dataclass
class AgentContext:
    """Context shared between agents"""
    user_profile: Dict[str, Any]
    selected_certification: Optional[str] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    prerequisites_analysis: Optional[Dict[str, Any]] = None
    study_plan: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None

@dataclass
class AgentResult:
    """Result from an agent execution"""
    success: bool
    data: Dict[str, Any]
    message: str
    next_agent: Optional[AgentType] = None
    context_updates: Optional[Dict[str, Any]] = None

class CertificationData:
    """Load and manage certification data from local JSON file"""
    
    def __init__(self):
        self.certifications = self._load_certifications()
    
    def _load_certifications(self) -> List[Dict[str, Any]]:
        """Load certifications from JSON file"""
        try:
            with open('data/certifications.json', 'r') as f:
                data = json.load(f)
                return data.get('certifications', [])
        except FileNotFoundError:
            print("❌ certifications.json not found. Creating sample data...")
            return self._get_sample_certifications()
    
    def _get_sample_certifications(self) -> List[Dict[str, Any]]:
        """Fallback sample certifications"""
        return [
            {
                "id": "az-900",
                "title": "Azure Fundamentals",
                "description": "Learn cloud concepts and Azure services",
                "level": "Fundamental",
                "category": "Cloud",
                "prerequisites": "None",
                "estimated_study_time": "20-30 hours"
            },
            {
                "id": "ai-900",
                "title": "Azure AI Fundamentals",
                "description": "Learn AI and machine learning fundamentals",
                "level": "Fundamental",
                "category": "AI",
                "prerequisites": "None",
                "estimated_study_time": "30-40 hours"
            }
        ]
    
    def get_all_certifications(self) -> List[Dict[str, Any]]:
        """Get all certifications"""
        return self.certifications
    
    def search_certifications(self, query: str) -> List[Dict[str, Any]]:
        """Search certifications by query"""
        query_lower = query.lower()
        results = []
        
        for cert in self.certifications:
            title = cert.get('title', '').lower()
            description = cert.get('description', '').lower()
            category = cert.get('category', '').lower()
            cert_id = cert.get('id', '').lower()
            
            if (query_lower in title or 
                query_lower in description or 
                query_lower in category or 
                query_lower in cert_id):
                results.append(cert)
        
        return results
    
    def get_certification_by_id(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Get certification by ID"""
        for cert in self.certifications:
            if cert.get('id', '').lower() == cert_id.lower():
                return cert
        return None

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType, ai_client, cert_data: CertificationData):
        self.agent_type = agent_type
        self.ai_client = ai_client
        self.cert_data = cert_data
        self.context: Optional[AgentContext] = None
    
    def set_context(self, context: AgentContext):
        """Set the context for this agent"""
        self.context = context
    
    def get_ai_response(self, system_prompt: str, user_message: str) -> str:
        """Get response from OpenAI API"""
        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting AI response: {str(e)}"

class GoalAgent(BaseAgent):
    """Agent for analyzing user goals and recommending certifications"""
    
    def __init__(self, ai_client, cert_data: CertificationData):
        super().__init__(AgentType.GOAL, ai_client, cert_data)
    
    def execute(self) -> AgentResult:
        """Execute goal analysis and recommendation"""
        try:
            # Get all certifications
            all_certs = self.cert_data.get_all_certifications()
            
            # Prepare user message
            user_message = self._prepare_user_message(all_certs)
            
            # Get AI response
            system_prompt = """You are a Microsoft Certification Advisor. Based on the user's profile and available certifications, recommend 2-3 most suitable certifications. Consider their experience level, interests, and career goals. Respond in JSON format:
            {
                "recommendations": [
                    {
                        "certification_id": "az-900",
                        "title": "Azure Fundamentals",
                        "reasoning": "Perfect for beginners...",
                        "difficulty": "Fundamental",
                        "estimated_study_time": "20-30 hours"
                    }
                ],
                "selected_certification": "az-900",
                "next_agent": "prerequisite"
            }"""
            
            ai_response = self.get_ai_response(system_prompt, user_message)
            
            # Parse response (simplified)
            recommendations = self._parse_recommendations(ai_response, all_certs)
            
            if recommendations:
                selected_cert = recommendations[0].get('certification_id', 'az-900')
                
                return AgentResult(
                    success=True,
                    data={'recommendations': recommendations},
                    message=f"Successfully recommended {len(recommendations)} certifications",
                    next_agent=AgentType.PREREQUISITE,
                    context_updates={'selected_certification': selected_cert}
                )
            else:
                return AgentResult(
                    success=False,
                    data={'error': 'No recommendations generated'},
                    message="Failed to generate recommendations",
                    next_agent=AgentType.PREREQUISITE
                )
                
        except Exception as e:
            return AgentResult(
                success=False,
                data={'error': str(e)},
                message=f"Error in goal agent: {str(e)}",
                next_agent=AgentType.PREREQUISITE
            )
    
    def _prepare_user_message(self, certifications: List[Dict[str, Any]]) -> str:
        """Prepare user message with context and certifications"""
        context_info = f"User Profile: {self.context.user_profile}" if self.context else "No context"
        
        certs_info = "Available Certifications:\n"
        for cert in certifications:
            certs_info += f"- {cert['id'].upper()}: {cert['title']} ({cert['level']}) - {cert['description']}\n"
        
        return f"""
Based on this user profile and available certifications, recommend the most suitable Microsoft certifications:

{context_info}

{certs_info}

Please provide 2-3 specific recommendations with certification codes and detailed reasoning.
"""
    
    def _parse_recommendations(self, ai_response: str, all_certs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse AI response to extract recommendations"""
        try:
            # Simple parsing - look for certification IDs
            import re
            cert_ids = re.findall(r'[A-Z]{2}-\d{3,4}', ai_response.upper())
            
            recommendations = []
            for cert_id in cert_ids[:3]:  # Limit to 3 recommendations
                cert = self.cert_data.get_certification_by_id(cert_id)
                if cert:
                    recommendations.append({
                        'certification_id': cert_id.lower(),
                        'title': cert['title'],
                        'reasoning': f"Recommended based on user profile analysis",
                        'difficulty': cert['level'],
                        'estimated_study_time': cert['estimated_study_time']
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"Error parsing recommendations: {e}")
            # Fallback to basic recommendations
            return [
                {
                    'certification_id': 'az-900',
                    'title': 'Azure Fundamentals',
                    'reasoning': 'Great starting point for cloud computing',
                    'difficulty': 'Fundamental',
                    'estimated_study_time': '20-30 hours'
                }
            ]

class PrerequisiteAgent(BaseAgent):
    """Agent for analyzing prerequisites"""
    
    def __init__(self, ai_client, cert_data: CertificationData):
        super().__init__(AgentType.PREREQUISITE, ai_client, cert_data)
    
    def execute(self) -> AgentResult:
        """Execute prerequisite analysis"""
        try:
            cert_id = self.context.selected_certification if self.context else None
            if not cert_id:
                return AgentResult(
                    success=False,
                    data={'error': 'No certification selected'},
                    message="No certification selected for analysis",
                    next_agent=AgentType.CURRICULUM
                )
            
            # Get certification details
            cert = self.cert_data.get_certification_by_id(cert_id)
            if not cert:
                return AgentResult(
                    success=False,
                    data={'error': f'Certification {cert_id} not found'},
                    message=f"Certification {cert_id} not found",
                    next_agent=AgentType.CURRICULUM
                )
            
            # Prepare analysis
            analysis = {
                'certification_id': cert_id,
                'meets_prerequisites': True,  # Simplified for now
                'knowledge_gaps': ['Basic IT concepts'],
                'preparation_recommendations': [
                    {
                        'topic': 'Basic IT Concepts',
                        'resources': ['Microsoft Learn fundamentals'],
                        'estimated_time': '10-15 hours'
                    }
                ],
                'timeline': '2-3 weeks',
                'confidence_level': 'high'
            }
            
            return AgentResult(
                success=True,
                data={'prerequisites_analysis': analysis},
                message=f"Successfully analyzed prerequisites for {cert_id.upper()}",
                next_agent=AgentType.CURRICULUM,
                context_updates={'prerequisites_analysis': analysis}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={'error': str(e)},
                message=f"Error in prerequisite agent: {str(e)}",
                next_agent=AgentType.CURRICULUM
            )

class CurriculumAgent(BaseAgent):
    """Agent for creating study plans"""
    
    def __init__(self, ai_client, cert_data: CertificationData):
        super().__init__(AgentType.CURRICULUM, ai_client, cert_data)
    
    def execute(self) -> AgentResult:
        """Execute curriculum planning"""
        try:
            cert_id = self.context.selected_certification if self.context else None
            if not cert_id:
                return AgentResult(
                    success=False,
                    data={'error': 'No certification selected'},
                    message="No certification selected for curriculum planning",
                    next_agent=AgentType.SCHEDULE
                )
            
            # Get certification details
            cert = self.cert_data.get_certification_by_id(cert_id)
            if not cert:
                return AgentResult(
                    success=False,
                    data={'error': f'Certification {cert_id} not found'},
                    message=f"Certification {cert_id} not found",
                    next_agent=AgentType.SCHEDULE
                )
            
            # Create study plan
            study_plan = {
                'certification_id': cert_id,
                'title': cert['title'],
                'modules': cert.get('modules', []),
                'learning_paths': cert.get('learning_paths', []),
                'total_study_time': cert['estimated_study_time'],
                'weekly_breakdown': self._create_weekly_breakdown(cert),
                'resources': [
                    'Microsoft Learn modules',
                    'Official documentation',
                    'Practice tests',
                    'Hands-on labs'
                ]
            }
            
            return AgentResult(
                success=True,
                data={'study_plan': study_plan},
                message=f"Successfully created study plan for {cert_id.upper()}",
                next_agent=AgentType.SCHEDULE,
                context_updates={'study_plan': study_plan}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={'error': str(e)},
                message=f"Error in curriculum agent: {str(e)}",
                next_agent=AgentType.SCHEDULE
            )
    
    def _create_weekly_breakdown(self, cert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create weekly study breakdown"""
        total_hours = int(cert['estimated_study_time'].split('-')[0])
        weeks = max(1, total_hours // 10)  # Assume 10 hours per week
        
        breakdown = []
        for week in range(1, weeks + 1):
            breakdown.append({
                'week': week,
                'focus': f"Week {week} topics",
                'hours': min(10, total_hours - (week - 1) * 10),
                'activities': ['Study modules', 'Practice exercises', 'Review concepts']
            })
        
        return breakdown

class ScheduleAgent(BaseAgent):
    """Agent for creating study schedules"""
    
    def __init__(self, ai_client, cert_data: CertificationData):
        super().__init__(AgentType.SCHEDULE, ai_client, cert_data)
    
    def execute(self) -> AgentResult:
        """Execute schedule creation"""
        try:
            study_plan = self.context.study_plan if self.context else None
            user_profile = self.context.user_profile if self.context else {}
            
            if not study_plan:
                return AgentResult(
                    success=False,
                    data={'error': 'No study plan available'},
                    message="No study plan available for scheduling",
                    next_agent=None
                )
            
            # Create schedule
            study_time = user_profile.get('study_time', '10')
            try:
                study_hours = int(study_time.split()[0]) if study_time.strip() else 10
            except (ValueError, IndexError):
                study_hours = 10
            schedule = {
                'certification_id': study_plan['certification_id'],
                'total_weeks': len(study_plan['weekly_breakdown']),
                'hours_per_week': study_hours,
                'daily_schedule': self._create_daily_schedule(study_hours),
                'milestones': self._create_milestones(study_plan),
                'exam_date': f"TBD - {len(study_plan['weekly_breakdown'])} weeks from start"
            }
            
            return AgentResult(
                success=True,
                data={'schedule': schedule},
                message=f"Successfully created study schedule",
                next_agent=None,  # Final agent
                context_updates={'schedule': schedule}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={'error': str(e)},
                message=f"Error in schedule agent: {str(e)}",
                next_agent=None
            )
    
    def _create_daily_schedule(self, hours_per_week: int) -> Dict[str, Any]:
        """Create daily study schedule"""
        hours_per_day = hours_per_week / 5  # 5 days per week
        
        return {
            'monday': f"{hours_per_day:.1f} hours - Core concepts",
            'tuesday': f"{hours_per_day:.1f} hours - Hands-on practice",
            'wednesday': f"{hours_per_day:.1f} hours - Review and labs",
            'thursday': f"{hours_per_day:.1f} hours - Practice tests",
            'friday': f"{hours_per_day:.1f} hours - Weekly review",
            'weekend': "Rest and light review"
        }
    
    def _create_milestones(self, study_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create study milestones"""
        milestones = []
        for i, week in enumerate(study_plan['weekly_breakdown'], 1):
            focus = week.get('focus', f"Week {i} topics")
            milestones.append({
                'week': i,
                'milestone': f"Complete Week {i} topics",
                'description': f"Finish {focus}",
                'status': 'Pending'
            })
        
        # Add final milestone
        milestones.append({
            'week': len(study_plan['weekly_breakdown']) + 1,
            'milestone': 'Take certification exam',
            'description': 'Schedule and take the official exam',
            'status': 'Pending'
        })
        
        return milestones 