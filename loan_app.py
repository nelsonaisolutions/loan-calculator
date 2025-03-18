import streamlit as st
import pandas as pd

def calculate_loan(principal, taeg, duration_months, insurance_amount):
    """Calculates loan details based on principal, TAEG, duration, and insurance.

    Args:
        principal (float): The total loan amount (in €).
        taeg (float): The annual interest rate (TAEG/APR) as a percentage.
        duration_months (int): The loan duration in months.
        insurance_amount (float): The monthly insurance cost.

    Returns:
        dict: A dictionary containing the loan details:
            - monthly_payment (float): The monthly payment amount.
            - total_cost (float): The total cost of the loan (interest paid).
            - total_paid (float): The total amount paid over the loan duration.
            - cost_percentage (float): The cost as a percentage of the loan.
            - insurance_total_cost: The total insurance cost.
            - amortization_table (DataFrame): The amortization table.
    """
    if principal <= 0 or taeg <= 0 or duration_months <= 0:
        raise ValueError(get_translation("Les valeurs doivent être positives."))

    monthly_rate = taeg / 100 / 12
    monthly_payment_without_insurance = principal * (monthly_rate * (1 + monthly_rate) ** duration_months) / ((1 + monthly_rate) ** duration_months - 1)
    monthly_payment_with_insurance = monthly_payment_without_insurance + insurance_amount

    total_paid = monthly_payment_with_insurance * duration_months
    total_cost = total_paid - principal
    cost_percentage = (total_cost / principal) * 100
    insurance_total_cost = insurance_amount * duration_months

    # Amortization table
    amortization_table = create_amortization_table(principal, monthly_rate, monthly_payment_without_insurance, duration_months, insurance_amount)

    return {
        "monthly_payment": monthly_payment_with_insurance,
        "total_cost": total_cost,
        "total_paid": total_paid,
        "cost_percentage": cost_percentage,
        "insurance_total_cost": insurance_total_cost,
        "amortization_table": amortization_table
    }

def create_amortization_table(principal, monthly_rate, monthly_payment, duration_months, insurance_amount):
    """Creates an amortization table for the loan."""
    data = []
    remaining_balance = principal
    for month in range(1, duration_months + 1):
        capital_beginning = remaining_balance
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        if remaining_balance < 0:
            remaining_balance = 0
        total_payment = monthly_payment + insurance_amount
        data.append([month, capital_beginning, principal_payment, interest_payment, insurance_amount, total_payment])

    df = pd.DataFrame(data, columns=[get_translation("Mois"), get_translation("Capital Restant Du en Début de Période"), get_translation("Capital Amorti"), get_translation("Intérêts"), get_translation("Assurance"), get_translation("Total Echeance")])

    # Calculate the totals BEFORE formatting (while still numeric)
    total_capital_amorti = df[get_translation("Capital Amorti")].sum()
    total_interest_paid = df[get_translation("Intérêts")].sum()
    total_insurance = df[get_translation("Assurance")].sum()
    total_echeance = df[get_translation("Total Echeance")].sum()

    # NOW format with commas for display
    df[get_translation("Capital Restant Du en Début de Période")] = df[get_translation("Capital Restant Du en Début de Période")].map(lambda x: f"{x:,.2f}")
    df[get_translation("Capital Amorti")] = df[get_translation("Capital Amorti")].map(lambda x: f"{x:,.2f}")
    df[get_translation("Intérêts")] = df[get_translation("Intérêts")].map(lambda x: f"{x:,.2f}")
    df[get_translation("Assurance")] = df[get_translation("Assurance")].map(lambda x: f"{x:,.2f}")
    df[get_translation("Total Echeance")] = df[get_translation("Total Echeance")].map(lambda x: f"{x:,.2f}")

    # Add the total row with already formatted numbers
    total_row = pd.DataFrame({
        get_translation("Mois"): [get_translation("Total")], 
        get_translation("Capital Restant Du en Début de Période"): [""], 
        get_translation("Capital Amorti"): [f"{total_capital_amorti:,.2f}"], 
        get_translation("Intérêts"): [f"{total_interest_paid:,.2f}"], 
        get_translation("Assurance"): [f"{total_insurance:,.2f}"], 
        get_translation("Total Echeance"): [f"{total_echeance:,.2f}"]
    })
    df = pd.concat([df, total_row], ignore_index=True)

    return df

