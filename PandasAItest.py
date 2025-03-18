import streamlit as st
import pandas as pd
import plotly.express as px
from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM

# ✅ Set up the Streamlit page
st.set_page_config(page_title="BEM&T CPK", page_icon="🤖", layout="wide")
st.title("🤖 BEMT CPK")

# ✅ File Uploader (Single File for Both Sections)
uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])

df = None
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.session_state["df"] = df  # Store in session state
        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")

col1, col2 = st.columns([2, 1])

# 📊 Column 1: Data Visualization
with col1:
    if df is not None:
        st.sidebar.header("📊 Customize Your Graph")

        graph_type = st.sidebar.radio("Select Graph Type:", ["Bar", "Line", "Scatter", "Pie"], horizontal=True)
        x_axis = st.sidebar.selectbox("Choose X-axis:", df.columns)
        y_axis = st.sidebar.multiselect("Choose Y-axis:", df.columns)

        st.markdown("### 📊 Data Visualization")
        if y_axis:  # Ensure at least one Y-axis is selected
            if graph_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis, title="Bar Chart")
            elif graph_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, title="Line Chart")
            elif graph_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis, title="Scatter Plot")
            elif graph_type == "Pie" and len(y_axis) == 1:
                fig = px.pie(df, names=x_axis, values=y_axis[0], title="Pie Chart")
            else:
                st.warning("For Pie Chart, please select only one Y-axis column.")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one Y-axis value.")

# 🤖 Column 2: AI Chat (Using PandasAI)
with col2:
    if df is not None:
        st.markdown("Chat with AI (Powered by PandasAI)")

        # ✅ Initialize session state for chat history if not exists
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        model = LocalLLM(
            api_base="http://localhost:11434/v1",
            model="llama3"
        )
        
        # Debugging: Print dataset information before initializing SmartDataframe
        #st.write("DataFrame Columns:", df.columns)  # Shows in Streamlit UI
        #st.write("First 5 Rows:", df.head())  # Shows first 5 rows in Streamlit UI

        #if 'Plant' in df.columns:
        #    st.write("Unique Values in 'Plant':", df['Plant'].unique())  # Check if 'BSK' exists


        # Convert DataFrame to SmartDataframe with debugging
        smart_df = SmartDataframe(df, {
            "enable_cache": False,
            "verbose": True,
            "use_error_correction": True
        }, config={"llm": model})

        # User query input
        prompt = st.text_area("What do you want to ask?")

        if st.button("Ask"):
            if prompt:
                with st.spinner("Generating response..."):
                    try:
                        response = smart_df.chat(prompt)
                        if response:
                            # ✅ Append question and response to chat history
                            st.session_state["chat_history"].append({"question": prompt, "response": response})

                            # ✅ Display the new chat message
                            with st.chat_message("user"):
                                st.markdown(prompt)
                            with st.chat_message("assistant"):
                                st.markdown(response)
                        else:
                            st.warning("No valid response received from the AI.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a question.")
       
        # Display chat history
        for chat in reversed(st.session_state["chat_history"]):
            with st.chat_message("user"):
                st.markdown(chat["question"])
            with st.chat_message("assistant"):
                st.markdown(chat["response"])
                
    else:
        st.info("Upload a file to start chatting with AI.")
