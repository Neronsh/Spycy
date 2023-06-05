from colorama import init
from googlesearch import search
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from random import randint
from fake_useragent import UserAgent
from requests.exceptions import HTTPError
from selenium.webdriver.support.wait import WebDriverWait
from termcolor import cprint
from pyfiglet import figlet_format
from linkedin_scraper import Person, actions
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
    # print("Loading:")

    animation = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]",
                 "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]\n"]

    for i in range(len(animation)):
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()


# Google search function about the target
def google_search(name, surname, company):
    query = name + " " + surname + " " + company

    # Initialise l'objet User-Agent
    user_agent = UserAgent()

    # Répète la recherche jusqu'à ce qu'elle réussisse ou qu'elle échoue après un certain nombre d'essais
    max_retries = 5
    for retry in range(max_retries):
        try:
            # Utilise un User-Agent différent pour chaque requête
            headers = {"User-Agent": user_agent.random}
            for j in search(query, num_results=5):
                print(j)

            # Sort de la boucle car la recherche a réussi
            break

        except HTTPError as e:
            # Si l'erreur est une erreur 429 Too Many Requests, attendez un certain temps avant de réessayer
            if e.response.status_code == 429:
                print(f"Error {e.response.status_code}: {e.response.reason}")
                print("Too many requests. Waiting...")
                time.sleep(randint(5, 10))
            else:
                # Si une autre erreur est levée, interrompt la boucle et lève l'erreur
                print(f"Error {e.response.status_code}: {e.response.reason}")
                break

        # Si on a atteint le nombre maximum d'essais, lève une erreur
        if retry == max_retries - 1:
            raise Exception(f"Could not retrieve results after {max_retries} retries")


# Linkedin research about the target
def linkedin_parsing(link):
    try:

        driver = webdriver.Chrome()
        email = "YOUR LINKEDIN EMAIL ADDRESS"
        password = "YOUR LINKEDIN PASSWORD"

        actions.login(driver, email, password)
        driver.get(link)
        time.sleep(3)

        contact_info = link + "/overlay/contact-info/"

        driver.get(contact_info)
        time.sleep(3)
        email_link = driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]")
        email = email_link.text
        # print("email is", email)

        driver.get(link)
        time.sleep(5)

        contacts_link = driver.find_element(By.XPATH, "//a[contains(@href, 'search/results/people')]")

        contacts_link = contacts_link.get_attribute("href")

        driver.get(contacts_link)

        _ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")))

        connections = driver.find_element(By.CLASS_NAME, "scaffold-layout__main")
        contacts = []

        # while True:
        for conn in connections.find_elements(By.CLASS_NAME, "reusable-search__result-container"):
            try:
                name_lk = conn.find_element(By.CLASS_NAME, "entity-result__title-text")
                job_lk = conn.find_element(By.CLASS_NAME, "entity-result__primary-subtitle")
                url_lk = conn.find_element(By.CLASS_NAME, "app-aware-link")

                name_text = name_lk.text
                name_text = name_text.split("View")[0].strip()
                job_text = job_lk.text
                url_text = url_lk.get_attribute("href")

                """
                print("name_lk", name_text)
                print("job_lk", job_text)
                print("url_lk", url_text, "\n")
                """

                contacts.append((name_text, job_text, url_text))

            except NoSuchElementException:
                print(
                    "Contacts could not be retrieved either because the target person has restricted the visibility of their contacts or they do not have any contacts available.")

        """
                    next_button = driver.find_element(By.XPATH, "//button[contains(span, 'Next')]")

                    if "disabled" in next_button.get_attribute("class"):
                        # Si il n'y a plus de boutons, la boucle s'arrête
                        break
                    # Clique sur le bouton suivant pour charger les contacts supplémentaires
                    next_button.click()
                    time.sleep(10)

                    # Attend que les nouveaux contacts soient chargés
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__result-container")))
        """
        time.sleep(2)
        driver.get(link)

        person = Person(link, driver=driver)
        return person, contacts, email

    except Exception as error:
        print("An error occurred during LinkedIn parsing:", str(error))
        print("Profile couldn't be parsed... Please try again later.")
        exit(1)


