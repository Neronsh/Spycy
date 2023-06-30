from colorama import init
from googlesearch import search
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from random import randint
from requests.exceptions import HTTPError
from selenium.webdriver.support.wait import WebDriverWait
from termcolor import cprint
from pyfiglet import figlet_format
from selenium.webdriver.support import expected_conditions as EC

import sys
import time
import webbrowser

import plotly.graph_objects as go
import networkx as nx

init(strip=not sys.stdout.isatty())

cprint(figlet_format('SPYCY', font='starwars'),
       'yellow', 'on_red', attrs=['bold'])

print("Please make sure to switch your LinkedIn Profile to English mode.\n")

print("Please ensure writing the right name / surname to avoid any errors")
name = input("Please enter target name: ")
surname = input("Enter surname: ")
company = input("Enter company name if known (refine the search): ")
city = input("Enter the city if known (pages blanches only): ")


def open_google_maps(address):
    address = address.replace(' ', '+')
    url = f"https://www.google.com/maps/search/?api=1&query={address}"
    webbrowser.open(url)


# Loading animation function
def loading():
    animation = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]",
                 "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]\n"]

    for i in range(len(animation)):
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()


# Google search function that print webpages related (or not) to the person
def google_search(name, surname, company):
    query = name + " " + surname + " " + company

    loop = False

    web_pages = input(
        "Would you like to print the pages that are related to the target? Please respond with Yes or No \n")

    if web_pages.lower() == "yes":
        loop = True

    elif web_pages.lower() == "no":
        loop = False

    # Repeat function until failure or success
    max_retries = 5
    for retry in range(max_retries):
        try:
            for j in search(query, num_results=5):
                print(j)
                if loop == True:
                    webbrowser.open(j)
            break

        except HTTPError as e:
            # If error 429 appears, the programme will wait
            if e.response.status_code == 429:
                print(f"Error {e.response.status_code}: {e.response.reason}")
                print("Too many requests. Waiting...")
                time.sleep(randint(5, 10))
            else:
                # if another error occurs, print the error and stop the programme
                print(f"Error {e.response.status_code}: {e.response.reason}")
                break

        # if max tries, stop
        if retry == max_retries - 1:
            raise Exception(f"Could not retrieve results after {max_retries} retries")


