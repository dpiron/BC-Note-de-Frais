import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from datetime import date
import streamlit as st
import pandas as pd
from io import StringIO
from datetime import date


st.set_page_config(layout="centered", page_title="Note de Frais")
st.title("Note de Frais")

data = st.text_area('Paste from google sheets', value='Paste data here')

csvStringIO = StringIO(data)
df = pd.read_csv(csvStringIO, sep=";", header=None)

df = df.fillna(value='')
df.columns = ['Date', 'Description', 'Items', 'Source', 'Amount', 'Paid by']

for i in range(len(df['Date'])):
    date_str = df['Date'][i].split('-')
    date_int = [int(x) for x in date_str]
    date_obj = date(date_int[2], date_int[1], date_int[0])
    df['Date'][i] = date_obj

for i in range(len(df['Items'])):
    df['Items'][i] = df['Items'][i].split(',')

for i in range(len(df['Amount'])):
    df['Amount'][i] = float(df['Amount'][i].replace(',', '.'))

### split D and J
df_D = df[df['Paid by'] == 'D']
df_J = df[df['Paid by'] == 'J']

env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("TemplateNotedeFrais.html")


def generate(df, who, i):
    df = df.sort_values(by='Date').reset_index()

    range_rows = range(len(df['Date']))

    if who == 'D':
        name = 'Denis Piron'
        n_compte_receiver = 'BE58 0019 0996 7079'
    elif who == 'J':
        name = 'Julia Boyaval'
        n_compte_receiver = 'BE71 0019 4884 3669'

    n_input = st.number_input('Numéro de la note', value=i)
    submit = st.button(f'Générer note de frais - {name}', use_container_width=True)

    first_date = df['Date'][0]
    n_ndf = first_date.strftime('%y%m') + '-' + str(n_input)

    if submit:
        html = template.render(
            company='BOYAVAL CONSULTANCY SRL',
            company_address='Rue Félix Bovie 13/1, 1050 Ixelles',
            n_entreprise='0793.986.966',
            n_compte='BE41 9675 3464 9010',
            n_ndf=n_ndf,
            date=first_date,
            n_compte_receiver=n_compte_receiver,
            name=name,
            df=df,
            range_rows=range_rows
        )

        pdf = pdfkit.from_string(html, False, options={"enable-local-file-access": ""})
        st.balloons()

        st.download_button(
            "Download PDF",
            data=pdf,
            file_name=f"Note-de-Frais-{n_ndf}-{who}.pdf",
            mime="application/octet-stream",
            use_container_width=True
        )
    return


i = 1
col1, col2 = st.columns(2)

if not df_D.empty:
    with col1:
        generate(df_D, 'D', i)
    i += 1

if not df_J.empty:
    with col2:
        generate(df_J, 'J', i)
    i += 1

