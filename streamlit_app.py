import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from datetime import date
import streamlit as st
from streamlit.components.v1 import iframe
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

conn = connect(":memory:", adapter_kwargs={
    "gsheetaspi" : {
    "service_account_info" : {
        "type" : st.secrets["gcp_service_account"]["type"],
        "project_id" : st.secrets["gcp_service_account"]["project_id"],
        "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
        "private_key" : st.secrets["gcp_service_account"]["private_key"],
        "client_email" : st.secrets["gcp_service_account"]["client_email"],
        "client_id" : st.secrets["gcp_service_account"]["client_id"],
        "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
        }
    },
})


# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=7)
    rows = rows.fetchall()
    return rows


sheet_url = st.secrets["gcp_service_account"]["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')


# Print results.
for row in rows:
    st.write(f"row")


st.set_page_config(layout="centered", page_icon="🎓", page_title="Diploma Generator")
st.title("🎓 Diploma PDF Generator")

st.write(
    "This app shows you how you can use Streamlit to make a PDF generator app in just a few lines of code!"
)

left, right = st.columns(2)

right.write("Here's the template we'll be using:")

env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("TemplateNotedeFrais.html")



left.write("Fill in the data:")
form = left.form("template_form")
student = form.text_input("Student name")
course = form.selectbox(
    "Choose course",
    ["Report Generation in Streamlit", "Advanced Cryptography"],
    index=0,
)
grade = form.slider("Grade", 1, 100, 60)
submit = form.form_submit_button("Generate PDF")

if submit:
    html = template.render(
        company='BOYAVAL CONSULTANCY SRL',
        company_address='Rue Félix Bovie 13, 1050 Ixelles',
        n_entreprise='543256432654364543',
        n_tva='n_tva',
        n_compte='n_compte',
        n_ndf='2209-01',
        date_to_do='SEPTEMBRE 2022',
        n_compte_receiver='435643263',
        name='Denis Piron',
        course=course,
        grade=f"{grade}/100",
        date=date.today().strftime("%B %d, %Y"),
    )

    pdf = pdfkit.from_string(html, False, options={"enable-local-file-access": ""})
    st.balloons()

    right.success("🎉 Your diploma was generated!")
    # st.write(html, unsafe_allow_html=True)
    # st.write("")
    right.download_button(
        "⬇️ Download PDF",
        data=pdf,
        file_name="diploma.pdf",
        mime="application/octet-stream",
    )
