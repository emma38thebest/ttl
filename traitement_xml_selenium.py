from ctypes import c_bool
import xml.etree.ElementTree as ET
import json as js
import json
from lxml import etree
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import unicodedata

# T�l�charger les ressources n�cessaires de NLTK
nltk.download('punkt')
nltk.download('wordnet')

# Charger le fichier XML
tree = ET.parse('/content/bonfichierr.xml')
root = tree.getroot()

xmltree = etree.parse('/content/bonfichierr.xml')

# R�cup�rer tous les �l�ments <h2>
h2_elements = xmltree.xpath('//h2')

auteurs  = {
  "A. B.": "Bouder Amel",
  "A. G.": "G�nety Ali�nor",
  "A. O.": "Oubraham Adel",
  "B. R.": "R�my Bernard",
  "Chr. H.": "Hamdoune Christine",
  "D. M.": "Mehentel Djahida",
  "Fr. T.": "Tecca Francesco",
  "Fr. W.": "Wibl� Fran�ois",
  "I. S.": "Sfaxi Intissar",
  "L. P.": "Prada Luigi",
  "M. C.-T.": "Coltelloni-Trannoy Mich�le",
  "N. T.": "Tran Nicolas",
  "Ph. L.": "Leveau Philippe",
  "S. D.": "Drici Salim",
  "T. A.": "Amraoui Touatia"
}

support_elements = [
    "autel", "base", "bloc", "borne", "borne militaire", "caisson", "chapiteau", "corniche",
    "colonne", "coupe", "cupule", "dalle", "entablement", "ind�termin�", "mosa�que",
    "pi�destal", "plaque", "sarcophage", "sculpture", "st�le", "urne", "tuile"
]

categories = [
    "chr�tienne", "dipl�me militaire", "support", "�dilitaire", "fun�raire",
    "biblio", "honorifique", "ind�termin�", "instrumentum", "religieuse", "routi�re", "inconnu"
]


materiaux = [
    "alb�tre", "bois", "calcaire", "granit", "gr�s",
    "ind�termin�", "marbre", "m�tal", "schiste", "terre cuite", "ind�termin�", "inconnu"
]



lieu_decouverte = ["Archambault","Hanafi","ind�termin�","oued el Kantara","oued Nsara","oued Rassoul","Porte de Tipasa","Porte secondaire sud", "Porte sud","Roseau ou Cadat"
]

lieu_conservation = [
    "inconnu",
    "Jardin du commandant de l'�cole militaire",
    "mairie hall",
    "Mus�e de Cherchell",
    "Mus�e de Nice-Cimiez",
    "Mus�e de Tipasa",
    "Mus�e des Antiquit�s",
    "Mus�e du Louvre",
    "Mus�e municipal",
    "Mus�e public national",
    "Parc Bocquet",
    "Parc Bocquet Villa",
    "Parc des mosa�ques",
    "Service des Antiquit�s"
]

inconnu = ["inconnu", "ind�termin�", "ind�termin�e", "inconnue", "inconnus", "ind�termin�s", "inconnues", "ind�termin�es","incertain", "incertaine"]


ville_conservation_dict = {"Alger":["Alger", "mus�e des antiquit�s"],
                      "Cherchell" :[ "Mus�e de Cherchell", "Parc Boquet", "Parc Bocquet Villa", "Parc des mosa�ques"],
                      "inconnue": ["inconnu", "ind�termin�", "ind�termin�e", "inconnue", "inconnus", "ind�termin�s", "inconnues", "ind�termin�es","incertain", "incertaine"],
                      "Marseille":["Marseille"],
                      "Nice-Cimiez":["Nice-Cimiez"],
                      "Paris":["Mus�e du Louvre"],
                      "Sidi Ghiles":["Sidi Ghiles"],
                      "Tipasa":["Mus�e de Tipasa","Tipasa","Tipaza"]
                      }