def display_loan_details(loan_data):
    """Displays the loan details in a Streamlit table."""
    results = {
        get_translation("Mensualité"): f"{loan_data['monthly_payment']:,.2f} €",
        get_translation("Coût Total"): f"{loan_data['total_cost']:,.2f} €",
        get_translation("Total Remboursé"): f"{loan_data['total_paid']:,.2f} €",
        get_translation("Coût en % du Prêt"): f"{loan_data['cost_percentage']:.2f} %",
        get_translation("Coût Assurance Total"): f"{loan_data['insurance_total_cost']:,.2f} €",
    }
    st.table(results.items())

def update_insurance_percentage():
    """Updates the insurance percentage based on the fixed amount."""
    if st.session_state.insurance_amount:
        st.session_state.insurance_percentage = (st.session_state.insurance_amount / st.session_state.principal) * 100
    else:
        st.session_state.insurance_percentage = 0.0

def update_insurance_amount():
    """Updates the fixed insurance amount based on the percentage."""
    if st.session_state.insurance_percentage:
        st.session_state.insurance_amount = (st.session_state.insurance_percentage / 100) * st.session_state.principal
    else:
        st.session_state.insurance_amount = 0.0

def update_duration_months():
    """Updates the duration in months based on years."""
    if "duration_years" in st.session_state:
        st.session_state.duration_months = int(st.session_state.duration_years * 12)

def update_duration_years():
    """Updates the duration in years based on months."""
    if "duration_months" in st.session_state:
        st.session_state.duration_years = int(round(st.session_state.duration_months / 12))

def highlight_total_row(df):
    """Highlights the total row in grey."""
    def highlight(row):
        is_total_row = row.name == len(df) - 1
        if is_total_row:
            return ['background-color: #f0f0f0'] * len(row)
        return [''] * len(row)
    return df.style.apply(highlight, axis=1)

# Translations dictionary
translations = {
    "Calculateur de Prêt 💸": {"Français": "Calculateur de Prêt 💸", "English": "Loan Calculator 💸"},
    "Calculez facilement les détails de votre prêt.": {"Français": "Calculez facilement les détails de votre prêt.", "English": "Easily calculate the details of your loan."},
    "Paramètres du Prêt": {"Français": "Paramètres du Prêt", "English": "Loan Parameters"},
    "Montant du Prêt (€)": {"Français": "Montant du Prêt (€)", "English": "Loan Amount (€)"},
    "TAEG (%)": {"Français": "TAEG (%)", "English": "APR (%)"},
    "Durée (mois)": {"Français": "Durée (mois)", "English": "Duration (months)"},
    "Assurance": {"Français": "Assurance", "English": "Insurance"},
    "Montant Assurance par mois (€)": {"Français": "Montant Assurance par mois (€)", "English": "Monthly Insurance Amount (€)"},
    "Calculer": {"Français": "Calculer", "English": "Calculate"},
    "Mensualité": {"Français": "Mensualité", "English": "Monthly Payment"},
    "Coût Total": {"Français": "Coût Total", "English": "Total Cost"},
    "Total Remboursé": {"Français": "Total Remboursé", "English": "Total Paid"},
    "Coût en % du Prêt": {"Français": "Coût en % du Prêt", "English": "Cost as % of Loan"},
    "Coût Assurance Total": {"Français": "Coût Assurance Total", "English": "Total Insurance Cost"},
    "Afficher le tableau d'amortissement": {"Français": "Afficher le tableau d'amortissement", "English": "Show Amortization Table"},
    "Mois": {"Français": "Mois", "English": "Month"},
    "Capital Restant Du en Début de Période": {"Français": "Capital Restant Du en Début de Période", "English": "Remaining Principal at Start of Period"},
    "Capital Amorti": {"Français": "Capital Amorti", "English": "Principal Paid"},
    "Intérêts": {"Français": "Intérêts", "English": "Interest"},
    "Assurance": {"Français": "Assurance", "English": "Insurance"},
    "Total Echeance": {"Français": "Total Echeance", "English": "Total Due"},
    "Total": {"Français": "Total", "English": "Total"},
    "Les valeurs doivent être positives.": {"Français": "Les valeurs doivent être positives.", "English": "Values must be positive."},
    "Ajustez les valeurs et cliquez sur 'Calculer' pour voir les détails de votre prêt. 💸": {"Français": "Ajustez les valeurs et cliquez sur 'Calculer' pour voir les détails de votre prêt. 💸", "English": "Adjust the values and click 'Calculate' to see the details of your loan. 💸"},
    "Assurance (%)": {"Français": "Assurance (%)", "English": "Insurance (%)"},  # THIS IS THE NEW LINE
    "Durée (années)": {"Français": "Durée (années)", "English": "Duration (years)"},  # THIS IS THE NEW LINE
}

