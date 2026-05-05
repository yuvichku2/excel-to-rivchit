import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Bank to Rovachit Converter", layout="wide")

st.title("🏦 ממיר דפי בנק לרווחית")
st.write("הפרדת חובה/זכות ותיקון עברית אוטומטי")

uploaded_file = st.file_uploader("העלה קובץ אקסל (XLSX) או קובץ CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # קריאת הקובץ
        if uploaded_file.name.endswith('.csv'):
            # ניסיון לקרוא בקידוד עברית של ווינדוס (מונע ג'יבריש)
            df = pd.read_csv(uploaded_file, encoding='cp1255')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("הקובץ נטען בהצלחה!")

        # בחירת טור הסכום (היתרה)
        column_name = st.selectbox("בחר את הטור שמכיל את הסכומים (חיובי/שלילי):", df.columns)

        # לוגיקה להפרדת חובה וזכות (ערכים חיוביים בלבד)
        df['חובה'] = df[column_name].apply(lambda x: abs(x) if x < 0 else 0)
        df['זכות'] = df[column_name].apply(lambda x: x if x > 0 else 0)

        # תצוגה מקדימה כדי שתוכל לוודא שהעברית תקינה
        st.subheader("תצוגה מקדימה (Preview)")
        st.dataframe(df.head(10))

        # יצירת קובץ להורדה בפורמט שמתאים לרווחית (CSV בקידוד עברית)
        output = io.StringIO()
        # ייצוא בקידוד cp1255 כדי שהעברית תישמר בייבוא לרווחית
        df.to_csv(output, index=False, encoding='cp1255')
        processed_data = output.getvalue()

        st.download_button(
            label="📥 הורד קובץ מוכן לרווחית",
            data=processed_data,
            file_name="converted_bank_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
        st.info("טיפ: וודא שטור הסכומים מכיל מספרים בלבד.")
