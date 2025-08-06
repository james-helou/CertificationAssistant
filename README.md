# Simple Agentic Certification Assistant

A streamlined Microsoft certification recommendation system that uses **local data** + **OpenAI API** + **sequential AI agents** to create personalized study plans.

## 🎯 **What It Does**

1. **Goal Agent** - Analyzes your profile and recommends certifications
2. **Prerequisite Agent** - Checks if you meet requirements and identifies gaps
3. **Curriculum Agent** - Creates a detailed study plan with modules
4. **Schedule Agent** - Generates a personalized study schedule

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install openai
```

### **2. Run the Assistant**
```bash
python simple_certification_assistant.py
```

### **3. Follow the Prompts**
- Enter your current job role
- Describe your career goals
- List your technical background
- Specify your experience level
- Choose areas of interest
- Set available study hours

## 📁 **File Structure**

```
├── data/
│   └── certifications.json     # All Microsoft certifications data
├── simple_agents.py            # Agent classes and logic
├── simple_certification_assistant.py  # Main application
└── README_SIMPLE.md           # This file
```

## 🤖 **How the Agents Work**

### **Sequential Flow:**
```
User Profile → Goal Agent → Prerequisite Agent → Curriculum Agent → Schedule Agent → Final Roadmap
```

### **Context Sharing:**
- Each agent builds on the previous agent's work
- No repeated questions
- Intelligent handoffs between agents

## 📊 **Sample Output**

```
🎯 Simple Agentic Certification Assistant
============================================================

🤖 Executing GOAL Agent...
----------------------------------------
✅ Goal Agent completed successfully
📝 Successfully recommended 2 certifications

📋 Certification Recommendations:

1. Azure Fundamentals (AZ-900)
   Difficulty: Fundamental
   Study Time: 20-30 hours
   Reasoning: Perfect for beginners starting cloud journey

🔄 Handing off to PREREQUISITE Agent...
----------------------------------------
✅ Prerequisite Agent completed successfully
📝 Successfully analyzed prerequisites for AZ-900

📚 Prerequisites Analysis for AZ-900:
   Meets Prerequisites: ✅ Yes
   Confidence Level: high
   Timeline: 2-3 weeks

🔄 Handing off to CURRICULUM Agent...
----------------------------------------
✅ Curriculum Agent completed successfully
📝 Successfully created study plan for AZ-900

📖 Study Plan for AZ-900:
   Title: Azure Fundamentals
   Total Study Time: 20-30 hours
   Total Weeks: 3

   Modules to Study:
     1. Describe cloud concepts
     2. Describe Azure architecture and services
     3. Describe Azure management and governance
     4. Describe Azure security, privacy, compliance, and trust

🔄 Handing off to SCHEDULE Agent...
----------------------------------------
✅ Schedule Agent completed successfully
📝 Successfully created study schedule

📅 Study Schedule for AZ-900:
   Total Weeks: 3
   Hours per Week: 10
   Exam Date: TBD - 3 weeks from start

   Daily Schedule:
     Monday: 2.0 hours - Core concepts
     Tuesday: 2.0 hours - Hands-on practice
     Wednesday: 2.0 hours - Review and labs
     Thursday: 2.0 hours - Practice tests
     Friday: 2.0 hours - Weekly review
     Weekend: Rest and light review

🎯 FINAL CERTIFICATION ROADMAP
============================================================

📋 Selected Certification: az-900
📊 Recommendations Generated: 2
📚 Prerequisites Analyzed: ✅
📖 Study Plan Created: ✅
📅 Schedule Generated: ✅

🚀 Your agentic certification journey is complete!
```

## 🔧 **Customization**

### **Add More Certifications**
Edit `data/certifications.json` to add new certifications:

```json
{
  "id": "new-cert-id",
  "title": "New Certification Title",
  "description": "Description of the certification",
  "level": "Fundamental",
  "category": "Cloud",
  "prerequisites": "None",
  "estimated_study_time": "25-35 hours",
  "modules": ["Module 1", "Module 2", "Module 3"]
}
```

### **Modify Agent Logic**
Edit `simple_agents.py` to customize agent behavior:

```python
class GoalAgent(BaseAgent):
    def execute(self) -> AgentResult:
        # Custom logic here
        pass
```

## 🎯 **Benefits of This Approach**

✅ **Simple** - No external API dependencies  
✅ **Fast** - Local data, instant responses  
✅ **Reliable** - No network issues or API limits  
✅ **Customizable** - Easy to modify and extend  
✅ **Agentic** - True sequential agent interactions  
✅ **Context-Aware** - Agents share information  

## 🚀 **Next Steps**

1. **Run the assistant** and get your personalized roadmap
2. **Follow the study plan** created by the agents
3. **Track your progress** using the provided milestones
4. **Customize the data** to add more certifications as needed

---

**Ready to start your certification journey? Run `python simple_certification_assistant.py` and let the AI agents guide you! 🎉** 