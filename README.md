# 🏛️ Government Scheme Discovery Assistant

**Track:** AI for Governance & Citizen Services
**Event:** SkillUp Hackathon in collaboration with IBM SkillsBuild

An AI-powered assistant that matches citizens to government schemes based on
their eligibility, with search, browse, and multilingual support — built to
solve four use cases from the problem statement in one platform.

## 🔗 Live Demo

[Try it here](PASTE_YOUR_STREAMLIT_LINK_HERE_AFTER_DEPLOYING)

## 🖥️ Screenshots

*(drag your screenshots into this line once you save — see note below)*

## 🎯 Problem

Many citizens are unaware of the government schemes and public services
available to them, or find the information difficult to understand — and
language is often an added barrier.

## ✅ Solution

| Project idea from problem statement | How this app covers it |
|---|---|
| Government scheme discovery assistant | Profile form matches user to relevant schemes |
| Citizen eligibility checker for welfare programs | Same matching engine checks eligibility (age/income/occupation/state/gender) |
| AI-powered public services information bot | Search & chat-style querying across all schemes |
| Multilingual governance and policy explainer | Language-aware explanations of results |

## 🏗️ Architecture

Built with a clean, layered structure — UI and business logic are fully separated:

- `models.py` — dataclasses (`Scheme`, `UserProfile`) with validation in `__post_init__`
- `eligibility.py` — `EligibilityChecker` matches a profile against all schemes using AND-combined criteria
- `filters.py` — `SchemeFilter` handles keyword and category search
- `data.py` — `SchemeRepository` loads and manages scheme data from `schemes.json`
- `exceptions.py` — custom exceptions for invalid input instead of silent failures
- `app.py` — Streamlit UI only, with zero business logic
- `tests/` — pytest unit tests covering eligibility and filtering logic

## 🛠️ Tech Stack

- Python (OOP)
- Streamlit
- IBM Bob (LLM)
- pytest

## ▶️ Run Locally

\`\`\`bash
pip install -r requirements.txt
streamlit run scheme_assistant/app.py
\`\`\`

## 🔮 Future Improvements

- More regional languages
- Voice input for low-literacy users
- Direct application link-outs and document checklists

## ⚠️ Disclaimer

This is a hackathon prototype. Scheme details are illustrative — always verify
against official government portals before applying.