# LinkedIn research about the person: Name, Job, Mail, Experience, Education, Contacts...
def linkedin_parsing(link):
    about = None

    try:

        ####################################################
        # LOGIN
        ####################################################

        driver = webdriver.Chrome()
        email = "ENTER YOUR LINKEDIN EMAIL HERE"
        password = "ENTER YOUR LINKEDIN PASSWORD HERE"

        driver.get("https://www.linkedin.com/login")

        email_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        email_field.send_keys(email)
        password_field.send_keys(password)

        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(
            20)  # If LinkedIn asks for Captcha, if yes, let it to 20 to have time to fill it manually. Lower it to 5 if there is no Captcha
        driver.get(link)
        time.sleep(3)

        ####################################################
        # NAME / SURNAME
        ####################################################
        try:
            full_name_element = driver.find_element("xpath",
                                                    "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/h1")
            full_name = full_name_element.text
            time.sleep(1)
        except Exception as e:
            print("Couldn't retrieve the full name of the person")

        ####################################################
        # JOB
        ####################################################
        try:

            job_element = driver.find_element("xpath",
                                              "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]")
            job = job_element.text
            time.sleep(1)
        except Exception as e:
            print("Couldn't retrieve the job of the person")

        ####################################################
        # CITY
        ####################################################
        try:
            workplace_element = driver.find_element("xpath",
                                                    "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]")
            workplace = workplace_element.text
            time.sleep(1)
        except Exception as e:
            print("Couldn't retrieve the workplace of the person")

        ####################################################
        # ABOUT
        ####################################################
        try:
            about = driver.find_element(By.ID, "about").find_element(By.XPATH, "..").find_element(By.CLASS_NAME,
                                                                                                  "display-flex").text
            time.sleep(1)
        except Exception as e:
            print("There is no written content in the 'About' section for this person.")
            about = None

        ####################################################
        # PERSONAL INFORMATION
        ####################################################

        time.sleep(3)
        button = driver.find_element(By.ID, "top-card-text-details-contact-info")
        button.click()
        time.sleep(3)
        # contact_info = link + "/overlay/contact-info/"
        # driver.get(contact_info)

        email_link = driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]")
        email = email_link.text

        driver.get(link)
        time.sleep(5)

        ####################################################
        # CONTACTS (FIRST PAGE ONLY)
        ####################################################

        contacts_link = driver.find_element(By.XPATH, "//a[contains(@href, 'search/results/people')]")

        contacts_link = contacts_link.get_attribute("href")

        driver.get(contacts_link)

        _ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")))

        connections = driver.find_element(By.CLASS_NAME, "scaffold-layout__main")
        contacts = []

        for conn in connections.find_elements(By.CLASS_NAME, "reusable-search__result-container"):
            try:
                name_lk = conn.find_element(By.CLASS_NAME, "entity-result__title-text")
                job_lk = conn.find_element(By.CLASS_NAME, "entity-result__primary-subtitle")
                url_lk = conn.find_element(By.CLASS_NAME, "app-aware-link")

                name_text = name_lk.text
                name_text = name_text.split("View")[0].strip()
                job_text = job_lk.text
                url_text = url_lk.get_attribute("href")

                contacts.append((name_text, job_text, url_text))

            except NoSuchElementException:
                print(
                    "Contacts could not be retrieved either because the target person has restricted the visibility of their contacts or they do not have any contacts available.")

        ####################################################
        # EDUCATION
        ####################################################

        education = []

        time.sleep(2)
        driver.get(link)

        education_info = link + "/details/education/"
        driver.get(education_info)
        time.sleep(3)

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        main_list = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "pvs-list")))
        education_list = main_list.find_elements(By.XPATH, "li")

        for edu in education_list:
            school_url = edu.find_element(By.XPATH,
                                          '(./descendant::a[contains(@class, "optional-action-target-wrapper")])[1]').get_attribute(
                'href')

            school_element = edu.find_element(By.XPATH,
                                              './/div[contains(@class, "display-flex") and contains(@class, "align-items-center") and contains(@class, "mr1") and contains(@class, "t-bold")]/span[1]')

            school_txt = school_element.text

            education.append((school_txt, school_url,))

        ####################################################
        # EXPERIENCE
        ####################################################

        experience = []

        time.sleep(2)
        driver.get(link)

        experience_info = link + "/details/experience/"
        driver.get(experience_info)
        time.sleep(3)

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        main_list = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "pvs-list")))
        experience_list = main_list.find_elements(By.XPATH, "li")

        for experience_element in experience_list:
            company_linkedin_url = experience_element.find_element(By.XPATH,
                                                                   '(./descendant::a[contains(@class, "optional-action-target-wrapper")])[1]').get_attribute(
                'href')
            job_title_element = experience_element.find_element(By.XPATH,
                                                                './/div[contains(@class, "display-flex") and contains(@class, "align-items-center") and contains(@class, "mr1") and contains(@class, "t-bold")]/span[1]')

            job_title = job_title_element.text

            experience.append((job_title, company_linkedin_url))

        if about is None:
            return full_name, job, workplace, experience, education, contacts, email, None
        else:
            return full_name, job, workplace, experience, education, contacts, email, about

    except Exception as error:
        print("An error occurred during LinkedIn parsing:", str(error))
        print("Profile couldn't be parsed... Please try again later.")
        exit(1)


# Search for the LinkedIn URL of the person with Google
def lk_search(name, surname, company):
    global first_link
    query = name + " " + surname + " " + company + " " + "linkedin"

    print("LinkedIn Profiles found:")

    # Repeat until failure or success
    max_retries = 5
    loading()
    for retry in range(max_retries):
        try:
            # Parcourt les résultats de recherche
            for index, result in enumerate(search(query, num_results=2), start=1):
                print(result)

                # The first link is being saved for future reference
                if index == 1:
                    first_link = result

            break

        except HTTPError as e:

            if e.response.status_code == 429:
                print(f"Error {e.response.status_code}: {e.response.reason}")
                print("Too many requests. Waiting...")
                time.sleep(randint(5, 10))
            else:

                print(f"Error {e.response.status_code}: {e.response.reason}")
                break

        # If max tries, print error and exit
        if retry == max_retries - 1:
            raise Exception(f"Could not retrieve results after {max_retries} retries")
    return first_link


