"""
app.py — Streamlit UI for the Government Scheme Discovery Assistant.

Run with:
    streamlit run scheme_assistant/app.py
"""

from __future__ import annotations

import streamlit as st

from scheme_assistant.data import SchemeRepository
from scheme_assistant.eligibility import EligibilityChecker
from scheme_assistant.filters import SchemeFilter
from scheme_assistant.models import Scheme, UserProfile

# ---------------------------------------------------------------------------
# Constants — kept here so they are easy to extend
# ---------------------------------------------------------------------------

STATES: list[str] = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal",
]

CATEGORIES: list[str] = ["General", "SC", "ST", "OBC", "EWS"]
OCCUPATIONS: list[str] = [
    "Farmer", "Student", "Salaried", "Self-employed", "Unemployed", "Other"
]
GENDERS: list[str] = ["Male", "Female", "Other"]


# ---------------------------------------------------------------------------
# Cached singleton — loaded once per session
# ---------------------------------------------------------------------------

@st.cache_resource
def _get_repo() -> SchemeRepository:
    return SchemeRepository()


# ---------------------------------------------------------------------------
# Small UI helpers
# ---------------------------------------------------------------------------

def _scheme_card(scheme: Scheme, expanded: bool = False) -> None:
    """Render a single scheme inside a collapsible expander."""
    with st.expander(f"📋 {scheme.name}", expanded=expanded):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Description:** {scheme.description}")
            st.markdown(f"**Benefits:** {scheme.benefits}")
        with col2:
            st.markdown(f"**Department:** {scheme.department}")
            st.markdown(f"**Category:** {scheme.scheme_category}")
            state_label = scheme.state if scheme.state != "National" else "🇮🇳 National"
            st.markdown(f"**State:** {state_label}")

        st.divider()
        st.markdown("**Eligibility Criteria**")
        elig_col1, elig_col2, elig_col3 = st.columns(3)
        with elig_col1:
            age_range = (
                f"{scheme.min_age}–{scheme.max_age} yrs"
                if not (scheme.min_age == 0 and scheme.max_age == 120)
                else "Any age"
            )
            st.metric("Age", age_range)
        with elig_col2:
            income_label = (
                "No limit"
                if scheme.max_income >= 9_999_999
                else f"≤ ₹{scheme.max_income:,.0f}/yr"
            )
            st.metric("Max Income", income_label)
        with elig_col3:
            genders = ", ".join(scheme.eligible_genders)
            st.metric("Gender", genders)

        extra_col1, extra_col2 = st.columns(2)
        with extra_col1:
            cats = ", ".join(scheme.eligible_categories)
            st.markdown(f"**Social Category:** {cats}")
        with extra_col2:
            occs = ", ".join(scheme.eligible_occupations)
            st.markdown(f"**Occupation:** {occs}")

        if scheme.tags:
            st.markdown(
                " ".join(f"`{t}`" for t in scheme.tags),
                unsafe_allow_html=False,
            )


def _no_results_message(context: str = "") -> None:
    st.info(
        f"No schemes found{' for ' + context if context else ''}. "
        "Try adjusting your criteria."
    )


# ---------------------------------------------------------------------------
# Tab: Check My Eligibility
# ---------------------------------------------------------------------------

def _tab_eligibility(repo: SchemeRepository) -> None:
    st.subheader("Find Schemes You Are Eligible For")
    st.write(
        "Fill in your personal details below and click **Check Eligibility** "
        "to see schemes you qualify for."
    )

    with st.form("eligibility_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
            income = st.number_input(
                "Annual Income (₹)",
                min_value=0.0,
                max_value=10_000_000.0,
                value=100_000.0,
                step=5_000.0,
                format="%.0f",
            )
            state = st.selectbox("State", STATES)
        with col2:
            category = st.selectbox("Social Category", CATEGORIES)
            occupation = st.selectbox("Occupation", OCCUPATIONS)
            gender = st.selectbox("Gender", GENDERS)

        submitted = st.form_submit_button("✅ Check Eligibility", use_container_width=True)

    if submitted:
        # Validation — Streamlit widgets already constrain numeric ranges,
        # but we guard against edge cases explicitly.
        errors: list[str] = []
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120.")
        if income < 0:
            errors.append("Annual income cannot be negative.")
        if not state:
            errors.append("Please select a state.")

        if errors:
            for err in errors:
                st.error(err)
            return

        try:
            profile = UserProfile(
                age=int(age),
                annual_income=float(income),
                state=state,
                category=category,
                occupation=occupation,
                gender=gender,
            )
        except ValueError as exc:
            st.error(f"Invalid input: {exc}")
            return

        checker = EligibilityChecker()
        matched = checker.get_eligible(profile, repo.get_all())

        if matched:
            st.success(f"🎉 {len(matched)} scheme(s) found matching your profile!")
            for scheme in matched:
                _scheme_card(scheme)
        else:
            _no_results_message("your profile")


# ---------------------------------------------------------------------------
# Tab: Search Schemes
# ---------------------------------------------------------------------------

def _tab_search(repo: SchemeRepository) -> None:
    st.subheader("Search Schemes by Keyword")
    st.write(
        "Enter a keyword like **farmer**, **education**, **women**, **health**, "
        "or **loan** to find relevant schemes."
    )

    keyword = st.text_input("Search keyword", placeholder="e.g. farmer, scholarship, housing")

    if st.button("🔍 Search", use_container_width=True):
        kw = keyword.strip()
        if not kw:
            st.warning("Please enter a search keyword before searching.")
            return

        sf = SchemeFilter()
        results = sf.by_keyword(repo.get_all(), kw)

        if results:
            st.success(f"Found {len(results)} scheme(s) matching **'{kw}'**.")
            for scheme in results:
                _scheme_card(scheme)
        else:
            _no_results_message(f"keyword '{kw}'")


# ---------------------------------------------------------------------------
# Tab: Browse & Filter
# ---------------------------------------------------------------------------

def _tab_browse(repo: SchemeRepository) -> None:
    st.subheader("Browse All Schemes")
    st.write("Use the filters below to narrow down the scheme list.")

    all_categories = ["All"] + repo.all_scheme_categories()
    all_states = ["All"] + repo.all_states()

    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Filter by Scheme Category", all_categories, key="browse_cat")
    with col2:
        selected_state = st.selectbox("Filter by State", all_states, key="browse_state")

    sf = SchemeFilter()
    schemes = repo.get_all()
    schemes = sf.by_scheme_category(schemes, selected_category)
    schemes = sf.by_state(schemes, selected_state)

    st.write(f"Showing **{len(schemes)}** scheme(s).")

    if schemes:
        for scheme in schemes:
            _scheme_card(scheme)
    else:
        _no_results_message()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Government Scheme Discovery Assistant",
        page_icon="🏛️",
        layout="wide",
    )

    st.title("🏛️ Government Scheme Discovery Assistant")
    st.caption(
        "Discover Indian government schemes you may be eligible for — "
        "based on your personal profile."
    )

    repo = _get_repo()

    if not repo.get_all():
        st.error(
            "No scheme data is available. "
            "Please ensure schemes.json is present in the package directory."
        )
        return

    tab1, tab2, tab3 = st.tabs(
        ["✅ Check My Eligibility", "🔍 Search Schemes", "📂 Browse All Schemes"]
    )

    with tab1:
        _tab_eligibility(repo)
    with tab2:
        _tab_search(repo)
    with tab3:
        _tab_browse(repo)

    st.divider()
    st.caption(
        f"📦 {len(repo.get_all())} schemes loaded · "
        "Data is for demonstration purposes only."
    )


if __name__ == "__main__":
    main()