secteur_decouverte_dict = {
    "N�cropole de l'ouest": ["n�cropole de l'ouest", "n�cropole occidentale", "oued el Kantara", "el kantara"],
    "N�cropole de l'est": ["n�cropole de l'est", "n�cropole orientale", "Nsara" ,"N'sara"],
    "n�cropole du sud": ["n�cropole du sud territoire", "n�cropole m�ridionale", "n�cropole du sud"],
    "Ville entre l'enceinte fran�aise et l'enceinte romaine": ["ville entre l'enceinte fran�aise et l'enceinte romaine"],
    "Ville int�rieur de l'enceinte fran�aise": ["ville int�rieur de l'enceinte fran�aise"],
    "ind�termin�": ["inconnu", "incertain", "incertaine", "ind�termin�", "ind�termin�e", "inconnue", "inconnus", "ind�termin�s", "inconnues", "ind�termin�es"]
}

decouverte = ["d�couvert", "d�couverte", "trouv�", "trouve", "trouv�e"]

conservation = ["conservation", "conserv�e", "conserv�", "conserv�s"]

correspondances_json = {}


def normalize_text(text):
    # Remplacer toutes les formes d'apostrophes par une apostrophe simple
    text = text.replace("?", "'").replace("`", "'")
    text = text.replace (".", " ")
    return text

def uni_text(text) :
    return unicodedata.normalize('NFKC', text)

    # Remplacer les articles contract�s comme "l'", "d'", "s'" par un espace
    text = re.sub(r"\bl'|\bd'|\bs'", " ", text)

    # Supprimer les espaces multiples cr��s par la substitution et normaliser le tout en minuscules
    text = re.sub(r'\s+', ' ', text)  # Remplacer les espaces multiples par un seul espace
    return text.strip().lower()  # Enlever les espaces en d�but/fin et normaliser en minuscules

def chercher_apres_mots(texte, liste_mots):
    for mot in liste_mots:
        position = texte.find(mot)
        if position != -1:  # Si un mot est trouv�
            return texte[position + len(mot):]  # Retourne le texte apr�s ce mot
    return None  # Si aucun mot de la liste n'est trouv�
def chercher_avant_mots(texte, liste_mots):
    for mot in liste_mots:
        position = texte.find(mot)
        if position != -1:  # Si un mot est trouv�
            return texte[:position]  # Retourne le texte avant ce mot
    return None  # Si aucun mot de la liste n'est trouv�

def chercher_avant_et_apres(texte, liste_mots_avant, liste_mots_apres):

    texte_apres = chercher_apres_mots(texte, liste_mots_apres)
    if texte_apres is None:
        return None
    else :
      texte_avant = chercher_avant_mots(texte_apres, liste_mots_avant)

    if texte_avant is not None and texte_apres is not None:
        return texte_avant.strip()
    elif texte_apres is not None:

        print(f"Texte apr�s le mot trouv�: {texte_apres.strip()}")
        return  texte_apres.strip()

    else:
        print("Aucun mot trouv� avant ou apr�s.")



def trouver_dates_flexibles(texte):
    # Liste des mois en fran�ais avec un groupe non capturant
    mois = r"(?:janvier|f�vrier|mars|avril|mai|juin|juillet|ao�t|septembre|octobre|novembre|d�cembre|ann�es)"

    # Expression r�guli�re pour capturer plusieurs formats de dates avec des groupes non capturants
    pattern = rf"\b(?:\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{2,4}}|\d{{1,2}}\s{mois}\s\d{{4}}|{mois}\s\d{{4}}|\d{{4}})\b"

    # Pattern pour d�tecter les intervalles (ex: entre 1980 et 1990)
    between_pattern = r"entre (\d{4}) et (\d{4})"

    # Trouver toutes les correspondances dans le texte
    dates = re.findall(pattern, texte)

    # Si un intervalle "entre ... et ..." est trouv�, l'ajouter aux dates
    interval_match = re.search(between_pattern, texte)
    if interval_match:
        # Extraire l'intervalle complet
        interval_text = interval_match.group(0)
        # Ajouter l'intervalle et retirer les ann�es individuelles associ�es
        dates = [date for date in dates if date not in interval_match.groups()]
        dates.append(interval_text)  # Ajouter l'intervalle complet

    return dates

