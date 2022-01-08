import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from chromedriver_py import binary_path

url1 = "https://digitalcloud.training/login"
url2 = "https://digitalcloud.training/courses/exam-simulator-for-aws-cloud-practitioner/exams/exam-simulation-for-aws-cloud-practitioner"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
#options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=binary_path, options=options)

driver.get(url1)
lgn = driver.find_element_by_id('user_login')
pswd = driver.find_element_by_id('user_pass')
btn = driver.find_element_by_id('wp-submit')
lgn.clear()
lgn.send_keys(str('fnardifilho@gmail.com'))
pswd.clear()
pswd.send_keys(str('1ncLuF4jeuW(Oj$b'))
btn.click()
time.sleep(3)
driver.get(url2)
start = driver.find_element_by_name('startQuiz')
time.sleep(7)
start.click()
time.sleep(7)
summary = driver.find_element_by_name('quizSummary')
summary.click()
time.sleep(3)
end = driver.find_element_by_name('endQuizSummary')
end.click()
time.sleep(12)

page = driver.page_source
soup_lxml = BeautifulSoup(page, 'lxml')
driver.quit()

wpProQuiz_question_text = soup_lxml.find_all(class_='wpProQuiz_question_text')
wpProQuiz_questionList = soup_lxml.find_all(class_='wpProQuiz_questionList')
wpProQuiz_response = soup_lxml.find_all(class_='wpProQuiz_response')
wpProQuiz_correct = soup_lxml.find_all(class_='wpProQuiz_correct')

document = '\\begin{enumerate}\n'
answer_key = '\\begin{enumerate}\n'
perguntas = [(e.text).strip() for e in wpProQuiz_question_text]
alternativas = []
alt = []
respostas_1 = []
respostas_2 = []
rsp_1 = []
rsp_2 = []

for i in range(len(wpProQuiz_questionList)):
    document += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\t\\begin{itemize}\n"
    alt_raw = wpProQuiz_questionList[i].find_all('label')

    for j in range(len(alt_raw)):
        a = (alt_raw[j].text).strip()
        alt.append(a)
        document += "\t\t\\item " + a + "\n"
    alternativas.append(alt)
    document += "\t\\end{itemize}\n\n"
    alt = []

    answer_key += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\n"
    rsp_raw1 = wpProQuiz_correct[i].find_all('p')
    rsp_raw2 = wpProQuiz_correct[i].find_all('li')

    r1 = (rsp_raw1[0].text).strip()    
    rsp_1.append(r1)
    answer_key += "\t" + r1 + "\n"
    respostas_1.append(rsp_1)
    rsp_1 = []
    
    if (rsp_raw2):
        answer_key += "\t\\begin{enumerate}\n"
        for k in range(len(rsp_raw2)):
            r2 = (rsp_raw2[k].text).strip()
            rsp_2.append(r2)
            answer_key += "\t\t\\item " + r2 + "\n"      
        answer_key += "\t\\end{enumerate}\n"
        respostas_2.append(rsp_2)
        rsp_2 = []
    else:
        respostas_2.append('')

document += "\\end{enumerate}"
answer_key += "\\end{enumerate}"

prova = bytes(document, 'utf-8').decode('utf-8', 'ignore')
gabarito = bytes(answer_key, 'utf-8').decode('utf-8', 'ignore')

indices_perguntas = []
possiveis_respostas = []
respostas_corretas = []
possiveis_explicacoes = []
explicacoes_corretas = []

lista_perguntas = soup_lxml.find_all('ul')
lista = []

for a in range(len(lista_perguntas)): 
    if len(lista_perguntas[a].attrs) == 3:
        indices_perguntas.append(lista_perguntas[a].attrs['data-question_id'])
        possiveis_respostas.append(lista_perguntas[a].find_all('li', class_='wpProQuiz_answerCorrectIncomplete'))

for i in range(len(indices_perguntas)): 
    for j in range(len(possiveis_respostas[i])):
        lista.append(possiveis_respostas[i][j].text.strip().replace("\n","").replace("  "," ")[3:])
    respostas_corretas.append(lista)
    lista = []

wpProQuiz_question_text = soup_lxml.find_all(class_='wpProQuiz_question_text')
perguntas = [(e.text).strip() for e in wpProQuiz_question_text]

gabarito_resumido = ""
gabarito_resumido += '\\begin{enumerate}\n'

for i in range(len(respostas_corretas)):
    gabarito_resumido += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\n"
    gabarito_resumido += "\t\\begin{itemize}\n"
    for j in range(len(respostas_corretas[i])):
        gabarito_resumido += "\t\item " + str(respostas_corretas[i][j]) + "\n"
    gabarito_resumido += "\\end{itemize}"
    gabarito_resumido += "\n\n"

gabarito_resumido += '\\end{enumerate}\n'

for b in range(len(wpProQuiz_response)):
    possiveis_explicacoes.append(wpProQuiz_response[b].find_all('li'))
    for c in range(len(possiveis_explicacoes[b])):
        lista.append(possiveis_explicacoes[b][c].text.strip().replace('’', '\''))
    explicacoes_corretas.append(lista)
    lista = []

gabarito_completo = ""
gabarito_completo += '\\begin{enumerate}\n'

for i in range(len(respostas_corretas)):
    gabarito_completo += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\n"
    gabarito_completo += "\t\\begin{itemize}\n"
    for j in range(len(respostas_corretas[i])):
        gabarito_completo += "\t\item \\textbf{" + str(respostas_corretas[i][j]) + "}\n"
    for k in range(len(explicacoes_corretas[i])):
        link = str(explicacoes_corretas[i][k])
        if link[0:4] != 'http':
            gabarito_completo += "\t\item " + str(explicacoes_corretas[i][k]) + "\n"
    gabarito_completo += "\t\\end{itemize}\n"
    gabarito_completo += "\n\n"
gabarito_completo += '\\end{enumerate}\n'

gbrs = bytes(gabarito_resumido, 'utf-8').decode('utf-8', 'ignore')
gbcp = bytes(gabarito_completo, 'utf-8').decode('utf-8', 'ignore')

with open('f1.tex', 'w') as file:  
        file.write(prova)
    
with open('f2.tex', 'w') as file:  
    file.write(gbrs)

with open('f3.tex', 'w') as file:  
    file.write(gbcp)

os.system("pdflatex 1-questionario.tex")
os.system("pdflatex 2-gabarito.tex")
os.system("pdflatex 3-estudo.tex")
os.system("rm -rf f1.tex f2.tex f3.tex *.aux *.log *.fls *.fdb_* *.gz")