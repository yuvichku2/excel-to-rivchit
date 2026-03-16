import streamlit as st
import pandas as pd
import io

# כותרת האפליקציה
st.set_page_config(page_title="ממיר אקסל לרווחית", layout="centered")
st.title("🏦 ממיר דפי בנק לפורמט רווחית")
st.write("העלה קובץ אקסל, בצע מיפוי עמודות והורד קובץ TXT מוכן לקליטה.")

# 1. העלאת קובץ
uploaded_file = st.file_uploader("בחר קובץ אקסל (xlsx)", type=["xlsx"])

if uploaded_file:
    # קריאת האקסל לתצוגה מקדימה
    df_input = pd.read_excel(uploaded_file)
    st.write("### תצוגה מקדימה של הקובץ שהועלה:")
    st.dataframe(df_input.head(5))

    st.divider()
    
    # 2. שלב המיפוי
    st.write("### מיפוי עמודות")
    st.info("בחר איזה טור מהאקסל שלך מתאים לכל שדה ברווחית:")
    
    col_options = ["---"] + list(df_input.columns)
    
    c1, c2 = st.columns(2)
    with c1:
        date_col = st.selectbox("תאריך (due_date)", options=col_options)
        debit_col = st.selectbox("חובה (debit)", options=col_options)
        asmacta_col = st.selectbox("אסמכתא (asmacta) - אופציונלי", options=col_options)
    with c2:
        credit_col = st.selectbox("זכות (credit)", options=col_options)
        desc_col = st.selectbox("פרטים (pratim)", options=col_options)

    # כפתור ביצוע
    if st.button("צור קובץ להורדה 🚀"):
        if "---" in [date_col, debit_col, credit_col, desc_col]:
            st.error("חובה למפות את שדות התאריך, החובה, הזכות והפרטים.")
        else:
            try:
                # לוגיקת העיבוד (מבוסס על הדוגמה הרווחית [cite: 1])
                output_df = pd.DataFrame()
                
                # העתקת הנתונים לפי המיפוי
                output_df['due_date'] = pd.to_datetime(df_input[date_col], dayfirst=True).dt.strftime('%d/%m/%y')
                output_df['debit'] = pd.to_numeric(df_input[debit_col], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
                output_df['credit'] = pd.to_numeric(df_input[credit_col], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
                output_df['pratim'] = df_input[desc_col].fillna("")
                output_df['asmacta'] = df_input[asmacta_col].fillna("") if asmacta_col != "---" else ""
                
                # הוספת מספר שורה כפי שמופיע במקור [cite: 1]
                output_df.insert(0, 'line_num', range(1, len(output_df) + 1))
                
                # יצירת ה-String של ה-TXT (מופרד בטאבים)
                buffer = io.StringIO()
                output_df.to_csv(buffer, sep='\t', index=False, encoding='utf-8-sig')
                
                st.success("הקובץ מוכן!")
                st.download_button(
                    label="📥 הורד קובץ TXT לרווחית",
                    data=buffer.getvalue(),
                    file_name="rovit_import.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"אירעה שגיאה בעיבוד: {e}")