# Search for the linkedin target URL on Google
def lk_search(name, surname, company):
    global first_link
    query = name + " " + surname + " " + company + " " + "linkedin"

    print("LinkedIn Profiles found:")

    # Répète la recherche jusqu'à ce qu'elle réussisse ou qu'elle échoue après un certain nombre d'essais
    max_retries = 5
    loading()
    for retry in range(max_retries):
        try:
            # Parcourt les résultats de recherche
            for index, result in enumerate(search(query, num_results=2), start=1):
                print(result)

                # Stocke le premier lien dans la variable 'first_link'
                if index == 1:
                    first_link = result

            # Sort de la boucle car la recherche a réussi
            break

        except HTTPError as e:
            # Si l'erreur est une erreur 429 Too Many Requests, attendez un certain temps avant de réessayer
            if e.response.status_code == 429:
                print(f"Error {e.response.status_code}: {e.response.reason}")
                print("Too many requests. Waiting...")
                time.sleep(randint(5, 10))
            else:
                # Si une autre erreur est levée, interrompt la boucle et lève l'erreur
                print(f"Error {e.response.status_code}: {e.response.reason}")
                break

        # Si on a atteint le nombre maximum d'essais, lève une erreur
        if retry == max_retries - 1:
            raise Exception(f"Could not retrieve results after {max_retries} retries")
    return first_link


# Pages Blanches research about the target
def search_pages_blanches(name, surname, city=None):
    # URL de la recherche sur Pages Blanches
    print(
        "\nResearching data on pages blanches...\nIf the city field is left blank or if the target does not exist on the website, it may provide inaccurate information.")
    if city is None:
        url = "https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui=" + name + "+" + surname + "&ou=&univers=pagesblanches&idOu="
    else:
        url = "https://www.pagesjaunes.fr/pagesblanches/recherche?quoiqui=" + name + "+" + surname + "&ou=" + city + "&univers=pagesblanches&idOu="

    loading()
    # Créer une instance du navigateur Chrome
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    # Naviguer vers la page web
    driver.get(url)
    time.sleep(2)

    # Utiliser les XPath pour extraire les informations
    button = driver.find_element(By.ID, "didomi-notice-agree-button")
    button.click()
    nom_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[1]/a/h3")
    address_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[1]/div/a")
    button = driver.find_element("xpath", "//button[contains(@data-pjstats, 'CONTACTER-PAR-TELEPHONE')]")
    button.click()
    phone_element = driver.find_element("xpath", "/html/body/main/div[2]/div/section/div/ul/li[1]/div[2]/div/div")

    # Obtenir le texte des éléments trouvés
    nom = nom_element.text
    address = address_element.text
    address = address.replace("Voir le plan", "")

    phone = phone_element.text
    phone = phone.replace("Opposé aux opérations de marketing", "").replace("Tél", "").replace(":", "")
    phone = phone.strip()
    phone = phone.replace("\n", "")

    # Afficher les informations
    print("Name :", nom)
    print("Address :", address)
    print("Phone :", phone)

    # Fermer le navigateur
    driver.quit()
    open_google_maps(address)


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
            node_trace['text'] += ('',)  # Nœud central sans étiquette
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


google_search(name, surname, company)

search_pages_blanches(name, surname, city)

link = lk_search(name, surname, company)

person, contacts, email = linkedin_parsing(link)

# Afficher le nom complet de la personne
print("Full name / connection degree: ", person.name)
print("Email: ", email)

url_var = person.also_viewed_urls
if not url_var:
    print("No viewved URLS.")
else:
    print("URLS viewved:")
    for url_elem in url_var:
        print(url_elem)

if person.about is None:
    print("The person has not provided any information in the 'About' section.\n")
else:
    print("About: ", person.about)

if person.interests:
    print("Interest: ", person.interests)
else:
    print("The person has not provided any information in the 'Interest' section.\n")

if person.accomplishments:
    print("Interest: ", person.accomplishments)
else:
    print("The person has not provided any information in the 'Accomplishments' section.\n")

# Afficher les expériences professionnelles de la personne
print("Professional Experiences :")
for experience in person.experiences:
    print("Job :", experience.position_title)
    print("Location :", experience.location)
    print("Company :", experience.institution_name)
    print("Company link:", experience.linkedin_url)
    print("Duration :", experience.from_date + " to " + experience.to_date + " overall : " + experience.duration)
    print("Description :", experience.description)
    print()

# Afficher les études de la personne
print("Studies :")
for education in person.educations:
    print("Degree :", education.degree)
    print("Establishment :", education.institution_name)
    if education.from_date is None and education.to_date is None:
        print()
    else:
        print("Duration :", education.from_date + " to " + education.to_date)
        print()

print("Contacts:")
for contact in contacts:
    print(contact)

print("\n Visualizing the target's contacts using a graph...")

central_node = "Target"
display_link_graph(central_node, contacts)

print("Finished.")