def extract_date_with_words_before(keywords, text, max_words_after=20):
    dates = trouver_dates_flexibles(text)
    words = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    for i, word in enumerate(words):
        if lemmatizer.lemmatize(word) in keywords:
            # Trouver l'index du mot-cl�
            keyword_index = i
            # Chercher la date la plus proche apr�s le mot-cl� dans les 20 mots suivants
            for j in range(keyword_index + 1, min(keyword_index + max_words_after + 1, len(words))):
                # Chercher des intervalles de dates
                for date in dates:
                    if date in ' '.join(words[keyword_index:j + 1]):
                        return date
    return None

def recherche_date_icone(text):
    # Initialisation des sections
    analyse_text = None
    datation_text = None
    iconographie_text = None
    datation = None
    iconographie = None
    datation_index = None
    iconographie_index = None
    datation_match = None
    iconographie_match = None


    # Nettoyage du texte
    text = text.strip()
    text = uni_text(text)

    # Recherche des indices des sections avec regex
    datation_match = re.search(r"Datation\s*?:", text)
    iconographie_match = re.search(r"Iconographie\s+de\s+la\s+niche\s*?:", text)
    analyse_text, iconographie_text, datation_text = "", "", ""  # Initialisation des variables

    if datation_match:
        datation_index = datation_match.start()
        analyse_text = text[:datation_index].strip()  # Texte avant "Datation" va dans analyse
        rest = text[datation_index:].strip()

        # V�rifie si "Iconographie de la niche" appara�t apr�s "Datation"
        if iconographie_match and iconographie_match.start() > datation_index:
            iconographie_index = iconographie_match.start()
            datation_text = rest[:iconographie_index - datation_index].replace("Datation :", "").strip()
            iconographie_text = text[iconographie_index:].replace("Iconographie de la niche :", "").strip()

        elif iconographie_match:
            # Si "Iconographie de la niche" appara�t avant "Datation"
            iconographie_index = iconographie_match.start()
            analyse_text = text[:iconographie_index].strip()
            iconographie_text = text[iconographie_index:datation_index].replace("Iconographie de la niche :", "").strip()
            datation_text = rest.replace("Datation :", "").strip()

        else:
            # Si "Iconographie de la niche" n'est pas trouv�, tout le reste est dans "datation"
            datation_text = rest.replace("Datation :", "").strip()

    elif iconographie_match:
        # Si seulement "Iconographie de la niche" est trouv�
        iconographie_index = iconographie_match.start()
        analyse_text = text[:iconographie_index].strip()  # Texte avant "Iconographie" va dans analyse
        iconographie_text = text[iconographie_index:].replace("Iconographie de la niche :", "").strip()

    else:
        # Si aucun mot-cl� n'est trouv�, tout va dans "analyse"
        analyse_text = text.strip()

    return analyse_text, iconographie_text, datation_text


def extraire_titre(titre):
    match = re.search(r'^\d+\.\s*(.*)', titre)  # Capture tout apr�s le chiffre et le point
    if match:
        return match.group(1).strip()  # Renvoie le texte sans espaces superflus
    return titre  # Retourne le titre original si aucune correspondance