def get_translation(text_key):
    """Returns the translation for the given text key in the selected language."""
    selected_language = st.session_state.language
    return translations[text_key][selected_language]

# Streamlit Interface
# Initialize session_state (This must be done BEFORE creating any widgets!)
st.session_state.setdefault("language", "Français")
st.session_state.setdefault("insurance_amount", 0.0)
st.session_state.setdefault("insurance_percentage", 0.0)
st.session_state.setdefault("principal", 30000.0)
st.session_state.setdefault("taeg", 4.45)
st.session_state.setdefault("duration_months", 57)
st.session_state.setdefault("duration_years", 57/12)  # Add this line to initialize years
st.session_state.setdefault("show_amortization_table", False)
st.session_state.setdefault("amortization_table", pd.DataFrame())
st.session_state.setdefault("loan_data", {})

st.sidebar.header("Language")
language = st.sidebar.selectbox("Select a language", ["Français", "English"], key="language")

st.title(get_translation("Calculateur de Prêt 💸"))
st.write(get_translation("Calculez facilement les détails de votre prêt."))

# Sidebar
st.sidebar.header(get_translation("Paramètres du Prêt"))
principal = st.sidebar.number_input(
    get_translation("Montant du Prêt (€)"), 
    min_value=1000, 
    step=1000,  # Using 1000 for easier whole number selection
    format="%d",  # This shows integers only (no decimals)
    key="principal"
)
taeg = st.sidebar.number_input(get_translation("TAEG (%)"), min_value=0.1, step=0.01, format="%.2f", key="taeg")

# Duration inputs - place months and years next to each other
col1, col2 = st.sidebar.columns(2)
with col1:
    duration_months = st.number_input(
        get_translation("Durée (mois)"), 
        min_value=1, 
        step=1, 
        key="duration_months",
        on_change=update_duration_years
    )

with col2:
    st.number_input(
        get_translation("Durée (années)"),
        min_value=1,
        max_value=50,
        step=1,
        key="duration_years",
        on_change=update_duration_months,
        format="%d"  # Integer format - no decimals
    )

# Insurance inputs
st.sidebar.header(get_translation("Assurance"))
insurance_amount = st.sidebar.number_input(
    get_translation("Montant Assurance par mois (€)"),
    min_value=0.0,
    step=1.0,
    format="%.2f",
    on_change=update_insurance_percentage,
    key="insurance_amount",
)

insurance_percentage = st.sidebar.number_input(
    get_translation("Assurance (%)"),
    min_value=0.0,
    step=0.01,
    format="%.2f",
    on_change=update_insurance_amount,
    key="insurance_percentage",
)

# Calculate Button
if st.button(get_translation("Calculer")):
    try:
        st.session_state.loan_data = calculate_loan(principal, taeg, duration_months, insurance_amount)
        st.session_state.amortization_table = st.session_state.loan_data["amortization_table"]
    except ValueError as e:
        st.error(f"Erreur : {e}")
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite : {e}")

# Display the loan data if exists
if "loan_data" in st.session_state and st.session_state.loan_data:
    display_loan_details(st.session_state.loan_data)

# Toggle Amortization Table Button
if st.button(get_translation("Afficher le tableau d'amortissement")):
    st.session_state.show_amortization_table = not st.session_state.show_amortization_table

# Display the amortization table if the button has been clicked and if the table exists
if st.session_state.show_amortization_table:
    if "amortization_table" in st.session_state:
        styled_table = highlight_total_row(st.session_state.amortization_table)
        st.dataframe(styled_table)

st.write(get_translation("Ajustez les valeurs et cliquez sur 'Calculer' pour voir les détails de votre prêt. 💸"))