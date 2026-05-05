import streamlit as st
import pandas as pd
import io

# הגדרות עמוד
st.set_page_config(page_title="Rovachit Bank Converter v6.1", layout="centered")

# הצגת מספר גרסה לוודא עדכניות
st.sidebar.info("גרסת אפליקציה: 6.1 (No Dependencies Fix)")

st.title("🏦 ממיר דפי בנק מותאם לרווחית")
st.write("מכין קובץ לפי ההנחיות: תאריך DD/MM/YY, מספר שורה 0, ואסמכתא מוגבלת.")

uploaded_file = st.file_uploader("העלה את קובץ דפי הבנק (SKYHALO)", type=['xlsx'])

if uploaded_file is not None:
    try:
        # קריאת הנתונים מהקובץ
        df_src = pd.read_excel(uploaded_file)
        st.success("קובץ המקור נטען בהצלחה!")
        
        if st.button("צור קובץ יעד לייבוא"):
            # 1. יצירת דאטה-פריים חדש לפי מבנה היעד
            new_df = pd.DataFrame()
            
            # עמודה 1: מספר שורה (תמיד 0)
            new_df['מס\' שורה'] = [0] * len(df_src)
            
            # עמודה 2: תאריך בפורמט DD/MM/YY
            date_col = 'תאריך פעולה'
            df_src[date_col] = pd.to_datetime(df_src[date_col], dayfirst=True, errors='coerce')
            new_df['תאריך'] = df_src[date_col].dt.strftime('%d/%m/%y')
            
            # עמודות 3-4: חובה וזכות
            amount_col = '$ זכות / חובה'
            # המרה למספר ליתר ביטחון
            df_src[amount_col] = pd.to_numeric(df_src[amount_col], errors='coerce').fillna(0)
            new_df['חובה'] = df_src[amount_col].apply(lambda x: abs(x) if x < 0 else 0)
            new_df['זכות'] = df_src[amount_col].apply(lambda x: x if x > 0 else 0)
            
            # עמודה 5: אסמכתא (עד 9 תווים)
            new_df['אסמכתא'] = df_src['אסמכתה'].astype(str).str.replace('.0', '', regex=False).str[:9]
            new_df['אסמכתא'] = new_df['אסמכתא'].replace('nan', '')
            
            # עמודה 6: פרטים
            new_df['פרטים'] = df_src['תיאור הפעולה'].astype(str)
            
            st.write("תצוגה מקדימה של הקובץ המוכן:")
            st.dataframe(new_df.head())
            
            # --- אפשרות 1: הורדה כקובץ טקסט (Tab Delimited) - ללא כותרות לפי ההנחיות ---
            buffer_txt = io.StringIO()
            new_df.to_csv(buffer_txt, sep='\t', index=False, encoding='cp1255', header=False)
            
            st.download_button(
                label="📥 הורד קובץ TXT לייבוא (ללא כותרות)",
                data=buffer_txt.getvalue(),
                file_name="bank_import_ready.txt",
                mime="text/plain"
            )
            
            # --- אפשרות 2: הורדה כאקסל (לביקורת) ---
            # משתמשים ב-openpyxl שהוא ברירת המחדל ב-Streamlit
            buffer_excel = io.BytesIO()
            new_df.to_excel(buffer_excel, index=False, engine='openpyxl')
            
            st.download_button(
                label="📊 הורד כקובץ אקסל (לביקורת)",
                data=buffer_excel.getvalue(),
                file_name="bank_import_check.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
