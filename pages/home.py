import streamlit as st

def render_home():
    st.title("🌿 Biodiversity Insights")
    st.subheader("Home")

    st.write(
        """
        This is the **home page** of the Biodiversity Insights dashboard.

        If you can see this text:
        - Streamlit is running correctly  
        - The navigation menu is working  
        - Page routing is set up properly  

        You can now start building out the dashboard page by page. 
        """
    )

