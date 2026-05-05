import streamlit as st
import pandas as pd
import io

# הגדרות עמוד
st.set_page_config(page_title="Bank to Rovachit DAT Converter", layout="centered")

# הצגת מספר גרסה לוודא עדכניות
st.sidebar.info("גרסת אפליקציה: 5.0 (Final DAT Fix)")

st.title("🏦 ממיר דפי בנק לפורמט DAT (רווחית)")
st.write("תיקון מבנה הקובץ והתאמה מלאה לייבוא")

# 1. העלאת הקובץ
uploaded_file = st.file_uploader("העלה קובץ אקסל או CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # קריאה ראשונית של הקובץ
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='cp1255')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("הקובץ נטען!")

        # 2. הגדרות מבנה
        mode = st.radio("מבנה הסכומים בקובץ:", 
                        ("טור סכום אחד (יתרה)", "שני טורים (חובה וזכות)"))
        
        include_header = st.checkbox("כלול שורת כותרת בקובץ ה-DAT (מומלץ לנסות בלי אם הייבוא נכשל)", value=False)

        cols = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            date_col = st.selectbox("טור תאריך:", cols)
            desc_col = st.selectbox("טור פרטים:", cols)
        with col2:
            ref_col = st.selectbox("טור אסמכתא:", cols)
            if mode == "טור סכום אחד (יתרה)":
                amount_col = st.selectbox("טור סכום:", cols)
            else:
                src_debit_col = st.selectbox("טור חובה מקורי:", cols)
                src_credit_col = st.selectbox("טור זכות מקורי:", cols)

        if st.button("צור קובץ DAT סופי"):
            # 3. עיבוד הנתונים
            if mode == "טור סכום אחד (יתרה)":
                df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
                df['f_debit'] = df[amount_col].apply(lambda x: abs(x) if x < 0 else 0)
                df['f_credit'] = df[amount_col].apply(lambda x: x if x > 0 else 0)
            else:
                df['f_debit'] = pd.to_numeric(df[src_debit_col], errors='coerce').abs().fillna(0)
                df['f_credit'] = pd.to_numeric(df[src_credit_col], errors='coerce').abs().fillna(0)

            # בניית הטבלה לייצוא
            final_df = pd.DataFrame({
                'Date': df[date_col],
                'Description': df[desc_col],
                'Reference': df[ref_col],
                'Debit': df['f_debit'],
                'Credit': df['f_credit']
            })

            # 4. ייצוא מוקפד ל-DAT
            # שימוש ב-lineterminator מבטיח הפרדת שורות תקינה בווינדוס
            output = io.StringIO()
            final_df.to_csv(output, sep='\t', index=False, header=include_header, 
                            encoding='cp1255', lineterminator='\r\n')
            
            st.write("תצוגה מקדימה של הנתונים:")
            st.dataframe(final_df.head())

            st.download_button(
                label="📥 הורד קובץ DAT מתוקן",
                data=output.getvalue(),
                file_name="bank_data_fixed.dat",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"שגיאה: {e}")