def extraire_dimensions(texte, categorie, dimensions):
  dimensions.clear()
  patterns = [
        r'[hH]\.?\s*:\s*(\d+(?:,\s*\d+)?)\s*cm',  # Pattern for height
        r'[hH]\dl\.?\s*:\s*(\d+(?:,\s*\d+)?)\s*cm',  # Pattern for heightdl : changed \l to [lL] to match lowercase or uppercase 'l'
        r'[lL]\.?\s*:\s*(\d+(?:,\s*\d+)?)\s*cm',  # Pattern for width
        r'(?:�p\.|pr\.)\s*:\s*(\d+(?:,\s*\d+)?)\s*cm'  # Pattern for depth/profundity
    ]

  # List to store the results
  if categorie == "dimensions":
    # Regex pour extraire les dimensions
    if "dimensions" or "Dimensions" in texte: # Changed to if "dimensions" in texte.lower() or "Dimensions" in texte.lower(): to account for case sensitivity
       # Replace non-breaking spaces with regular spaces
        texte = texte.replace('\u202F', ' ')
        # Search for each dimension in the text
        for pattern in patterns:
            match = re.search(pattern, texte)
            if match:
                dimensions.append(match.group(1))
            else:
                dimensions.append(None)  # Append None if the dimension is not found
  elif categorie == "epi" :
    if re.search(r'([dD]imensions?\s+[��]pigraphiques?|[cC]hamp\s+[��]pigraphique?s?)', texte): # Added ,texte to re.search function call
      # Replace non-breaking spaces with regular spaces
      texte = texte.replace('\u202F', ' ')
      # Search for each dimension in the text
      for pattern in patterns:
          match = re.search(pattern, texte)
          if match:
              dimensions.append(match.group(1))
          else:
              dimensions.append(None)  # Append None if the dimension is not found


  # Return dimensions only if they were found, else return None
  if any(dimensions):
    return dimensions
  else:
    return None



# R�cup�rer tous les �l�ments <h2> du fichier XML
h2_elements = xmltree.xpath('//h2')

# Initialiser le compteur pour les inscriptions
count_inscr = 0

data = {}

# Boucler sur chaque <h2>
for h2 in h2_elements:
    # R�cup�rer l'ID de l'�l�ment <h2>, ou utiliser un identifiant unique si aucun ID n'est d�fini
    h2_id = h2.get('id', f"h2_{h2_elements.index(h2)}").zfill(3)  # Utilise l'index comme fallback pour l'ID
    paleo_texts = []
    apparat_texts = ""
    # V�rifier s'il y a des �l�ments <Inscription_avec_alin�a_5_pt> dans le <h2>
    if len(h2.xpath('.//Inscription_traduction_italique')) > 0:
      trad = h2.xpath('.//Inscription_traduction_italique')[0]
      preceding_trad = trad.xpath("preceding-sibling::*[not(self::Inscription_avec_alin�a_5_pt)][1]")
      if preceding_trad : 
        apparat_texts = preceding_trad[0].text 
        


    if len(h2.xpath('.//Inscription_avec_alin�a_5_pt')) > 0:
        # Prendre le premier <Inscription_avec_alin�a_5_pt>
        el = h2.xpath('.//Inscription_avec_alin�a_5_pt')[0]
        print(f"Dans <h2> {h2_id} : Premi�re inscription trouv�e : {el.text}")
        count_inscr += 1

    # V�rifier s'il y a une deuxi�me inscription
    if len(h2.xpath('.//Inscription_avec_alin�a_5_pt')) > 1 and count_inscr:
        el = h2.xpath('.//Inscription_avec_alin�a_5_pt')[1]  # Deuxi�me �l�ment Inscription_avec_alin�a_5_pt
        print(f"Dans <h2> {h2_id} : Deuxi�me inscription trouv�e : {el.text}")
        
        # R�cup�rer plusieurs balises <Apparat_critique> pr�c�dentes
        preceding_elements = el.xpath("preceding-sibling::Apparat_critique")

        # Afficher et concat�ner les textes des balises <Apparat_critique> pr�c�dentes
        if preceding_elements:
            # Concat�ner tous les textes des balises <Apparat_critique> pr�c�dentes (sauf les deux premi�res)
            for prev in preceding_elements[2:]:
                print(f"Balise pr�c�dente <Apparat_critique> : {prev.tag} avec texte : {prev.text}")
                paleo_texts.extend(prev.text)  # Ajouter le texte � la liste

        else:
            print(f"Aucune balise <Apparat_critique> pr�c�dente dans <h2> {h2_id}.")
        
        count_inscr += 1

    # V�rifier s'il y a des balises <Apparat_critique_tabulations_9pt> et une inscription avant
    elif len(h2.xpath('.//Apparat_critique_tabulations_9pt')) > 0 and count_inscr:
        el = h2.xpath('.//Apparat_critique_tabulations_9pt')[0]
        print(f"Dans <h2> {h2_id} : Premi�re <Apparat_critique_tabulations_9pt> trouv�e : {el.text}")
        
        # R�cup�rer plusieurs balises <Apparat_critique> pr�c�dentes
        preceding_elements = el.xpath("preceding-sibling::Apparat_critique")
        
        # Concat�ner tous les textes des balises <Apparat_critique> pr�c�dentes (sauf les deux premi�res)
        if preceding_elements:
            for prev in preceding_elements[2:]:
                print(f"Balise pr�c�dente <Apparat_critique> : {prev.tag} avec texte : {prev.text}")
                paleo_texts.extend(prev.text)  # Ajouter le texte � la liste
        else:
            print(f"Aucune balise <Apparat_critique> pr�c�dente dans <h2> {h2_id}.")
     
        count_inscr += 1
    # Afficher une ligne de s�paration pour chaque <h2>
    print("\n--- Fin du h2 ---\n")
    if  h2_id not in data:
            data[h2_id] = {}  # Initialiser le dictionnaire pour cet ID
    if paleo_texts:
       
        data[h2_id]["Caract�ristiques paleographiques"] = "".join(paleo_texts)
    if apparat_texts : 
      
            if apparat_texts != "".join(paleo_texts):
              if any(word in apparat_texts for word in["Texte","texte","L.","ligne","Ligne","lignes","Lignes","page","lettres","mots","mot","lettre"] ) : 
                data[h2_id]["Apparat critique"] = apparat_texts
              

    