# Perform a Pages Blanches search on the person, specifying the city for better accuracy.
def search_pages_blanches(name, surname, city=None):
    print(
        "\nResearching data on pages blanches...\nIf the city field is left blank or if the target does not exist on the website, it may provide inaccurate information.")
    if city is None:
        url = "https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui=" + name + "+" + surname + "&ou=&univers=pagesblanches&idOu="
    else:
        url = "https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui=" + name + "+" + surname + "&ou=" + city + "&univers=pagesblanches&idOu="

    loading()

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    driver.get(url)
    time.sleep(2)

    try:

        # Using XPATH to extract information from the first search result on the page for the person
        button = driver.find_element(By.ID, "didomi-notice-agree-button")
        button.click()
        name_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[1]/a/h3")
        address_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[1]/div/a")
        button = driver.find_element("xpath", "//button[contains(@data-pjstats, 'CONTACTER-PAR-TELEPHONE')]")
        button.click()
        phone_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[2]/div/div")

        # Remove unnecessary text from the strings, retaining only the relevant data
        pb_name = name_element.text
        address = address_element.text
        address = address.replace("Voir le plan", "")

        phone = phone_element.text
        phone = phone.replace("Opposé aux opérations de marketing", "").replace("Tél", "").replace(":", "")
        phone = phone.strip()
        phone = phone.replace("\n", "")

        print("Name :", pb_name)
        print("Address :", address)
        print("Phone :", phone)

        driver.quit()
        open_google_maps(address)

    # If the person is not in the annular, a message is printed
    except Exception as e:
        print("The individual you are searching for does not seem to be listed in the Pages Blanches directory")


# The person's contacts are visualized as a graph, with the person being the central node and the contacts represented as edges
def display_link_graph(central_node, endpoints):
    G = nx.Graph()
    G.add_node(central_node)

    for endpoint in endpoints:
        arg1, arg2, *_ = endpoint
        initials = ''.join(word[0] for word in arg1.split())
        G.add_edge(central_node, initials, label=f"{arg1}', '{arg2}")

    pos = nx.spring_layout(G, k=10)

    node_labels = {node: node if isinstance(node, str) else '' for node in G.nodes}

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color='gray'),
        hoverinfo='text',
        mode='lines'
    )

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition='top center',
        hoverinfo='text',
        mode='markers+text',
        marker=dict(
            color='red',
            size=20
        )
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

        if node == central_node:
            node_trace['text'] += ('',)  # Central node without tag
        else:
            node_text = node_labels[node]
            for edge in G.edges(node):
                label = G.edges[edge]['label']
                node_text += f"', {label}"
            node_trace['text'] += (node_text,)

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        title=''
                    ))

    fig.update_layout(
        annotations=[
            dict(
                x=x,
                y=y,
                text=text,
                showarrow=False,
                font=dict(size=8),
                xref="x",
                yref="y"
            ) for x, y, text in zip(node_trace['x'], node_trace['y'], node_trace['text'])
        ]
    )

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    fig.update_traces(textposition='top center', hovertext=node_trace['text'])

    fig.show()


###################################
# MAIN PART
# 1 - Begin by conducting a Google search on the person.
# 2 - Perform a Pages Blanches research to gather additional information.
# 3 - Search for the person's LinkedIn URL.
# 4 - Extract relevant data from the person's LinkedIn profile.
# 5 - Print available information about the person based on the retrieved data
# 6 - Print the person's contacts using a graph representation, where the person is the central node and the contacts are the edges.
###################################

google_search(name, surname, company)

search_pages_blanches(name, surname, city)

link = lk_search(name, surname, company)

full_name, job, workplace, experience, education, contacts, email, about = linkedin_parsing(link)

# Print information about the person (name, job, workplace, email, experience, studies, contacts...)
print("\nPerson information: \n")

print("Full name: ", full_name)
print("Job: ", job)
print("Workplace: ", workplace)
print("Email: ", email)

if about is None:
    print("The 'About' section has not been filled in.")
else:
    print("About: ", about)

print("\nProfessional Experience: \n")
for exp in experience:
    print(exp)

print("\nEducation: \n")
for edu in education:
    print(edu)

print("\nContacts:")
for contact in contacts:
    print(contact)

# Create a graph based on the person contacts
print("\nVisualizing the target's contacts using a graph...")

central_node = "Target"
display_link_graph(central_node, contacts)

print("Finished.")

input('Press ENTER to exit')
