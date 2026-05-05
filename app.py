import streamlit as st
import pandas as pd
import io

# הגדרות עמוד
st.set_page_config(page_title="Bank to Rovachit DAT Converter", layout="centered")

# הצגת מספר גרסה בראש העמוד לוודא עדכניות
st.sidebar.info("גרסת אפליקציה: 3.0 (DAT Export)")

st.title("🏦 ממיר דפי בנק לפורמט DAT (רווחית)")
st.write("מפריד חובה/זכות, מתקן עברית ומייצא קובץ DAT")

# 1. העלאת הקובץ
uploaded_file = st.file_uploader("העלה קובץ אקסל או CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # זיהוי סוג הקובץ וקריאה מתאימה (טיפול בג'יבריש בקריאה)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='cp1255')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("הקובץ נטען בהצלחה!")

        # 2. בחירת העמודות הרלוונטיות
        cols = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            date_col = st.selectbox("בחר טור תאריך:", cols)
            desc_col = st.selectbox("בחר טור פרטים/תיאור:", cols)
        with col2:
            ref_col = st.selectbox("בחר טור אסמכתא:", cols)
            amount_col = st.selectbox("בחר טור סכום (יתרה):", cols)

        if st.button("הכן קובץ להורדה"):
            # 3. לוגיקה של חובה וזכות (הפרדה לערכים חיוביים)
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
            
            df['חובה'] = df[amount_col].apply(lambda x: abs(x) if x < 0 else 0)
            df['זכות'] = df[amount_col].apply(lambda x: x if x > 0 else 0)

            # 4. יצירת טבלה סופית נקייה
            final_df = pd.DataFrame({
                'תאריך': df[date_col],
                'פרטים': df[desc_col],
                'אסמכתא': df[ref_col],
                'חובה': df['חובה'],
                'זכות': df['זכות']
            })

            st.write("תצוגה מקדימה של הקובץ שיווצר:")
            st.dataframe(final_df.head())

            # 5. יצירת קובץ DAT (מופרד ב-Tabs ובקידוד עברית חלונות)
            buffer = io.StringIO()
            final_df.to_csv(buffer, sep='\t', index=False, encoding='cp1255')
            
            st.download_button(
                label="📥 הורד קובץ DAT לרווחית",
                data=buffer.getvalue(),
                file_name="bank_statement.dat",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"אירעה שגיאה בעיבוד הקובץ: {e}")
