import streamlit as st
import pandas as pd
import io

# הגדרות עמוד
st.set_page_config(page_title="Bank to Rovachit DAT Converter", layout="centered")

# הצגת מספר גרסה לוודא עדכניות
st.sidebar.info("גרסת אפליקציה: 4.0 (Dual Column Support)")

st.title("🏦 ממיר דפי בנק לפורמט DAT (רווחית)")
st.write("תמיכה בטור סכום אחד או בטורי חובה וזכות נפרדים")

# 1. העלאת הקובץ
uploaded_file = st.file_uploader("העלה קובץ אקסל או CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # זיהוי סוג הקובץ וקריאה מתאימה
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='cp1255')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("הקובץ נטען בהצלחה!")

        # 2. בחירת מבנה הקובץ
        mode = st.radio("איך מופיעים הסכומים בקובץ המקור?", 
                        ("טור סכום אחד (יתרה עם +/-)", "שני טורים נפרדים (חובה וזכות)"))

        cols = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            date_col = st.selectbox("בחר טור תאריך:", cols)
            desc_col = st.selectbox("בחר טור פרטים/תיאור:", cols)
        with col2:
            ref_col = st.selectbox("בחר טור אסמכתא:", cols)
            
            if mode == "טור סכום אחד (יתרה עם +/-)":
                amount_col = st.selectbox("בחר טור סכום (יתרה):", cols)
            else:
                src_debit_col = st.selectbox("בחר טור חובה במקור:", cols)
                src_credit_col = st.selectbox("בחר טור זכות במקור:", cols)

        if st.button("הכן קובץ להורדה"):
            # 3. לוגיקה של חובה וזכות
            if mode == "טור סכום אחד (יתרה עם +/-)":
                df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
                df['final_debit'] = df[amount_col].apply(lambda x: abs(x) if x < 0 else 0)
                df['final_credit'] = df[amount_col].apply(lambda x: x if x > 0 else 0)
            else:
                # שימוש בטורים הקיימים והפיכתם למספר חיובי
                df['final_debit'] = pd.to_numeric(df[src_debit_col], errors='coerce').abs().fillna(0)
                df['final_credit'] = pd.to_numeric(df[src_credit_col], errors='coerce').abs().fillna(0)

            # 4. יצירת טבלה סופית נקייה
            final_df = pd.DataFrame({
                'תאריך': df[date_col],
                'פרטים': df[desc_col],
                'אסמכתא': df[ref_col],
                'חובה': df['final_debit'],
                'זכות': df['final_credit']
            })

            st.write("תצוגה מקדימה:")
            st.dataframe(final_df.head())

            # 5. יצירת קובץ DAT
            buffer = io.StringIO()
            final_df.to_csv(buffer, sep='\t', index=False, encoding='cp1255')
            
            st.download_button(
                label="📥 הורד קובץ DAT לרווחית",
                data=buffer.getvalue(),
                file_name="bank_statement.dat",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"אירעה שגיאה: {e}")
