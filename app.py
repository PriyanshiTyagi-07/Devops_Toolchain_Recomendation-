import streamlit as st
import sqlite3
import hashlib
import os
from streamlit_lottie import st_lottie
import requests
import streamlit as st
from streamlit.components.v1 import html

from predict_model import make_prediction  # Ensure this function exists in the predict_model.py file

# Set page config
st.set_page_config(page_title="Complete Website", page_icon="🌐", layout="wide")

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie animations
tool_animation = load_lottieurl("https://lottie.host/88ddcb38-340c-4e52-867b-c55f49a36ed5/3hNUTG0Q7j.json")
success_animation = load_lottieurl("https://lottie.host/957e0d16-e6e5-4442-b7ee-538175ae688d/soWfl4ZyZJ.json")
lottie_login = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")
lottie_welcome = load_lottieurl("https://lottie.host/14719474-cfbd-4c78-ab6a-95f01b9ca7a2/JldEfNuFVe.json")

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        salt TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Hash password with salt
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

# Function to register user
def register_user(username, password):
    salt = os.urandom(16).hex()  # Generate a random salt
    hashed_password = hash_password(password, salt)
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', 
                       (username, hashed_password, salt))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to login user
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password, salt FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        stored_password, salt = user
        hashed_password = hash_password(password, salt)
        if hashed_password == stored_password:
            return True
    return False

# Function to handle logout
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.page = "Login"  # Set the page to Login after logout

# Initialize the DB
init_db()

# Session management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "Login"

# Function to handle login
def handle_login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.authenticated = True
            st.session_state.current_user = username
            st.session_state.page = "Home"
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    # Add a link to go to the registration page
    if st.button("Register"):
        st.session_state.page = "Register"

# Function to handle registration
def handle_registration():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password:
            if register_user(username, password):
                st.success("Registration successful! Please login.")
                st.session_state.page = "Login"
            else:
                st.error("Username already exists.")
                

        else:
            st.error("Passwords do not match.")
            
    # Add a Login button to go back to the Login page
    if st.button("Back to Login"):
        st.session_state.page = "Login"  # Redirect to login page
        st.rerun()

# Sidebar navigation (only visible if authenticated)
def render_sidebar():
    if st.session_state.authenticated:
        st.sidebar.title("Navigation")
        # Add button for "DevOps Tools"
        home_button = st.sidebar.button("Home")
        about_button = st.sidebar.button("About")
        devops_button = st.sidebar.button("DevOps Tool Recommendation")
        devops_tools_button = st.sidebar.button("DevOps Tools")  # New button
        
        logout_button = st.sidebar.button("Logout")
        
        return home_button, about_button, logout_button, devops_button , devops_tools_button
    return None, None, None, None , None

# Only render the sidebar if the user is authenticated
home_button, about_button, logout_button, devops_button , devops_tools_button = render_sidebar()

if home_button:
    st.session_state.page = "Home"
elif about_button:
    st.session_state.page = "About"
elif logout_button:
    logout()  # Logout when the button is pressed
    st.success("You have been logged out.")
elif devops_button:
    st.session_state.page = "DevOps Tool Recommendation"
elif devops_tools_button:
    st.session_state.page = "DevOps Tools"  # Navigate to the new DevOps Tools page


# Login page
if st.session_state.page == "Login" and not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    st_lottie(lottie_login, height=300)
    handle_login()

# Registration page
elif st.session_state.page == "Register":
    st.markdown("<h2 style='text-align: center;'>Register</h2>", unsafe_allow_html=True)
    handle_registration()