# Si aucun �l�ment <Inscription_avec_alin�a_5_pt> n'a �t� trouv�
if count_inscr == 0:
    print("Aucune inscription trouv�e dans le document.")



# Boucler sur tous les �l�ments <h2>

for h2 in root.iter('h2'):
    corpus_id = h2.get('id').zfill(3)  # Ensure <h2> tags have 'id' attributes
    print(corpus_id)
     

    inscription_count = 0
    carac_paleo_list = []
    apparat_critique_list = []
    text = ""
    capture_apparat = 0
    start_collecting = False
    current_section = None
    traduction = ""
    found_traduction = False
    collected_text = False  # Flag to ensure only the first NormalParagraphStyle is collected
    relevant_sequence_started = False
    last_relevant_tag = None
    collecting_text = False
    if corpus_id not in data:
        data[corpus_id] = {} 

    for i, child in enumerate(h2):
          # Commence la collecte des paragraphes apr�s l'inscription ou traduction
        if child.tag == 'Titre_2':

            print(f"Titre: {child.text}")
            titre = uni_text(child.text) # Le texte du titre

            if titre:  # V�rifie que le texte n'est pas None
                titre_sans_numero = extraire_titre(titre)  # Extraire le texte apr�s le num�ro
                print(f"Titre : {titre_sans_numero}")
                data[corpus_id]['Titre'] = titre_sans_numero  # Stocke le titre dans le dictionnaire
            else : 
              print ("erreur")



            # V�rifier l'�l�ment suivant qui contient des informations sur la st�le (premier apr�s <Titre_2>)
            if i + 1 < len(h2):
                support_info = h2[i + 1]
                print(f"Informations sur la st�le (balise suivante): {support_info.text}")
                support_info_text = uni_text(support_info.text)
                data[corpus_id]['Information_support'] = support_info_text
                  # Chercher si un mot cl� du support est pr�sent dans la balise suivante
                for element in support_elements:
                    if element in support_info_text.lower():  # Comparaison insensible � la casse
                        print(f"�l�ment de support trouv� : {element}")
                        support = element
                        data[corpus_id]['Support'] = support
                        break  # Sortir de la boucle si un �l�ment est trouv

                for element in materiaux:
                    if element in support_info_text.lower():  # Comparaison insensible � la casse
                        print(f"�l�ment de support trouv� : {element}")
                        matiere = element
                        data[corpus_id]['Mati�re'] = matiere
                        break  # Sortir de la boucle si un �l�ment est tr

            # V�rifier l'�l�ment encore apr�s qui contient des informations sur la d�couverte (deuxi�me apr�s <Titre_2>)
            if i + 2 < len(h2):
                decouverte_info = h2[i + 2]
                decouverte_info_text=uni_text(decouverte_info.text)
                print(f"Informations sur la d�couverte (deux balises apr�s): {decouverte_info.text}")
                data[corpus_id]['Information_decouverte'] = decouverte_info_text
                # Chercher si un mot cl� du support est pr�sent dans la balise suivante
                date_decouverte = extract_date_with_words_before(decouverte, decouverte_info_text)

                decouverte_text_clean = normalize_text(decouverte_info_text.lower())
                print ("date",date_decouverte)
                if date_decouverte is not None:
                    print(f"Date trouv�e : {date_decouverte}")
                    data[corpus_id]['Date_decouverte'] = date_decouverte
                # Recherche dans le lieu de d�couverte
                texte_decouverte =chercher_avant_et_apres (decouverte_text_clean, conservation, decouverte)

                # Recherche dans le lieu de d�couverte
                for element in lieu_decouverte:
                    if element.lower() in decouverte_text_clean:  # Comparaison insensible � la casse
                        print(f"�l�ment de lieu de d�couverte trouv� : {element}")
                        lieu_trouve = element
                        data[corpus_id]['Lieu_decouverte'] = lieu_trouve

                        break
                    elif any(mot in decouverte_text_clean for mot in inconnu):
                        lieu_trouve = "ind�termin�"
                        print(f"�l�ment de lieu de d�couverte trouv� : {lieu_trouve}")
                        data[corpus_id]['Lieu_decouverte'] = lieu_trouve
                        break



                # Recherche dans le secteur de d�couverte
                for secteur, termes in secteur_decouverte_dict.items():
                      # Si un terme est trouv� dans le texte, retourner la cl� (secteur correspondant)
                    if any(terme in  decouverte_text_clean for terme in termes):

                          print(f"Secteur de d�couverte trouv� : {secteur}")
                          secteur_trouve = secteur
                          data[corpus_id]['Secteur_decouverte'] = secteur_trouve
                          break

                # Supposons que chercher_apres_mots renvoie un texte en minuscule
                texte_conserv = chercher_apres_mots(decouverte_text_clean, conservation)
                if texte_conserv is not None:
                    print(f"Texte conserv� : '{texte_conserv}'")  # Affiche le texte pour le d�bogage
                    data[corpus_id]['Texte_sur_la_conservation'] = texte_conserv
                    lieu_conserv = None  # Initialiser lieu_conserv
                    ville_conserv = None  # Initialiser ville_conserv

                    # Recherche dans les lieux de conservation
                    for element in lieu_conservation:
                        if element.lower() in texte_conserv:  # Comparaison insensible � la casse
                            print(f"�l�ment de lieu de conservation trouv� : {element}")
                            lieu_conserv = element
                            data[corpus_id]['Lieu_de_conservation'] = lieu_conserv
                            break  # On arr�te la recherche d�s qu'on trouve une correspondance

                    # Recherche dans le secteur de d�couverte
                    for secteur, termes in ville_conservation_dict.items():
                          # Si un terme est trouv� dans le texte, retourner la cl� (secteur correspondant)
                        if any(terme.lower() in  texte_conserv.lower() for terme in termes):

                              print(f"Secteur de d�couverte trouv� : {secteur}")
                              ville_conserv = secteur
                              data[corpus_id]['Ville_de_conservation'] = ville_conserv
                              break

                    # V�rification de l'inconnu dans le texte
                    if any(mot in texte_conserv for mot in inconnu):
                        lieu_conserv = "inconnu"
                        data[corpus_id]['Lieu_de_conservation'] = lieu_conserv
                        print(f"�l�ment de lieu de conservation trouv� : {ville_conserv}")

                    # D�bogage final : afficher le r�sultat de lieu_conserv
                    if lieu_conserv:
                        print(f"R�sultat final : lieu de conservation - {ville_conserv}")
                    else:
                        print("Aucune ville de conservation trouv�e dans le texte donn�.")








            # Si tu veux aller encore plus loin dans la structure
            result = []
            result = result.clear()
            if i + 3 < len(h2):

                dimensions_info = h2[i + 3]
                dimensions_info_text = uni_text(dimensions_info.text)

                print(f"Dimensions (trois balises apr�s): {dimensions_info_text.lower()}")
                dimensions = []

                result = extraire_dimensions(dimensions_info_text, "dimensions", [])
                print(result)
                if result is not None and len(result) > 0:  # Check if result is not None and has elements
                  data[corpus_id]["dimensions objet"] = {}
                  if result[0] is not None:
                      hauteur = result[0]
                      print(f"Hauteur : {hauteur} cm")
                      data[corpus_id]["dimensions objet"]['Hauteur'] = hauteur
                  if result[2] is not None:
                      largeur = result[2]
                      print(f" : {largeur} cm")
                      data[corpus_id]["dimensions objet"]['Largeur'] = largeur

                      
                  if result[3] is not None:
                      profondeur = result[3]
                      data[corpus_id]["dimensions objet"]['Profondeur'] = profondeur

                      print(f"Profondeur : {profondeur} cm {i}")





            if i +  4 < len(h2):
                #if child.tag == "Apparat_critique":
                  texte_epigraphique = h2[i + 4]
                  texte_epigraphique_text = uni_text(texte_epigraphique.text)
                  print(f"Texte de l'epigraphique : {texte_epigraphique_text}")
                  data[corpus_id]['Texte_epigraphique'] = texte_epigraphique_text
                  epigraphique_text_clean = normalize_text(texte_epigraphique_text.lower())
                  dimensions = []
                  result = extraire_dimensions (texte_epigraphique_text, "epi", dimensions)
                  print (f"�pigraphique{ result}")
                  if result is not None and len(result) > 0:  # Check if result is not None and has elements
                    data[corpus_id]["dimensions_epigraphique"] = {}
                    if result[0] is not None:
                        hauteur = result[0]
                        print(f"Hauteur : {hauteur} cm")
                        data[corpus_id]["dimensions_epigraphique"]['Hauteur'] = result[0]
                    if result[1] is not None:
                        hdl = result[1]
                        print(f"hdl : {hdl} cm")
                        data[corpus_id]["dimensions_epigraphique"]['Hdl'] = result[1]
                    if result[3] is not None:
                        profondeur = result[3]
                        print(f"Profondeur : {profondeur} cm")
                        data[corpus_id]["dimensions_epigraphique"]['Profondeur'] = result[3]



        if (child.tag == 'Inscription_avec_alin�a_5_pt' or child.tag == "Apparat_critique_tabulations_9pt"):
          if inscription_count == 0:
              print(f"Premi�re inscription : {child.text}")
              inscription = uni_text(child.text)
              data[corpus_id]['Inscription'] = inscription
              inscription_count += 1
          elif inscription_count == 1:
              print(f"Deuxi�me inscription : {child.text}")
              developpe = uni_text(child.text)
              data[corpus_id]['D�veloppement'] = developpe
              inscription_count += 1
            # Conditions pour inscription et traduction
        # Check for traduction tag
        if child.tag == "Inscription_traduction_italique":
            traduction = uni_text(child.text)
            data[corpus_id]['traduction'] = traduction
            found_traduction = True
            collecting_text = True  # Start collecting after traduction
            print(f"traduction : {traduction}")


        # Start tracking relevant sequence
        elif child.tag in ['Apparat_critique_tabulations_9pt', 'Inscription_avec_alin�a_5_pt']:
            relevant_sequence_started = True
            last_relevant_tag = child.tag
            collecting_text = True  # Start collecting after these tags

        # Track relevant Apparat_critique if in sequence
        elif child.tag == 'Apparat_critique' and relevant_sequence_started:
            last_relevant_tag = child.tag

        # Accumulate text from NormalParagraphStyle after traduction or last relevant tag
        elif child.tag == 'NormalParagraphStyle' and collecting_text:
            if child.text:
                texte_norm = uni_text(child.text)
                if re.search(r'([Tt]raductions?\s?)', child.text) is None:

                  text += child.text.strip() + " "  # Accumulate text
                  print(f"Collected Text: {child.text.strip()}")

        # Stop collecting if a non-relevant tag is encountered
        elif collecting_text and child.tag not in ['NormalParagraphStyle']:
            collecting_text = False

        # Capture les <Apparat_critique>
        if capture_apparat == 0 and child.tag == 'Apparat_critique':
          capture_apparat = 1




        elif capture_apparat == 1  and child.tag == 'Apparat_critique':
          data[corpus_id]['Lemme'] = uni_text(child.text)
          print(f"Lemme : {uni_text(child.text)}")
          capture_apparat = 2

        if child.tag=="Initiales_auteurs_entre_crochets":

          auteur = uni_text(child.text)
          print (auteur)
            # Extraire les initiales entre crochets et supprimer les espaces
          initials = re.findall(r'\[(.*?)\]', auteur)[0].strip()
          print (initials)

          # S�parer les initiales par des virgules ou des points-virgules
          initials_list = re.split(r'[,;]', initials)
          print (initials_list)

          # Rechercher chaque initiale dans le dictionnaire et construire la liste des noms
          auteur_names = []
          for initial in initials_list:
            initial = uni_text(initial.strip())
            if initial in auteurs:
              auteur_names.append(auteurs[initial])
              print (f"Auteur trouv� : {auteurs[initial]}")
            elif auteur_names:
              for initial in initials_list:
                print (f"auteur pas trouv� !!!! {initial}")
            else :
              print (auteur)
          if auteur_names is not None :
            data[corpus_id]['Auteur'] = auteur_names


    # Call the function once the desired text has been accumulated
    if text:

        result = recherche_date_icone(text)

        print(result)
        if result[0]:
            analyse_txt = result[0]
            data[corpus_id]['Analyse'] = analyse_txt
            print(f"Analyse : {analyse_txt}")
        if result[1]:
            iconographie = result[1]

            iconographie = uni_text(iconographie)
            iconographie = iconographie.replace('Iconographie de la niche :', '')
            iconographie = iconographie.replace('Iconographie de la niche:', '')
            print(f"Iconographie : {iconographie}")
            data[corpus_id]['Iconographie'] = iconographie
        if result[2]:
            datation = result[2]
            datation = uni_text(datation)
            datation = datation.replace('Datation :', '')
            datation = datation.replace('Datation:', '')
            print(f"Datation : {datation}")
            data[corpus_id]['Datation'] = datation

            print (result)



for h2_id in data:
    # V�rifier si "Apparat critique" et "Lemme" existent et sont identiques
    if "Apparat critique" in data[h2_id] and data[h2_id].get("Apparat critique") == data[h2_id].get("Lemme"):
        # Supprimer "Apparat critique" si les valeurs sont identiques
        del data[h2_id]["Apparat critique"]
    
    elif "Analyse" in data[h2_id]:
      if "Apparat critique" in data[h2_id] and data[h2_id].get("Apparat critique") in data[h2_id].get("Analyse", ""):
          del data[h2_id]["Apparat critique"]


# Enregistrement dans un fichier JSON
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)









