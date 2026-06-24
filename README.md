# disertatie_monitorizare_culturi_agricole
Realizarea practica si testarea unui sistem cu functia de a preleva si analiza imagini pentru stabilirea gradului de crestere a unor culturi agricole. Sistemul dezvoltat implementeaza un nod senzor inteligent bazat pe placa de dezvoltare Arduino Nicla Vision cu camera foto integrata.
Sistemul a fost antrenat in Edge Impulse iar implementarea finala ruleaza in OpenMV pentru placa Arduino Nicla Vision.
Setul de date a fost obtinut din urmatoarele surse:
  - https://www.kaggle.com/datasets/shubham2703/five-crop-diseases-dataset?resource=download
  - https://www.kaggle.com/datasets/sarfarazkhanmphil/wheat-weed-field-image-dataset?utm_source=chatgpt.com
  - https://www.kaggle.com/datasets/matthewmasters/global-wheat-head-dataset-manually-refined
  - https://www.kaggle.com/datasets/khanaamer/wheat-leaf-disease-dataset?resource=download

Foldeurul intitulat arduino contine fisierele necesare pentru incarcarea firmware‑ului pe placa Nicla Vision.

In foldrul monitorizare se afla scripturile python prin care se realizeaza comunicarea seriala cu dashbord-ul, orchestratorul gestionează automat toate modulele necesare:
  - python orchestrator.py - pentru comunicare seriala
  - python orchestrator.py --no-sim - pentru simularea cu rezultatele din simulated_results.txt

Pentru testarea comunicatiei seriale se apeleaza reciever.py din terminal

In folderul demo se pot gasi atat un demonstrativ al funcționării sistemului cat si câteva imagini utilizabile pentru testare