# Home page
elif st.session_state.page == "Home" and st.session_state.authenticated:
    st.markdown(f"<h2 style='text-align: center; font-size: 32px; font-weight: bold; color: #2a3d66;'>Welcome, {st.session_state.current_user}! 👋</h2>", unsafe_allow_html=True)
    st_lottie(lottie_welcome, height=250, speed=0.8)
    st.markdown(
        """
        <p style="text-align: center; font-size: 18px; color: #555;">
        This is your personalized dashboard. Explore the features of the website using the navigation menu on the left.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Profile section with user data
    st.markdown(
        """
        <div style="background-color: #f9f9f9; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: 30px; max-width: 800px; margin-left: auto; margin-right: auto;">
        <h3 style="text-align: center; color: #2a3d66; font-size: 28px; font-weight: 600;">Your Profile</h3>
        <p style="text-align: center; font-size: 16px; color: #777; margin-top: 10px;">
        Welcome to your profile page. Here, you can manage your account, view your activity, and customize your settings.
        </p>
        <div style="margin-top: 30px; text-align: center;">
            <p style="font-size: 18px; color: #333; font-weight: 500;">
            You are now connected to the platform and can explore all the personalized features and tools available. Feel free to navigate through the options in the sidebar.
            </p>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# About page
elif st.session_state.page == "About" and st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>About This Website</h2>", unsafe_allow_html=True)
    st_lottie(tool_animation, height=200, key="about_animation")  # Show animation for about page
    st.markdown(
        """
        <p style="text-align: center; font-size: 18px;">
        This is a demonstration of a complete **Streamlit-based website**. 
        It includes user authentication, navigation, and interactive features.
        </p>
        """,
        unsafe_allow_html=True,
    )

# DevOps Tools Page with 3 Cards per Row and Expandable Feature
elif st.session_state.page == "DevOps Tools" and st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #2a3d66; font-size: 36px; font-weight: bold;'>Explore Top DevOps Tools</h2>", unsafe_allow_html=True)
    st_lottie(tool_animation, height=150, key="devops_tools_animation")

    st.markdown("""
    <p style="text-align: center; font-size: 18px; color: #555;">
    Discover the best tools to streamline your DevOps processes. Click on a tool to learn more.
    </p>
    """, unsafe_allow_html=True)

    # Define the tools with links to their official documentation
    tools = [
        {"name": "Jenkins", "category": "CI/CD", "icon": "https://img.icons8.com/color/48/000000/jenkins.png", "description": "An open-source automation server that facilitates CI/CD pipelines.", "doc_link": "https://www.jenkins.io/doc/"},
        {"name": "CircleCI", "category": "CI/CD", "icon": "https://img.icons8.com/color/48/000000/circleci.png", "description": "Automates the software development process with CI/CD and workflows.", "doc_link": "https://circleci.com/docs/"},
        {"name": "Travis CI", "category": "CI/CD", "icon": "https://img.icons8.com/color/48/000000/travis-ci.png", "description": "A continuous integration service to build and test code.", "doc_link": "https://docs.travis-ci.com/"},
        
        {"name": "GitHub", "category": "Version Control", "icon": "https://img.icons8.com/ios-filled/50/000000/github.png", "description": "A platform for version control and collaboration using Git.", "doc_link": "https://docs.github.com/en/github"},
        {"name": "GitLab", "category": "Version Control", "icon": "https://img.icons8.com/color/48/000000/gitlab.png", "description": "A web-based Git repository manager with CI/CD functionality.", "doc_link": "https://docs.gitlab.com/ee/"},
        {"name": "Bitbucket", "category": "Version Control", "icon": "https://img.icons8.com/color/48/000000/bitbucket.png", "description": "A Git repository management solution for professional teams.", "doc_link": "https://support.atlassian.com/bitbucket-cloud/"},
        
        {"name": "Docker", "category": "Containerization", "icon": "https://img.icons8.com/color/48/000000/docker.png", "description": "A platform for developing, shipping, and running applications in containers.", "doc_link": "https://docs.docker.com/"},
        
        {"name": "Prometheus", "category": "Monitoring", "icon": "https://static-00.iconduck.com/assets.00/prometheus-icon-511x512-1vmxbcxr.png", "description": "An open-source monitoring and alerting toolkit designed for reliability.", "doc_link": "https://prometheus.io/docs/"},
        {"name": "Grafana", "category": "Monitoring", "icon": "https://img.icons8.com/color/48/000000/grafana.png", "description": "An open-source platform for monitoring and observability.", "doc_link": "https://grafana.com/docs/"},
        {"name": "ELK Stack", "category": "Monitoring", "icon": "https://banner2.cleanpng.com/20180928/eaq/kisspng-elasticsearch-kibana-logstash-logfile-apache-lucen-organiza-tus-logs-plesk-con-logstash-kibana-y-ela-1713928819514.webp", "description": "A set of three open-source tools for searching, analyzing, and visualizing log data.", "doc_link": "https://www.elastic.co/guide/index.html"},
        
        {"name": "Kubernetes", "category": "Orchestration", "icon": "https://img.icons8.com/ios-filled/50/000000/kubernetes.png", "description": "An open-source system for automating deployment, scaling, and management of containerized applications.", "doc_link": "https://kubernetes.io/docs/"},
        {"name": "Docker Swarm", "category": "Orchestration", "icon": "https://img.icons8.com/ios-filled/50/000000/docker.png", "description": "A native clustering and orchestration solution for Docker containers.", "doc_link": "https://docs.docker.com/engine/swarm/"},
        
        {"name": "HashiCorp Vault", "category": "Security", "icon": "https://cdn.worldvectorlogo.com/logos/vault-enterprise.svg", "description": "A tool for secrets management and data protection.", "doc_link": "https://www.vaultproject.io/docs"},
        {"name": "SonarQube", "category": "Security", "icon": "https://cdn.worldvectorlogo.com/logos/sonarqube-1.svg", "description": "A platform for continuous inspection of code quality to perform automatic reviews.", "doc_link": "https://docs.sonarqube.org/"},
        {"name": "OWASP ZAP", "category": "Security", "icon": "https://logos.bugcrowdusercontent.com/logos/2376/fdfa/651b17be/051e0245d787d1f71246d515e88a8564_zap256x256-oversize.png", "description": "An open-source web application security scanner.", "doc_link": "https://www.zaproxy.org/docs/"},
        
        {"name": "Terraform", "category": "IaC", "icon": "https://img.icons8.com/color/48/000000/terraform.png", "description": "An open-source IaC tool for building, changing, and versioning infrastructure safely.", "doc_link": "https://www.terraform.io/docs"},
        {"name": "Ansible", "category": "IaC", "icon": "https://static-00.iconduck.com/assets.00/ansible-icon-2048x2048-mc4z634w.png", "description": "An open-source automation tool for configuration management and application deployment.", "doc_link": "https://docs.ansible.com/ansible/latest/index.html"},
        
        {"name": "JFrog Artifactory", "category": "Artifact Management", "icon": "https://img.stackshare.io/service/4711/jfrog-artifactory-logo.png", "description": "A universal artifact repository manager for managing software packages.", "doc_link": "https://www.jfrog.com/confluence/display/JFROG/Documentation"},
        {"name": "Nexus Repository", "category": "Artifact Management", "icon": "https://miro.medium.com/v2/resize:fit:256/1*2b4k1_SmKkNRgqZV-NMFQg.png", "description": "A repository manager for storing and managing artifacts.", "doc_link": "https://help.sonatype.com/"},
    ]

    # Creating 3 columns per row for the cards
    num_columns = 3
    for i in range(0, len(tools), num_columns):
        cols = st.columns(num_columns)
        for j, tool in enumerate(tools[i:i+num_columns]):
            with cols[j]:
                # Card with icon and name always visible
                st.markdown(f"""
                <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; text-align: center; cursor: pointer;">
                    <img src="{tool['icon']}" alt="{tool['name']} Icon" style="height: 60px; width: 60px; margin-bottom: 10px;" />
                    <h4 style="color: #2a3d66; font-size: 20px; font-weight: bold; margin-bottom: 10px;">{tool['name']}</h4>
                    <p style="color: #777; font-size: 14px; margin-bottom: 10px;">{tool['category']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Expanding content with description and documentation link
                with st.expander("Learn More"):
                    st.markdown(f"""
                    <div style="font-size: 14px; color: #555; margin-top: 10px;">
                        <p><strong>Description:</strong> {tool['description']}</p>
                        <a href="{tool['doc_link']}" target="_blank" style="color: #1E90FF; text-decoration: none; font-weight: bold;">Official Documentation</a>
                    </div>
                    """, unsafe_allow_html=True)

# DevOps Tool Recommendation page
elif st.session_state.page == "DevOps Tool Recommendation" and st.session_state.authenticated:
    st_lottie(tool_animation, height=200, key="header_animation")
    st.markdown(
        """
        <h1 class="header-title">DevOps Tool Recommendation System</h1>
        <p class="sub-header">Find the perfect DevOps tool for your project with ease!</p>
        """,
        unsafe_allow_html=True
    )

    # Input section for DevOps Tool Recommendation
    st.markdown("### Provide Project Details")
    col1, col2, col3 = st.columns(3)

    with col1:
        team_size = st.selectbox('Team Size', ['Small', 'Medium', 'Large'], help="Select small if team size upto 10 ,medium if team size upto 50 ,large if team size above 50")
        compliance = st.selectbox('Compliance', ['Low', 'Medium', 'High'], help="Select the compliance level required.")

    with col2:
        release_frequency = st.selectbox('Release Frequency', ['Daily', 'Weekly', 'Monthly'], help="Select the frequency of releases.")
        scalability = st.selectbox('Scalability', ['Auto-scaling', 'Manual', 'None'], help="Select the scalability requirements.")

    with col3:
        project_size = st.selectbox(
        'Project Size',
        ['Small', 'Medium', 'Large'],
        help=(
            "### Division of Project Size\n"
            "- **Small Projects (Organic):**\n"
            "  - **Team:** Small (2–5 members)\n"
            "  - **Duration:** 1–3 months\n"
            "  - **Estimated LOC:** 2,000–20,000\n"
            "  - **Complexity:** Simple requirements with little interdependency.\n\n"
            "- **Medium Projects (Semi-Detached):**\n"
            "  - **Team:** Medium (5–20 members)\n"
            "  - **Duration:** 3–6 months\n"
            "  - **Estimated LOC:** 20,000–100,000\n"
            "  - **Complexity:** Moderate requirements, partial interdependencies.\n\n"
            "- **Large Projects (Embedded):**\n"
            "  - **Team:** Large (>20 members)\n"
            "  - **Duration:** >6 months\n"
            "  - **Estimated LOC:** >100,000\n"
            "  - **Complexity:** Complex requirements, high interdependencies, strict constraints."
        )
    )
        project_length = st.selectbox('Project Length', ['Short', 'Medium', 'Long'], help="If project duration is 1-2 months select short , if duration is 3-6 months select medium , else select long")
        security_level = st.selectbox('Security Level', ['Strict', 'Moderate', 'None'], help="Select the required security level.")

    # Button for prediction
    st.markdown("### Predict the Best DevOps Tool")
    if st.button('🔍 Predict DevOps Tool'):
        # Prepare input data for prediction
        input_data = {
            'Team Size': team_size,
            'Release Frequency': release_frequency,
            'Compliance': compliance,
            'Scalability': scalability,
            'Project Size': project_size,
            'Project Length': project_length,
            'Security Level': security_level
        }
        
        # Make prediction
        predicted_tool = make_prediction(input_data)
        
        # Display the result
        st.success(f"🎯 The recommended DevOps tool for your project is: **{predicted_tool}**")
        st_lottie(success_animation, height=200, key="success_animation")


# Footer with animation and styling
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 14px;'>Developed with ❤️</p>", 
    unsafe_allow_html=True
)